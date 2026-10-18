from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

import cv2
import easyocr
import numpy as np
from roboflow import Roboflow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect each book on a bookshelf image and OCR the spine text."
    )
    parser.add_argument("--image",
    default="books.jpg",
     required=True, help="Path to the bookshelf image.")
    parser.add_argument(
        "--api-key",
        default="e2Y4Eb7Ry9fLXPyH5Gm9",
        help="Roboflow API key. Defaults to ROBOFLOW_API_KEY env var if not provided.",
    )
    parser.add_argument(
        "--workspace",
        default="capjamesg",
        help="Roboflow workspace name from the model URL.",
    )
    parser.add_argument(
        "--project",
        default="open-shelves",
        help="Roboflow project name from the model URL.",
    )
    parser.add_argument(
        "--version",
        type=int,
        default=1,
        help="Roboflow model version. Change if your project uses another version.",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=40.0,
        help="Minimum confidence threshold for Roboflow detections.",
    )
    parser.add_argument(
        "--overlap",
        type=float,
        default=30.0,
        help="Overlap threshold for Roboflow detections.",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory to store cropped book images and OCR results.",
    )
    parser.add_argument(
        "--margin",
        type=int,
        default=12,
        help="Padding around detected book boxes before cropping.",
    )
    parser.add_argument(
        "--language",
        default="en",
        choices=["en"],
        help="EasyOCR language model. English also supports digits.",
    )
    return parser.parse_args()


def load_roboflow_model(api_key: str, workspace: str, project: str, version: int) -> Any:
    key = api_key or os.environ.get("ROBOFLOW_API_KEY")
    if not key:
        raise ValueError(
            "Roboflow API key is required. Provide --api-key or set the ROBOFLOW_API_KEY environment variable."
        )

    rf = Roboflow(api_key=key)
    project_ref = rf.workspace(workspace).project(project)
    return project_ref.version(version).model


def detect_books(
    image_path: str,
    model: Any,
    confidence: float,
    overlap: float,
) -> list[dict[str, Any]]:
    prediction = model.predict(image_path, confidence=confidence)
    payload = prediction.json()
    return payload.get("predictions", [])


def crop_book_regions(
    image: np.ndarray,
    predictions: list[dict[str, Any]],
    margin: int = 12,
) -> list[tuple[int, np.ndarray, tuple[int, int, int, int]]]:
    crops: list[tuple[int, np.ndarray, tuple[int, int, int, int]]] = []
    height, width = image.shape[:2]

    for index, item in enumerate(predictions):
        x_center = float(item["x"])
        y_center = float(item["y"])
        box_w = float(item["width"])
        box_h = float(item["height"])

        x1 = max(0, int(x_center - box_w / 2) - margin)
        y1 = max(0, int(y_center - box_h / 2) - margin)
        x2 = min(width, int(x_center + box_w / 2) + margin)
        y2 = min(height, int(y_center + box_h / 2) + margin)

        crop = image[y1:y2, x1:x2]
        if crop.size == 0:
            continue
        crops.append((index, crop, (x1, y1, x2, y2)))

    return crops


def ocr_single_crop(ocr_model: Any, crop: np.ndarray) -> list[dict[str, Any]]:
    rotations = [
        ("0", crop),
        ("90", cv2.rotate(crop, cv2.ROTATE_90_CLOCKWISE)),
        ("180", cv2.rotate(crop, cv2.ROTATE_180)),
        ("270", cv2.rotate(crop, cv2.ROTATE_90_COUNTERCLOCKWISE)),
    ]

    best_items: list[dict[str, Any]] = []
    best_score = -1.0

    text_items: list[dict[str, Any]] = []
    for _, rotated_crop in rotations:
        result = ocr_model.readtext(
            rotated_crop,
            allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
            detail=1,
            paragraph=False,
        )

        for line in result:
            if not isinstance(line, (list, tuple)) or len(line) < 3:
                continue

            text = re.sub(r"[^A-Za-z0-9]", "", str(line[1]))
            if not text:
                continue
            confidence = float(line[2])
            if confidence > 0.3:
                text_items.append({"text": text, "confidence": confidence})

        # if not text_items:
        #     continue

        # score = sum(item["confidence"] for item in text_items)
        # if score > best_score or (abs(score - best_score) < 1e-9 and len(text_items) > len(best_items)):
        #     best_items = text_items
        #     best_score = score

    return text_items  # Return all text items from all rotations, not just the best one


def save_results(output_dir: Path, crops: list[tuple[int, np.ndarray, tuple[int, int, int, int]]], ocr_results: list[dict[str, Any]]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    for idx, crop, _ in crops:
        crop_path = output_dir / f"book_{idx:03d}.png"
        cv2.imwrite(str(crop_path), crop)

    with (output_dir / "ocr_results.json").open("w", encoding="utf-8") as fh:
        json.dump(ocr_results, fh, ensure_ascii=False, indent=2)


def main() -> None:
    args = parse_args()
    
    image_path = Path(args.image)
    if not image_path.exists():
         raise FileNotFoundError(f"Image not found: {image_path}")

    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Unable to load image: {image_path}")
        # raise=抗議#(if影像路徑不存在，則引發錯誤，停止執行)

    model = load_roboflow_model(args.api_key, args.workspace, args.project, args.version)
    #()裡面為load roboflow, detect_books所需的材料;model為roboflow模型;predictions為roboflow模型偵測後的結果
    predictions = detect_books(str(image_path), model, args.confidence, args.overlap)
    print('==================')
    print(f"Detected {len(predictions)} book regions in {image_path}.")
    print(predictions)
    print('==================')



    if not predictions:
        print(f"No book objects detected in {image_path}. Adjust --confidence or --overlap.")
        return

    output_dir = Path(args.output_dir)
    crops = crop_book_regions(image, predictions, margin=args.margin)
   #()裡面為crop_book_regions所需的材料;crops為很多個剪切過後的長方形
    ocr_model = easyocr.Reader([args.language], gpu=False, verbose=False)
    ocr_results: list[dict[str, Any]] = []
 
    for idx, crop, box in crops:
        recognized = ocr_single_crop(ocr_model, crop)
        text = " ".join(item["text"] for item in recognized if item.get("text"))
        ocr_results.append(
            {
                "book_index": idx,
                "bbox": {"x1": box[0], "y1": box[1], "x2": box[2], "y2": box[3]},#記下長方形框的座標(左上右下)
                "text": text,
                "ocr_details": recognized,
                "crop_path": str(output_dir / f"book_{idx:03d}.png"),#存檔掃描到的資訊
            }
        )
       

    save_results(output_dir, crops, ocr_results)
     #每個crop都會重複操作，執行 OCR，並將結果儲存在 ocr_results 中

    print(f"Detected {len(predictions)} book regions in {image_path}.")
    print(f"Saved cropped images and OCR results to {output_dir}.")
    for item in ocr_results:
        print(f"Book {item['book_index']}: {item['text'] or '(no text recognized)'}")


if __name__ == "__main__":
    main()
