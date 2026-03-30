# 驗證模式（Verify Patterns）

不同類型的產出需要不同的驗證方式。以下是各類型的標準驗證流程。

---

## Server / API 類

```bash
# 1. 背景啟動
dotnet run &  # 或 node server.js &（run_in_background: true）

# 2. 等待啟動（根據 app 大小調整）
sleep 3-6

# 3. 發送測試請求
curl -s -w "\nHTTP_CODE:%{http_code}" -X POST http://localhost:PORT/ \
  -d '{"test":"data"}' -H "Content-Type: application/json"

# 4. 程式化斷言（不只看 200，要檢查 body）
# 回應包含預期欄位？status code 正確？latency 合理？

# 5. 清理
taskkill //IM AppName.exe //F  # Windows
# kill %1  # Linux/Mac
```

**PASS 條件**：HTTP 200 + 回應 body 包含預期資料
**FAIL 條件**：非 200、timeout、回應格式錯誤

---

## CLI 工具類

```bash
# 直接執行並檢查輸出
my-cli --input test.txt --output result.txt

# 檢查 exit code
echo $?  # 應該是 0

# 檢查輸出檔案
cat result.txt  # 內容符合預期？
```

**PASS 條件**：exit code 0 + 輸出內容正確
**FAIL 條件**：非零 exit code、輸出為空、內容錯誤

---

## UI / Frontend 類

```bash
# 啟動 dev server
npm run dev &  # run_in_background: true

# 等待啟動
sleep 5

# 檢查 server 在跑
curl -s -o /dev/null -w "%{http_code}" http://localhost:PORT/
# 應該回 200

# 如果有瀏覽器工具（Playwright、claude-in-chrome）：
# 導航到頁面 → 截圖 → 確認 UI 元素存在
```

**PASS 條件**：頁面載入 + 關鍵 UI 元素存在
**FAIL 條件**：白屏、console error、元素缺失

---

## 程式庫 / 函式類

```bash
# 寫一個最小測試腳本
py -c "
from my_module import my_function
result = my_function('test_input')
assert result == 'expected_output', f'Got {result}'
print('PASS')
"
```

**PASS 條件**：assert 通過 + 輸出 PASS
**FAIL 條件**：AssertionError、ImportError、任何 exception

---

## 設定檔 / 配置類

```bash
# 檢查 JSON 語法
py -c "import json; json.load(open('config.json'))"

# 檢查關鍵欄位存在
py -c "
import json
cfg = json.load(open('config.json'))
assert 'required_field' in cfg, 'Missing required_field'
print('PASS')
"
```

---

## 通用原則

1. **永遠用外部工具驗證**，不是「我看了 code 覺得對」
2. **程式化斷言優先**：寫一個會 PASS 或 FAIL 的腳本，不是人眼判斷
3. **驗證完清理**：kill 背景 process、刪暫存檔
4. **記錄驗證結果**：至少用 TaskUpdate 記錄 PASS/FAIL
