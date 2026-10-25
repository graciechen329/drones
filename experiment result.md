10/25
# 實驗一（包含索書號）

列出該書脊的最高分候選書目與分數；若最高分並列，列出並列候選。token ≥ 10 時，門檻是分數必須嚴格大於 token 數的 40%；其他 token 數則依原程式門檻判定。

---

執行的 47 個書脊結果整理如下。符合門檻且最高分唯一的項目，程式已更新 Supabase；分數相同的項目不會更新。完整資料見 `output/book_match_results.json`。
### 符合標準，已更新 Supabase（17 筆）

| 書脊編號 | 匹配書目 | 分數 |
|---:|---|---:|
| 03 | American Writers & Their Works | 8 |
| 04 | The First Four Years | 7 |
| 09 | Beyond The Horizon | 9 |
| 10 | Farmer Boy | 4 |
| 13 | These Happy Golden Years | 8 |
| 14 | Beyond The Horizon | 2 |
| 18 | Beyond The Horizon | 9 |
| 20 | Little House in the Big Woods | 5 |
| 22 | The Slippery Slope | 2 |
| 23 | Anne of Ingleside | 4 |
| 25 | Farmer Boy | 7 |
| 26 | The First Four Years | 2 |
| 28 | These Happy Golden Years | 6 |
| 34 | The Life and Adventures of Santa Claus | 3 |
| 36 | Little House on the Prairie | 6 |
| 39 | American Writers & Their Works | 5 |
| 41 | Farmer Boy | 3 |

### 未達分數門檻（16 筆）

列出該書脊的最高分候選書目與分數；若最高分並列，列出並列候選。`token ≥ 10` 時，門檻是分數必須**嚴格大於 token 數的 40%**；其他 token 數則依原程式門檻判定。

| 書脊編號 | 最高分候選書目（分數） | 判定 |
|---:|---|---|
| 00 | Anne of Green Gables（8） | 29 tokens，需大於 11.6 |
| 01 | Anne of Windy Poplars、Anne's House of Dreams、Little House on the Prairie（各 3） | 10 tokens，需大於 4 |
| 07 | Anne of Avonilea、Rilla of Ingleside、The Vile Village（各 4） | 10 tokens，需大於 4 |
| 08 | The Life and Adventures of Santa Claus、The Wonderful Wizard of Oz（各 7） | 27 tokens，需大於 10.8 |
| 12 | Rilla of Ingleside（4） | 14 tokens，需大於 5.6 |
| 16 | Pinocchio, The Boy、The Austere Academy、The Bad Beginning（各 4） | 10 tokens，需大於 4 |
| 27 | Pinocchio, The Boy、The Austere Academy、The Carnivorous Carnival（各 4） | 10 tokens，需大於 4 |
| 30 | Good Books,Good Times！、O Jerusalem！、The Wonderful Wizard of Oz（各 2） | 7 tokens，需至少 3 |
| 32 | Beyond The Horizon、Farmer Boy、Good Books,Good Times！（各 1） | 3 tokens，需至少 2 |
| 33 | The Austere Academy、The Bad Beginning、The Carnivorous Carnival（各 4） | 10 tokens，需大於 4 |
| 38 | 顯示的候選各 0 分 | 0 tokens，未達門檻 |
| 42 | American Writers & Their Works（1） | 2 tokens，需至少 2 |
| 43 | 顯示的候選各 0 分 | 0 tokens，未達門檻 |
| 44 | 顯示的候選各 0 分 | 0 tokens，未達門檻 |
| 45 | The Bad Beginning（4） | 10 tokens，需大於 4 |
| 46 | Good Books,Good Times！（4） | 10 tokens，需大於 4 |

### 同分，無法判斷（14 筆）

| 書脊編號 | 同分候選書目 | 最高分 |
|---:|---|---:|
| 02 | Anne of Green Gables（兩筆書目紀錄） | 6 |
| 05 | Anne of Green Gables（兩筆書目紀錄） | 6 |
| 06 | Anne of Windy Poplars、Anne's House of Dreams、The Life and Adventures of Santa Claus | 4 |
| 11 | Anne of the Island、The Life and Adventures of Santa Claus | 5 |
| 15 | The Austere Academy、The Hostile Hospital | 5 |
| 17 | Pinocchio, The Boy、The Austere Academy、The Carnivorous Carnival | 4 |
| 19 | Dangerous Journey、Little House in the Big Woods | 3 |
| 21 | Pinocchio, The Boy、The Austere Academy、The Carnivorous Carnival | 4 |
| 24 | Anne of Avonilea、Dangerous Journey、My Mommy and Me | 3 |
| 29 | Beyond The Horizon、Lady Chatterie's Lover、The Life and Adventures of Santa Claus | 4 |
| 31 | The Wonderful Wizard of Oz（三筆書目紀錄） | 4 |
| 35 | Little House in the Big Woods、Pinocchio, The Boy | 4 |
| 37 | The Wonderful Wizard of Oz（三筆書目紀錄） | 5 |
| 40 | Anne of Ingleside、Little House in the Big Woods、The Life and Adventures of Santa Claus | 4 |








