# Automatic Evaluation of Handwritten Answer Sheets
### End-to-End Exam Grading & Classroom Leaderboard with Vision Transformers (ViT-B/16) and FastAPI

Welcome to the **Automatic Evaluation and Leaderboard Ranking of Handwritten Answer Sheets** project. This system automates the examination evaluation lifecycle by using artificial intelligence to deskew, segment, recognize, and grade handwritten student responses.

Manual grading is time-consuming, prone to cognitive fatigue, and susceptible to evaluation bias. Our platform employs deep learning and morphological computer vision to digitize, classify, and score handwritten answer sheets with consistency and speed.

---

## 🌟 Key Features

1. **Orientation & Skew Correction:** Automatically detects landscape vs. portrait captures and applies affine deskewing.
2. **Hough Line Column & Cell Extraction:** Isolates the right-hand True/False answer table and segments 10 individual question cells using Hough line detection with an adaptive fallback grid.
3. **Deep Learning Classification:** Evaluates handwriting using fine-tuned **Vision Transformer (`ViT-B/16`)** with multi-head self-attention, achieving 100% accuracy on standard test sheets alongside a lightweight CNN baseline.
4. **Interactive Web Dashboard:** Modern glassmorphic web UI built with HTML5/CSS3/Vanilla JS with Dark and Light mode themes.
5. **Classroom Roster & Leaderboard:** Bulk upload student answer sheets with names, automatically grade the class, highlight the **Top 3 Podium (Gold, Silver, Bronze)**, flag bottom students for remedial intervention, and export `Graded_sheets.csv`.
6. **Visual Inspector:** Full-resolution sheet overlays displaying localized question cell bounding boxes and individual prediction confidence heatmaps.

---

## 🚀 Quick Start Guide

### 1. Requirements
- Python 3.10 or above (Python 3.12 recommended)
- Standard multi-core CPU (GPU optional)

### 2. Launch the Web Application
Simply double-click the Windows batch file:
```cmd
run_app.bat
```
Or run from your terminal:
```bash
python run_server.py
```
Open your browser and navigate to:
```text
http://127.0.0.1:8000
```
Interactive API documentation (Swagger UI) is available at:
```text
http://127.0.0.1:8000/docs
```

---

## 🛠️ System Architecture & Workflow

```
[ Raw Exam Paper Photo / Scan ]
             │
             ▼
[ Aspect Scaling (900px) & Affine Deskewing ]
             │
             ▼
[ Hough Line Transform Column Slicing ]
             │
             ▼
[ Horizontal Divider Clustering & Fallback Grid (Q1 - Q10) ]
             │
             ▼
[ Vision Transformer (ViT-B/16) Batch Inference ]
             │
             ▼
[ Answer Key Matching, Marks & Grade Computation ]
             │
             ▼
[ Class Leaderboard Podium & Graded CSV Export ]
```

---

## 📊 Model Benchmark Comparison

| Metric | Vision Transformer (ViT-B/16) | Baseline CNN |
|---|---|---|
| **Test Accuracy on Benchmark Sheets** | **100.0%** (Confidence > 97%) | 60.0% |
| **Model Size** | 343.2 MB (PyTorch Checkpoint) | **26.8 MB** (Keras Checkpoint) |
| **Latency per Full Sheet (CPU)** | 2.84 seconds | **1.12 seconds** |
| **Handling Handwriting Variances** | **Superior** (Global patch attention) | Moderate (Prone to broken stroke disconnects) |
| **Recommendation** | **Primary Production Model** | Lightweight Fallback Model |

---

## 👥 Project Team

- **D Sathvik** (24BDE0174) – *Lead System Architect & Deep Learning Engineer*
- **K Devendra** (24BDE0148) – *Computer Vision & Slicing Pipeline Engineer*
- **R Guru Charan** (24BDE0075) – *Full-Stack Web UI/UX & Verification Engineer*

**Academic Guidance:**
- **Prof. Nivedita S**, Assistant Professor, School of Computer Science Engineering and Information Systems (SCORE)
