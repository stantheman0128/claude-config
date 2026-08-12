"""Quota Pacer 核心：讀用量、讀 active 基準、算裁決。hook 與 eval CLI 共用。

兩條 guard，先到者觸發：
- 用量 guard：每條限制 session 起點記 U0，available=100-U0，正規化門檻。
- 時間 guard：從 started 起算 elapsed 分鐘，minutes 為上限；只靠牆鐘，不碰用量資料，
  所以在讀不到 usage 的環境（SDK / 桌面 App）照樣有效。

門檻與時間盒模型見 docs/specs/2026-07-18-quota-pacer-design.md。
EMERGENCY 是給 hook 的最後保險，低於 hard-stop，確保寫交接的 buffer 不會被 hook 擋掉。
"""
import json
import os
import time

def _f(env, default):
    try:
        return float(os.environ.get(env, default))
    except (TypeError, ValueError):
        return float(default)

def _num(x):
    """安全轉數字，壞值回 None（防 active.json 被寫壞時 float() 爆例外）。"""
    try:
        return float(x)
    except (TypeError, ValueError):
        return None

SOFT = _f("QP_SOFT_RATIO", 0.10)
HARD = _f("QP_HARD_RATIO", 0.05)
FLOOR = _f("QP_FLOOR_PP", 3)
GAP = _f("QP_NOTICE_GAP_PP", 1)
EMERGENCY = _f("QP_EMERGENCY_PP", 1)
STALE = _f("QP_STALE_SEC", 90)
GRACE_MIN = _f("QP_GRACE_MIN", 3)
NOTICE_MIN = _f("QP_NOTICE_MIN", 2)

USAGE_STATE = os.environ.get("QP_USAGE_STATE") or os.path.join(
    os.path.expanduser("~"), ".claude", "usage-state.json")
ACTIVE_FILE = os.environ.get("QP_ACTIVE_FILE") or os.path.join(
    os.path.expanduser("~"), ".claude", "quota-pacer", "active.json")
CRED_FILE = os.environ.get("QP_CRED_FILE") or os.path.join(
    os.path.expanduser("~"), ".claude", ".credentials.json")
USAGE_URL = os.environ.get("QP_USAGE_URL") or "https://api.anthropic.com/api/oauth/usage"
REFRESH_COOLDOWN = _f("QP_REFRESH_COOLDOWN_SEC", 60)
REFRESH_MARK = os.path.join(os.path.dirname(ACTIVE_FILE), ".refresh-attempt")

RANK = {"CONTINUE": 0, "WINDDOWN": 1, "HARDSTOP": 2, "EMERGENCY": 3}
LIMITS = {"5h": "five_hour", "weekly": "seven_day"}

def _read_usage_file():
    with open(USAGE_STATE, encoding="utf-8") as fh:
        d = json.load(fh)
    d["_age"] = time.time() - float(d.get("ts", 0))
    return d

def _iso_to_epoch(s):
    """ISO 8601（含時區）→ epoch 秒；壞值回 None。"""
    if not s:
        return None
    try:
        from datetime import datetime
        return int(datetime.fromisoformat(s).timestamp())
    except (TypeError, ValueError):
        return None

def _pct(v):
    n = _num(v)
    if n is None:
        return None
    return int(n) if float(n).is_integer() else round(n, 1)

