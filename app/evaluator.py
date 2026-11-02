import os
import io
import time
import base64
import logging
from typing import List, Dict, Any, Optional, Tuple

import cv2
import numpy as np
from PIL import Image

import torch
import torchvision
from torchvision import transforms
from torch import nn

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Evaluator")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "best_models")
VIT_PATH = os.path.join(MODELS_DIR, "best_model_vit.pth")
CNN_PATH = os.path.join(MODELS_DIR, "best_model_cnn.keras")
SAMPLES_DIR = os.path.join(BASE_DIR, "Train_Samples_V0", "Train_Samples_V0")


class SheetEvaluator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.vit_model = None
        self.cnn_model = None
        self.vit_loaded = False
        self.cnn_loaded = False
        
        # Load ViT transformation
        self.vit_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
        ])
        
        # Prediction class mappings
        # ViT mapping from notebook: 2 -> True, 1 -> False, 0 -> Empty
        self.vit_map = {2: "True", 1: "False", 0: "Empty"}
        # CNN mapping from notebook: 0 -> True, 1 -> False, 2 -> Empty
        self.cnn_map = {0: "True", 1: "False", 2: "Empty"}

    def load_vit(self):
        if self.vit_loaded:
            return True
        try:
            logger.info(f"Loading ViT model from {VIT_PATH}...")
            if not os.path.exists(VIT_PATH) or os.path.getsize(VIT_PATH) < 10000:
                logger.error("ViT model file is missing or incomplete (Git LFS pointer).")
                return False
                
            model = torchvision.models.vit_b_16(weights=None)
            model.heads = nn.Linear(in_features=768, out_features=3)
            state_dict = torch.load(VIT_PATH, map_location=self.device)
            model.load_state_dict(state_dict)
            model.to(self.device)
            model.eval()
            self.vit_model = model
            self.vit_loaded = True
            logger.info(f"ViT model loaded successfully on {self.device}!")
            return True
        except Exception as e:
            logger.exception(f"Failed to load ViT model: {e}")
            return False

    def load_cnn(self):
        if self.cnn_loaded:
            return True
        try:
            logger.info(f"Loading CNN model from {CNN_PATH}...")
            if not os.path.exists(CNN_PATH) or os.path.getsize(CNN_PATH) < 10000:
                logger.error("CNN model file is missing or incomplete.")
                return False
                
            import tensorflow as tf
            # Suppress excessive TF logs
            os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
            self.cnn_model = tf.keras.models.load_model(CNN_PATH)
            self.cnn_loaded = True
            logger.info("CNN model loaded successfully!")
            return True
        except Exception as e:
            logger.exception(f"Failed to load CNN model: {e}")
            return False

    @staticmethod
    def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))
        M[0, 2] += (new_w / 2) - center[0]
        M[1, 2] += (new_h / 2) - center[1]
        return cv2.warpAffine(image, M, (new_w, new_h))

    def preprocess_image(self, img: np.ndarray, manual_rotation: int = 0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Resize image so max dim is ~900px, handle rotation, and produce:
        1. Grayscale sharpened image for segmentation
        2. BGR colored image for UI visualization overlay
        """
        # Apply manual rotation if specified
        if manual_rotation in [90, 180, 270]:
            img = self.rotate_image(img, manual_rotation)
        elif img.shape[0] < img.shape[1]:
            # Auto-rotate if horizontal
            img = self.rotate_image(img, 90)

        # Scale down for processing
        max_dim = max(img.shape[:2])
        scale = round(900.0 / max_dim, 2) if max_dim > 0 else 1.0
        width = int(img.shape[1] * scale)
        height = int(img.shape[0] * scale)
        resized_bgr = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)

        # Grayscale
        if len(resized_bgr.shape) == 3:
            img_gray = cv2.cvtColor(resized_bgr, cv2.COLOR_BGR2GRAY)
        else:
            img_gray = resized_bgr.copy()
            resized_bgr = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)

        # Sharpen grayscale
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 1))
        sharpened_gray = cv2.filter2D(img_gray, -1, kernel)

        return sharpened_gray, resized_bgr

    def extract_column_and_cells(
        self,
        img_gray: np.ndarray,
        img_bgr: np.ndarray,
        expected_cells: int = 10
    ) -> Tuple[List[np.ndarray], List[Tuple[int, int, int, int]], np.ndarray]:
        """
        Locates the rightmost answer column and splits it into rows (cells).
        Returns:
            - List of cropped cell images (grayscale)
            - List of cell bounding boxes (x, y, w, h) in img_bgr coordinates
            - Annotated img_bgr with detections drawn
        """
        H, W = img_gray.shape[:2]
        annotated_bgr = img_bgr.copy()

        # The True/False column is located in the right portion of the answer sheet
        crop_x_start = 3 * W // 5
        right_gray = img_gray[:, crop_x_start:]
        right_H, right_W = right_gray.shape[:2]

        canny = cv2.Canny(right_gray, 50, 200, None, 3)
        col_x1 = 0
        col_x2 = right_W

        try:
            lines = cv2.HoughLines(canny, 1, np.pi / 180, 200)
            if lines is not None:
                lines = np.reshape(lines, (-1, 2))
                vertical_lines = []
                for i in lines:
                    if abs(np.cos(i[1])) > 0.99:
                        r, theta = i[0], i[1]
                        if np.cos(theta) < 0:
                            r = abs(r)
                            theta = np.pi + theta
                        vertical_lines.append([r, theta])

                if len(vertical_lines) >= 2:
                    vertical_lines = np.array(vertical_lines)
                    vertical_lines = vertical_lines[vertical_lines[:, 0].argsort()]
                    v_edges = [vertical_lines[0]]
                    for i in range(1, len(vertical_lines)):
                        if abs(vertical_lines[i][0] - v_edges[-1][0]) >= right_W // 3:
                            v_edges.append(vertical_lines[i])

                    v_edges = np.array(v_edges, dtype=int)
                    if len(v_edges) >= 2:
                        # Found column bounds
                        c1 = max(0, v_edges[0][0])
                        c2 = min(right_W, v_edges[1][0])
                        if (c2 - c1) > 25:
                            col_x1 = c1
                            col_x2 = c2
        except Exception as e:
            logger.debug(f"Hough column detection fallback: {e}")

        # If column detection was too narrow or wide, use robust fallback
        if (col_x2 - col_x1) < 30 or (col_x2 - col_x1) > right_W * 0.9:
            col_x1 = right_W // 6
            col_x2 = 5 * right_W // 6

        TFcol = right_gray[:, col_x1:col_x2]
        abs_col_x1 = crop_x_start + col_x1
        abs_col_x2 = crop_x_start + col_x2

        # Draw the column boundary on annotated image
        cv2.rectangle(
            annotated_bgr,
            (abs_col_x1, 0),
            (abs_col_x2, H),
            (0, 200, 255),
            2
        )

        # Detect horizontal dividers in TFcol
        cannyTF = cv2.Canny(TFcol, 10, 100, None, 3)
        kernel = 5
        tolerance = 8
        horizontal = []
        for i in range(kernel, cannyTF.shape[0] - kernel):
            h_line = False
            for j in range(tolerance, cannyTF.shape[1] - tolerance):
                for k in range(-kernel, kernel):
                    if (cannyTF[i + k, j - 1] == 255 or cannyTF[i + k, j] == 255 or cannyTF[i + k, j + 1] == 255):
                        h_line = True
                        break
                else:
                    h_line = False
                    break
                h_line = True
            if h_line:
                horizontal.append(i)

        min_lines = []
        if len(horizontal) > 1:
            s, n = 0, 0
            for i in range(len(horizontal) - 1):
                if horizontal[i + 1] - horizontal[i] <= kernel:
                    s += horizontal[i]
                    n += 1
                    if i == len(horizontal) - 2:
                        min_lines.append(int(s / n))
                else:
                    s += horizontal[i]
                    n += 1
                    min_lines.append(int(s / n))
                    if i == len(horizontal) - 2:
                        min_lines.append(horizontal[-1])
                    s = 0
                    n = 0

        if len(min_lines) > 0 and min_lines[0] < 10:
            min_lines = min_lines[1:]
        if len(min_lines) >= 13:
            min_lines = min_lines[2:]

        cell_crops = []
        cell_boxes = []

        # Check if detected dividers yield valid cells
        if len(min_lines) >= 10:
            valid_cuts = []
            for i in range(len(min_lines) - 1):
                h_diff = min_lines[i + 1] - min_lines[i]
                if 20 <= h_diff <= 250:
                    valid_cuts.append((min_lines[i], min_lines[i + 1]))
            if len(valid_cuts) >= 8:
                # Use detected dividers
                for y1, y2 in valid_cuts[:expected_cells]:
                    cell_crop = TFcol[y1:y2, :]
                    cell_crops.append(cell_crop)
                    cell_boxes.append((abs_col_x1, y1, abs_col_x2 - abs_col_x1, y2 - y1))

        # Uniform fallback if edge detection didn't get 10 cells
        if len(cell_crops) < expected_cells:
            cell_crops = []
            cell_boxes = []
            # Top/bottom margins of the sheet table
            y_start = int(H * 0.12)
            y_end = int(H * 0.88)
            available_h = y_end - y_start
            cell_h = available_h // expected_cells

            for q in range(expected_cells):
                y1 = y_start + q * cell_h
                y2 = min(H, y1 + cell_h)
                cell_crop = TFcol[y1:y2, :] if y2 <= TFcol.shape[0] else TFcol[max(0, TFcol.shape[0]-cell_h):, :]
                cell_crops.append(cell_crop)
                cell_boxes.append((abs_col_x1, y1, abs_col_x2 - abs_col_x1, cell_h))

        # Draw cell boundaries on annotated image
        for idx, (bx, by, bw, bh) in enumerate(cell_boxes):
            cv2.rectangle(annotated_bgr, (bx, by), (bx + bw, by + bh), (0, 255, 100), 2)
            cv2.putText(
                annotated_bgr,
                f"Q{idx + 1}",
                (max(10, bx - 45), by + bh // 2 + 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 0),
                2
            )

        return cell_crops, cell_boxes, annotated_bgr

    @staticmethod
    def encode_cv2_image_to_base64(img: np.ndarray, quality: int = 85) -> str:
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        _, buffer = cv2.imencode(".jpg", img, encode_param)
        b64_str = base64.b64encode(buffer).decode("utf-8")
        return f"data:image/jpeg;base64,{b64_str}"

    def evaluate_sheet(
        self,
        image_bytes: bytes,
        correct_answers: List[str],
        model_type: str = "vit",
        manual_rotation: int = 0,
        filename: str = "sheet.jpg"
    ) -> Dict[str, Any]:
        """
        Full evaluation pipeline for one sheet.
        """
        # Decode image
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Could not decode the provided image bytes.")

        start_time = time.time()

        # Preprocess
        img_gray, img_bgr = self.preprocess_image(img, manual_rotation)

        # Segment column and 10 cells
        expected_cells = len(correct_answers) if correct_answers else 10
        cell_crops, cell_boxes, annotated_bgr = self.extract_column_and_cells(
            img_gray, img_bgr, expected_cells=expected_cells
        )

        model_type = model_type.lower()
        predictions = []
        confidences = []

        if model_type == "vit":
            if not self.vit_loaded:
                success = self.load_vit()
                if not success:
                    raise RuntimeError("ViT model could not be loaded. Please ensure best_model_vit.pth is downloaded.")

            # Prepare ViT batch: convert each cell to PIL RGB and transform
            t_imgs = []
            for crop in cell_crops:
                pil_img = Image.fromarray(crop).convert("RGB")
                t_imgs.append(self.vit_transform(pil_img))

            batch_tensor = torch.stack(t_imgs).to(self.device)
            self.vit_model.eval()
            with torch.no_grad():
                logits = self.vit_model(batch_tensor)
                probs = torch.softmax(logits, dim=1)
                best_probs, pred_indices = torch.max(probs, dim=1)

            for p_idx, prob in zip(pred_indices, best_probs):
                predictions.append(self.vit_map.get(p_idx.item(), "Empty"))
                confidences.append(round(prob.item() * 100, 1))

        elif model_type == "cnn":
            if not self.cnn_loaded:
                success = self.load_cnn()
                if not success:
                    raise RuntimeError("CNN model could not be loaded. Please ensure best_model_cnn.keras exists.")

            # Prepare CNN batch: resize to (100, 40), threshold, divide 255
            for crop in cell_crops:
                resized = cv2.resize(crop, (40, 100))
                _, binary = cv2.threshold(resized, 128, 255, cv2.THRESH_BINARY)
                scaled = binary.astype(np.float32) / 255.0
                cell_input = np.expand_dims(scaled, axis=(0, -1)) # Shape (1, 100, 40, 1)

                preds = self.cnn_model.predict(cell_input, verbose=0)[0]
                idx = int(np.argmax(preds))
                conf = float(preds[idx]) * 100.0
                predictions.append(self.cnn_map.get(idx, "Empty"))
                confidences.append(round(conf, 1))
        else:
            raise ValueError(f"Unknown model_type '{model_type}'. Choose 'vit' or 'cnn'.")

        # Grade against correct answers
        results_cells = []
        total_score = 0
        total_questions = len(cell_crops)

        for i, (pred, conf, crop) in enumerate(zip(predictions, confidences, cell_crops)):
            correct = correct_answers[i] if i < len(correct_answers) else "True"
            is_match = (pred.lower() == correct.lower())
            mark = 1 if is_match else 0
            total_score += mark

            # Encode cell crop thumbnail
            cell_thumb_b64 = self.encode_cv2_image_to_base64(crop, quality=80)

            results_cells.append({
                "qno": i + 1,
                "predicted": pred,
                "confidence": conf,
                "correct_answer": correct,
                "is_correct": is_match,
                "mark": mark,
                "cell_thumbnail": cell_thumb_b64
            })

        percentage = round((total_score / total_questions) * 100.0, 1) if total_questions > 0 else 0.0
        elapsed_sec = round(time.time() - start_time, 2)
        annotated_b64 = self.encode_cv2_image_to_base64(annotated_bgr, quality=85)

        # Determine grade letter
        if percentage >= 90:
            letter_grade = "A+"
        elif percentage >= 80:
            letter_grade = "A"
        elif percentage >= 70:
            letter_grade = "B"
        elif percentage >= 60:
            letter_grade = "C"
        elif percentage >= 50:
            letter_grade = "D"
        else:
            letter_grade = "F"

        return {
            "filename": filename,
            "model_used": model_type.upper(),
            "total_score": total_score,
            "max_score": total_questions,
            "percentage": percentage,
            "letter_grade": letter_grade,
            "processing_time_sec": elapsed_sec,
            "cells": results_cells,
            "annotated_image": annotated_b64,
            "evaluated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }


# Singleton evaluator
evaluator = SheetEvaluator()
