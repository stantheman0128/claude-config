"""Quota Pacer 用量讀取器：印當前 5h/weekly/scoped 用量與資料新鮮度。

檔案缺或過舊會先自拉官方 oauth/usage endpoint（60s 冷卻），拉不到才報 MISSING。

用法：
  py read_usage.py          人看的一行
  py read_usage.py --json   給 skill 記基準用的 JSON
"""
import json
import sys

import pace_core as pc

def fmt_reset(resets_at, now):
    if not resets_at:
        return "?"
    d = int(resets_at) - int(now)
    if d <= 0:
        return "now"
    return f"{d // 3600}h{(d % 3600) // 60:02d}m"

def main():
    try:
        u = pc.load_usage(refresh_if_stale=True)
    except (OSError, ValueError):
        print(f"MISSING\tusage-state.json 讀不到、自動刷新也失敗（{pc.USAGE_STATE}）。"
              f"確認 ~/.claude/.credentials.json 存在且網路可達。", file=sys.stderr)
        sys.exit(3)

    h5 = u.get("five_hour", {}).get("pct")
    w = u.get("seven_day", {}).get("pct")
    scoped = {k: v.get("pct") for k, v in (u.get("scoped") or {}).items()}
    age = int(u.get("_age", 0))
    stale = age > pc.STALE

    if "--json" in sys.argv[1:]:
        print(json.dumps({"five_hour": h5, "seven_day": w, "scoped": scoped,
                          "age": age, "stale": stale}))
        return

    import time
    now = time.time()
    h5r = fmt_reset(u.get("five_hour", {}).get("resets_at"), now)
    wr = fmt_reset(u.get("seven_day", {}).get("resets_at"), now)
    sc = "".join(f"  |  {k} {v}%" for k, v in scoped.items())
    tag = f"  ⚠STALE({age}s)" if stale else ""
    print(f"5h {h5}% (reset {h5r})  |  weekly {w}% (reset {wr}){sc}  |  {age}s ago{tag}")

if __name__ == "__main__":
    main()
