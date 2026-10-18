# step 1 取書目來源
# 書目來源：bookslist.csv 
# 讀出所有欄位的文字id欄位除外，合併為單一字串，再把這個字串是用空格與非字元符號（:,-/）分割成小token，將所有token放入list 中，並將所有書本的 token list 存入一個 list 中。
# 再將所有書本的 token list 存入一個 list 中

# step 2 取辨識結果
# 辨識結果來源：output_4dirs_combine/ocr_result.json
# 讀出所有辨識結果的文字(text field , not in ocr_details)，把這個字串是用空格與非字元符號（:,-）分割成小token，將所有token放入list 中，並將所有辨識結果的 token list 存入一個 list 中。

# step 3 計算相似度
# 對每筆 OCR 辨識結果，逐一與所有書目的 token 清單進行比對。
# 比較兩個 token 時，先計算 Levenshtein 編輯距離，再以
# 1 - 編輯距離 / 兩個 token 中較長者的字元數，換算出 0.0 到 1.0 的相似度。
# 對每個書目 token，找出與所有 OCR token 比對後的最高相似度；
# 若最高相似度大於 0.5，便將該書目的匹配分數加 1。
# 將所有書目的匹配分數由高至低排序，取分數最高的前 3 筆作為候選書目。

# step 4 輸出結果

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import List


def tokenize(text: str) -> List[str]:
	"""將文字依空白與常見標點切分，並移除空字串及單字元 token。"""
	if not text:
		return []
	# split on whitespace and common punctuation, keep alphanumerics
	parts = re.split(r"[\s:\-\/,]+", text)
	tokens = [p.strip() for p in parts if p and len(p.strip()) > 1]
	return tokens


def levenshtein(a: str, b: str) -> int:
	"""計算兩個字串之間的 Levenshtein 編輯距離。

	編輯距離是將一個字串轉換成另一個字串所需的最少插入、刪除或替換次數。
	"""
	# classic DP
	if a == b:
		return 0
	if len(a) == 0:
		return len(b)
	if len(b) == 0:
		return len(a)
	prev = list(range(len(b) + 1))
	for i, ca in enumerate(a, start=1):
		cur = [i] + [0] * len(b)
		for j, cb in enumerate(b, start=1):
			cost = 0 if ca == cb else 1
			cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
		prev = cur
	return prev[-1]


def similarity_token(t1: str, t2: str) -> float:
	"""依編輯距離計算兩個 token 的相似度，回傳介於 0.0 到 1.0 的分數。"""
	if not t1 or not t2:
		return 0.0
	# ld 可以想成錯誤個數
	ld = levenshtein(t1, t2)
	# 字串長
	m = max(len(t1), len(t2))
	if m == 0:
		return 0.0
	# 1 - (編輯距離 / 較長字串長度) = 1-錯誤率 = 正確率/相似度
	return 1.0 - (ld / m)


def load_books(csv_path: Path) -> List[dict]:
	"""讀取書目 CSV，排除欄位名稱以 id 結尾的欄位後建立 token 清單。

	每筆回傳資料包含原始資料列（row）及其文字 token（tokens）。
	"""
	books = []
	with csv_path.open("r", encoding="utf-8", newline="") as fh:
		reader = csv.DictReader(fh)
		for row in reader:
			# combine all fields except ones that look like ids
			parts = [v.lower() for k, v in row.items() if v and not k.lower().endswith("id")]
			text = " ".join(parts)
			tokens = tokenize(text)
			books.append({"row": row, "tokens": tokens})
	return books


def load_ocr_results(json_path: Path) -> List[dict]:
	"""讀取 OCR JSON，取出辨識文字並建立 token 清單。

	支援 JSON 頂層為清單，或以 ocr_results 為鍵的字典；
	每筆回傳資料包含原始辨識結果（entry）及其文字 token（tokens）。
	"""
	data = json.loads(json_path.read_text(encoding="utf-8"))
	items = []
	# support either list or dict with key
	entries = data if isinstance(data, list) else data.get("ocr_results", [])
	for entry in entries:
		text = entry.get("text") or ""
		tokens = tokenize(text.lower())
		items.append({"entry": entry, "tokens": tokens})
	return items