## 問題
同一區域的書籍索書號相似，數字相似容易誤判分數，導致許多書目同分無法判斷

## 改進辦法
刪掉所有索書號與年份(有數字的欄位)
只比對作者與書名


# 實驗二


依照目前的判斷邏輯整理最新的 `比對結果`。判定門檻為：OCR token 數 ≥10 時，分數須嚴格大於 token 數的 40%；6–9 個 token 至少 3 分；5 個或更少至少 2 分。符合門檻但最高分並列者列為「同分無法判斷」。

### 符合標準，已更新 Supabase（17 筆）

| 書脊編號 | 匹配書目 | 分數 |
|---:|---|---:|
| 04 | The First Four Years | 5 |
| 09 | Beyond The Horizon | 7 |
| 10 | Farmer Boy | 3 |
| 13 | These Happy Golden Years | 6 |
| 18 | Beyond The Horizon | 7 |
| 19 | Dangerous Journey | 3 |
| 20 | Little House in the Big Woods | 5 |
| 22 | The Slippery Slope | 2 |
| 23 | Anne of Ingleside | 3 |
| 25 | Farmer Boy | 5 |
| 26 | The First Four Years | 2 |
| 28 | These Happy Golden Years | 4 |
| 34 | The Life and Adventures of Santa Claus | 2 |
| 36 | Little House on the Prairie | 4 |
| 39 | American Writers & Their Works | 5 |
| 40 | Little House in the Big Woods | 3 |
| 41 | Farmer Boy | 2 |

### 未達分數門檻（23 筆）

分數為最高候選分數；同分的最高候選一併列出。

| 書脊編號 | 最高分候選書目 | 分數 |
|---:|---|---:|
| 00 | Anne of Green Gables | 6 |
| 01 | Anne of Windy Poplars、Anne's House of Dreams、Little House on the Prairie | 各 3 |
| 03 | American Writers & Their Works、Best-Loved Nursery Rhymes、Little House in the Big Woods | 各 5 |
| 07 | The Vile Village | 3 |
| 08 | The Life and Adventures of Santa Claus、The Wonderful Wizard of Oz | 各 6 |
| 12 | Little House in the Big Woods、Rilla of Ingleside、The First Four Years | 各 3 |
| 14 | 多筆候選書目 | 0 |
| 15 | The Austere Academy、The Hostile Hospital | 各 3 |
| 16 | The Bad Beginning | 3 |
| 17 | Anne of Avonilea、Anne of the Island、Pinocchio, The Boy | 各 2 |
| 21 | Anne of Avonilea、Anne of the Island、Pinocchio, The Boy | 各 2 |
| 24 | Anne of Avonilea、Dangerous Journey | 各 2 |
| 27 | Anne of Avonilea、Anne of the Island、Pinocchio, The Boy | 各 2 |
| 29 | American Writers & Their Works、Anne of Avonilea、Anne of the Island | 各 2 |
| 30 | Good Books,Good Times！、O Jerusalem！ | 各 1 |
| 32 | 多筆候選書目 | 0 |
| 33 | The Austere Academy、The Bad Beginning、The Carnivorous Carnival | 各 3 |
| 38 | 多筆候選書目 | 0 |
| 42 | American Writers & Their Works | 1 |
| 43 | 多筆候選書目 | 0 |
| 44 | 多筆候選書目 | 0 |
| 45 | Pinocchio, The Boy、The Bad Beginning | 各 3 |
| 46 | Good Books,Good Times！ | 4 |

### 同分，達門檻但無法判斷（7 筆）

| 書脊編號 | 同分候選書目 | 分數 |
|---:|---|---:|
| 02 | Anne of Green Gables（兩筆不同館藏紀錄） | 4 |
| 05 | Anne of Green Gables（兩筆不同館藏紀錄） | 5 |
| 06 | Anne of Windy Poplars、Anne's House of Dreams、My Mommy and Me | 各 3 |
| 11 | Anne of the Island、The Life and Adventures of Santa Claus | 各 4 |
| 31 | Little House in the Big Woods、Little House on the Prairie、The Wonderful Wizard of Oz | 各 3 |
| 35 | Little House in the Big Woods、Pinocchio, The Boy | 各 4 |
| 37 | The Wonderful Wizard of Oz（三筆不同館藏紀錄） | 各 4 |

共處理 **47 個書脊**：17 筆已更新、23 筆未達門檻、7 筆達門檻但最高分並列。

# 結論: 已更新者不變; 未達門檻者增加; 同分者減少
