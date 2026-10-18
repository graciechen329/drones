from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any

import cv2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Draw book detection boxes from a Roboflow log onto an image."
    )
    parser.add_argument("--log", default="abc.log", help="Path to the Roboflow log.")
    parser.add_argument("--image", default="book.jpg", help="Source bookshelf image.")
    parser.add_argument("--output", default="result.jpg", help="Output image path.")
    return parser.parse_args()


def load_predictions(log_path: Path) -> list[dict[str, Any]]:
    text = log_path.read_text(encoding="utf-16")
    marker = "Detected "
    marker_position = text.find(marker)
    if marker_position < 0:
        raise ValueError(f"Could not find detection data in {log_path}.")

    list_start = text.find("[", marker_position)
    if list_start < 0:
        raise ValueError(f"Could not find the prediction list in {log_path}.")
    separator = text.find("\n==================", list_start)
    list_text = text[list_start:] if separator < 0 else text[list_start:separator]

    decoder = json.JSONDecoder()
    try:
        predictions, _ = decoder.raw_decode(list_text)
    except json.JSONDecodeError:
        try:
            predictions = ast.literal_eval(list_text)
        except (SyntaxError, ValueError) as error:
            raise ValueError(f"Could not parse prediction data in {log_path}.") from error

    if not isinstance(predictions, list) or not all(
        isinstance(item, dict) for item in predictions
    ):
        raise ValueError("Prediction data must be a list of objects.")
    return predictions


def draw_predictions(
    image_path: Path, predictions: list[dict[str, Any]], output_path: Path
) -> None:
    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Unable to load image: {image_path}")

    supported_extensions = {".bmp", ".jpeg", ".jpg", ".png", ".tif", ".tiff"}
    if output_path.suffix.lower() not in supported_extensions:
        output_path = output_path.with_suffix(".jpg")
        print(f"Unsupported image extension for {output_path.name}; saving as {output_path.name} instead.")

    for index, prediction in enumerate(predictions, start=1):
        try:
            x_center = float(prediction["x"])
            y_center = float(prediction["y"])
            box_width = float(prediction["width"])
            box_height = float(prediction["height"])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid bounding box at prediction {index}.") from error

        x1 = round(x_center - box_width / 2)
        y1 = round(y_center - box_height / 2)
        x2 = round(x_center + box_width / 2)
        y2 = round(y_center + box_height / 2)

        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 180, 0), 8)
        cv2.putText(
            image,
            str(index),
            (x1 + 8, max(32, y1 + 42)),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.3,
            (0, 0, 255),
            3,
            cv2.LINE_AA,
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(output_path), image):
        raise OSError(f"Unable to write output image: {output_path}")


def main() -> None:
    args = parse_args()
    log_path = Path(args.log)
    image_path = Path(args.image)
    output_path = Path(args.output)

    if not log_path.exists():
        raise FileNotFoundError(f"Log not found: {log_path}")
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    predictions = load_predictions(log_path)
    draw_predictions(image_path, predictions, output_path)
    print(f"Drew {len(predictions)} book boxes on {output_path}.")


if __name__ == "__main__":
    main()