def similarity_token2(t1: str, t2: str) -> float:
	"""計算兩個 token 的相似度，回傳介於 0.0 到 1.0 的分數。

	以較短 token 去尋找較長 token 中的子字串（和較短字串字數相同）所得到最高的相似度，
	
	ex. t1:grean 
	    t2:anneofgreengables <-- t2 中間要取出比對的字串應為 green
	             ^^^^^
		計算 grean 與 green 的相似度，得到 0.8
	"""
	if not t1 or not t2 or len(t1) < 2 or len(t2) < 2:
		return 0.0

	long, short = (t1, t2) if len(t1) >= len(t2) else (t2, t1)
	max_sim = 0.0
	for i in range(len(long) - len(short) + 1):
		if long[i]==short[0]:
			sub = long[i:i + len(short)]
			sim = similarity_token(sub, short)
			if sim > 0.5:
				max_sim = max(max_sim, sim)
	return max_sim

def match_book_tokens(ocr_tokens: List[str], book_tokens: List[str]) -> float:
	"""以 OCR token 與書目 token 的相似度計算書目匹配分數。

	逐一檢查每個書目 token；若它與任一 OCR token 的最高相似度大於 0.5，
	便將總分加一。回傳符合門檻的書目 token 數量。
	"""
	if not ocr_tokens or not book_tokens:
		return 0.0
	total = 0.0
	
	for bt in book_tokens:
		best_score = 0.0
		for ot in ocr_tokens:
			s = similarity_token2(ot.lower(), bt.lower())
			if s > best_score:
				best_score = s
			# if s > 0.5:
			# 	print(f"'{ot}'  <=> '{bt}' : similarity = {s:.4f}")
		if best_score > 0.5:
			total += 1
		
	return total


def find_best_matches(books: List[dict], ocrs: List[dict], top_n: int = 1) -> List[dict]:
	"""為每筆 OCR 辨識結果找出分數最高的前 top_n 本書。

	逐一計算 OCR 結果與所有書目的匹配分數，依分數由高至低排序，
	並回傳各 OCR 原始資料及其候選書目索引與分數。
	"""
	results = []
	for o in ocrs:
		best = []
		for i, b in enumerate(books):
			score = match_book_tokens(o["tokens"], b["tokens"])
			best.append((i, score))
		best.sort(key=lambda x: x[1], reverse=True)
		picks = best[:top_n]
		results.append({"ocr": o["entry"], "matches": picks})
	return results


def main() -> None:
	"""載入書目與 OCR 結果、計算候選匹配，並將結果寫入 JSON 檔。"""
	base = Path(".")
	csv_path = base / "bookslist.csv"
	ocr_json = base / "output_4dirs_combine" / "ocr_results.json"

	if not csv_path.exists():
		print(f"bookslist.csv not found at {csv_path}")
		return
	if not ocr_json.exists():
		print(f"OCR results not found at {ocr_json}")
		return

	books = load_books(csv_path)
	# for b in books:
	print(f"\n----------------\n")
	print(f"{books[0]}")
	ocrs = load_ocr_results(ocr_json)

	# for o in ocrs:
	print(f"\n----------------\n")
	print(f"{ocrs[0]}")
	matches = find_best_matches(books, ocrs, top_n=3)

	out = []
	for m in matches:
		o = m["ocr"]
		rec = {"text": o.get("text", ""), "candidates": []}
		for idx, score in m["matches"]:
			rec["candidates"].append({"book_row": books[idx]["row"], "score": score})
		out.append(rec)

	Path("book_match_results.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
	print(f"Wrote book_match_results.json with {len(out)} entries")


if __name__ == "__main__":
	main()
