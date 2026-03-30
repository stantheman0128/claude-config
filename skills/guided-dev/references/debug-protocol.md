# Debug Protocol（除錯步驟）

驗證失敗時，按照以下步驟系統化排查。不要亂猜亂改。

---

## Step 1: 分類問題

| 症狀 | 問題類型 | 跳到 |
|------|---------|------|
| `error` / `exception` 在 build 時 | 編譯錯誤 | Step 2 |
| App 啟動後立即 crash | Runtime crash | Step 3 |
| App 在跑但不回應請求 | Server 不回應 | Step 4 |
| 回應了但內容錯誤 | 邏輯錯誤 | Step 5 |
| 前幾次對但現在壞了 | 回歸問題 | Step 6 |

---

## Step 2: 編譯錯誤

```bash
# 讀完整 error message（不要只看第一行）
dotnet build 2>&1 | head -50

# 常見原因：
# - 缺少 import/using
# - 型別不匹配
# - 缺少套件（需要 npm install / dotnet add package）
```

**修復後**：重新 build，確認 0 errors 再進 Verify。

---

## Step 3: Runtime Crash

```bash
# 用 foreground 模式執行，看完整 stack trace
timeout 10 dotnet run 2>&1
# 或
timeout 10 node server.js 2>&1
```

**看什麼**：
- Exception 類型（NullReference? FileNotFound? PortInUse?）
- Stack trace 指向哪個檔案的哪一行
- 是啟動時 crash 還是收到請求才 crash

---

## Step 4: Server 不回應

依序檢查：

```bash
# 1. Process 在跑嗎？
tasklist | grep -i AppName
# 如果不在 → 回到 Step 3

# 2. Port 在聽嗎？
netstat -ano | grep PORT
# 如果沒有 → app 可能綁定了錯的 port

# 3. 能不能 ping 到？
curl -v http://localhost:PORT/
# 看 Connection refused vs timeout vs 其他

# 4. Windows 防火牆？
# 開發階段通常不是問題，但如果其他都正常就檢查這個

# 5. 是不是 modal dialog 在 blocking？（Windows GUI app）
# 改用非阻塞 UI 或檢查有沒有未處理的 dialog
```

---

## Step 5: 邏輯錯誤

```bash
# 1. 加 log 到關鍵位置
# 在可疑的函式入口和出口加 console.log / print

# 2. 重新啟動並觸發操作
# 3. 讀 log 輸出，追蹤資料流

# 4. 找到「預期值 vs 實際值」的分歧點
# 那個分歧點就是 bug 所在
```

**原則**：不要猜。用 log 追蹤到確切的分歧點再修。

---

## Step 6: 回歸問題

```bash
# 1. 確認是哪個 Slice 的改動造成的
git diff HEAD~1  # 看最近改了什麼

# 2. 重新跑之前 Slice 的驗證
# 如果之前的 Slice 壞了 → 這次改動有副作用

# 3. 考慮 revert 最近的改動，用更小的步驟重做
```

---

## 何時放棄當前方案

以下情況代表需要 **re-plan**，不是繼續 fix：

- 同一個問題 fix 了 3 次還是失敗
- Fix 的改動越來越大，已經超出原本 Slice 的範圍
- 發現原始設計有根本問題（例如選錯了框架、用錯了 API）
- 修一個 bug 會引入另一個 bug（循環修復）

**Re-plan 時**：告訴使用者「這條路走不通，原因是 X。我打算改成 Y，可以嗎？」