def fetch_usage(timeout=10):
    """打官方 oauth/usage endpoint，轉成 usage-state.json 格式（含 scoped）。

    失敗 raise（OSError/ValueError），由 refresh_usage 統一吞。
    """
    import urllib.request  # 延遲載入：hook 路徑 import pace_core 時不揹網路模組
    with open(CRED_FILE, encoding="utf-8") as fh:
        cred = json.load(fh)
    oauth = cred.get("claudeAiOauth", cred)
    token = oauth.get("accessToken") or oauth.get("access_token")
    if not token:
        raise ValueError("credentials 裡沒有 OAuth access token")

    req = urllib.request.Request(USAGE_URL, headers={
        "Authorization": "Bearer " + token,
        "anthropic-beta": "oauth-2025-04-20",
        "User-Agent": "quota-pacer/0.2",
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = json.loads(resp.read().decode("utf-8"))

    out = {"ts": time.time(), "source": "oauth"}
    for key in ("five_hour", "seven_day"):
        blk = raw.get(key) or {}
        out[key] = {"pct": _pct(blk.get("utilization")),
                    "resets_at": _iso_to_epoch(blk.get("resets_at"))}
    scoped = {}
    for lim in raw.get("limits") or []:
        if lim.get("kind") != "weekly_scoped":
            continue
        model = ((lim.get("scope") or {}).get("model") or {})
        name = (model.get("display_name") or "scoped").strip().lower().replace(" ", "-")
        scoped[name] = {"pct": _pct(lim.get("percent")),
                        "resets_at": _iso_to_epoch(lim.get("resets_at"))}
    if scoped:
        out["scoped"] = scoped
    return out

def refresh_usage(force=False):
    """拉新用量寫 USAGE_STATE。成功回 dict、失敗/冷卻中回 None，絕不覆寫壞資料。"""
    if not force:
        try:
            if time.time() - os.path.getmtime(REFRESH_MARK) < REFRESH_COOLDOWN:
                return None
        except OSError:
            pass
    try:
        os.makedirs(os.path.dirname(REFRESH_MARK), exist_ok=True)
        with open(REFRESH_MARK, "w"):
            pass
    except OSError:
        pass
    try:
        data = fetch_usage()
    except Exception:
        return None
    tmp = USAGE_STATE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False)
        os.replace(tmp, USAGE_STATE)
    except OSError:
        return None
    data = dict(data)
    data["_age"] = 0.0
    return data

def load_usage(refresh_if_stale=False):
    """讀 usage state。refresh_if_stale=True 時，檔案缺/過舊就先自拉一次再讀。

    hook 路徑請維持預設 False（PreToolUse 每次工具呼叫都跑，不能揹網路延遲）。
    """
    if not refresh_if_stale:
        return _read_usage_file()
    try:
        d = _read_usage_file()
    except (OSError, ValueError):
        d = None
    if d is None or d.get("_age", 0) > STALE:
        fresh = refresh_usage()
        if fresh is not None:
            return fresh
    if d is None:
        return _read_usage_file()  # 沒舊檔又刷不到 → 照舊 raise 給呼叫端
    return d

def load_active(path=ACTIVE_FILE):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)

def thresholds(u0):
    avail = max(0.0, 100.0 - u0)
    hs = max(HARD * avail, FLOOR)
    wd = max(SOFT * avail, hs + GAP)
    return wd, hs

def eval_limit(cur, u0):
    if cur is None or u0 is None:
        return "CONTINUE"
    rem = 100.0 - cur
    wd, hs = thresholds(u0)
    if rem <= EMERGENCY:
        return "EMERGENCY"
    if rem <= hs:
        return "HARDSTOP"
    if rem <= wd:
        return "WINDDOWN"
    return "CONTINUE"

def elapsed_min(started):
    n = _num(started)
    if not n or n <= 0:
        return 0.0
    return (time.time() - n) / 60.0

def eval_time(started, minutes):
    s, m = _num(started), _num(minutes)
    if not s or not m or s <= 0 or m <= 0:
        return "CONTINUE"
    e = (time.time() - s) / 60.0
    hard_at = max(0.0, m - GRACE_MIN)
    wind_at = max(0.0, hard_at - NOTICE_MIN)
    if e >= m:
        return "EMERGENCY"
    if e >= hard_at:
        return "HARDSTOP"
    if e >= wind_at:
        return "WINDDOWN"
    return "CONTINUE"

def evaluate(usage, active):
    """回 (verdict, trigger)。時間與用量兩條 guard 先到者。usage 可為 None（讀不到）。"""
    verdict, trigger = "CONTINUE", ""

    if _num(active.get("minutes")):
        v = eval_time(active.get("started"), active.get("minutes"))
        if RANK[v] > RANK[verdict]:
            verdict, trigger = v, "time"

    if usage is not None:
        mode = active.get("mode", "both")
        u0 = active.get("u0", {})
        names = ["weekly"] if mode == "5h-override" else ["5h", "weekly"]
        for name in names:
            key = LIMITS[name]
            cur = usage.get(key, {}).get("pct")
            v = eval_limit(cur, u0.get(key))
            if RANK[v] > RANK[verdict]:
                verdict, trigger = v, name

    return verdict, trigger
