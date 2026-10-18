# drones
## 紀錄
- 2026/05/23 分配工作 決定讓無人機當圖書館管理員解決人力不足問題 先製作無人機模型 再寫程式
- 2026/05/30 3D模型繪畫 3D列印出來  
- 2026/06/06 前天在學校圖書館拍攝了書櫃的照片 測試 初步使用AI建構的程式碼測試，但OCR出來的效果無法辨識，程式待改善與修正

---
# 書脊辨識與館藏狀態更新

`src/book_checker.py` 將書脊偵測、ROI 裁切、四方向 OCR、書目比對與 Supabase 更新整合為單一流程。

## 安裝依賴

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 設定連線

設定 Roboflow API key 與 Supabase 專案資訊。Supabase key 必須具有 `books` 資料表的 SELECT 與 UPDATE 權限，並遵守資料表的 RLS policy；不要在程式碼中放入 service-role key。

```bash
export ROBOFLOW_API_KEY="your-roboflow-api-key"
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-supabase-anon-or-publishable-key"
```

## 執行

```bash
python src/book_checker.py \
  --image path/to/bookshelf.jpg \
  --output-dir output
```

可選參數包括 `--supabase-table`（預設 `books`）、`--books-csv`（預設 `bookslist.csv`）、`--workspace`、`--project`、`--version`、`--confidence`、`--overlap` 與 `--margin`。

## 流程與比對規則

1. 從 Supabase `books` 資料表分頁讀取書目資料，並匯出 `bookslist.csv`。欄位為 `id, original_id, title, author_publisher, publication_year, category, location, call_number, avaliable, last_check`。
2. 使用 Roboflow 偵測書本，裁切每本書脊 ROI，並以 EasyOCR 對原圖及順、逆時針旋轉 90 度的影像辨識英文字母與數字。
3. 使用 `book_match.py` 的 token 編輯距離／局部比對方法，計算每筆 OCR 結果與書目的分數。
4. OCR token 數量至少 10 時，分數必須大於 token 數的 40%；6 至 9 個 token 時分數至少為 3；5 個或更少 token 時分數至少為 2。符合門檻且最高分唯一時，將該書的 `avaliable` 設為 `true`，並更新 `last_check` 為 UTC 時間。低於門檻或最高分並列時不更新。

## 輸出

- `bookslist.csv`：本次由 Supabase 讀取的書目快照。
- `output/book_NNN.png`：各書脊的 ROI 圖片。
- `output/ocr_results.json`：OCR 文字與辨識細節。
- `output/book_match_results.json`：前三名候選書目、比對分數與更新狀態。

資料庫使用 Supabase REST API 更新；如果 RLS 或權限設定阻止讀取／更新，程式會直接顯示錯誤，不會將失敗視為更新成功。

## TLS 憑證錯誤

Supabase HTTPS 連線會使用 `certifi` 根憑證並驗證伺服器憑證。若網路環境使用自訂 CA（例如公司代理伺服器），可在執行前將 CA 憑證檔設為 `SSL_CERT_FILE`，必要時也可用 `SSL_CERT_DIR` 指定憑證目錄。請勿停用 TLS 憑證驗證。
