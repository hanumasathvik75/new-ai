# 📝 Automatic Evaluation of Handwritten Answer Sheets — Web Application

A full-stack, real-time web application for automated evaluation and grading of handwritten True/False answer sheets using Deep Learning (**Vision Transformer ViT-B/16** and **Convolutional Neural Networks**).

---

## 🚀 Live Server & Access

The FastAPI server is currently **active and running**:

- **Web App UI:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive API Docs (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🌟 Key Features

1. **Dual Deep Learning Models:**
   - **Vision Transformer (ViT-B/16):** Pre-trained and fine-tuned for high accuracy classification of handwritten "True", "False", and "Empty" answer cells.
   - **Convolutional Neural Network (CNN):** Fast, lightweight model option.
2. **Interactive Answer Key Customizer:**
   - Click-to-toggle 10-question answer key (True / False).
   - Built-in presets: *Preset 1*, *Preset 2*, *All True*, *All False*, and *Invert All*.
3. **Single Sheet Inspection:**
   - Drag & drop or upload scanned or photographed answer sheets.
   - Image orientation controls (0°, 90°, 180°, 270°).
   - Automatic column segmentation and cell extraction.
   - **Visual Overlay:** View the annotated answer sheet with the detected column and question bounding boxes highlighted.
   - **Question Breakdown:** Inspect the cropped handwritten snippet for every individual question (Q1–Q10), the model's prediction, confidence percentage bar, and correct/incorrect mark.
4. **Batch Grading & CSV Export:**
   - Upload multiple sheets at once, or grade all 28 repository sample sheets with one click.
   - Live analytics: Total Sheets, Class Average Score, Pass Rate.
   - Download the generated `Graded_sheets.csv` report instantly.
5. **Sample Gallery:**
   - Pre-loaded gallery of test sheets from `Train_Samples_V0`.
   - One-click "⚡ Test This Sheet" button to instantly evaluate any sample without needing to upload files.
6. **Dark / Light Mode:**
   - Sleek modern theme with toggle switch and persistence.

---

## 🛠️ How to Restart or Run Anytime

You can launch the web app anytime using either of the following methods:

### Option 1: Double-click Windows Batch File
Double click `run_app.bat` located at:
```
D:\Evaluation-of-Handwritten-Answer-Sheets\run_app.bat
```

### Option 2: Run via Terminal (PowerShell / Command Prompt)
```powershell
cd D:\Evaluation-of-Handwritten-Answer-Sheets
py -3.12 run_server.py
```

Then open your browser at **[http://127.0.0.1:8000](http://127.0.0.1:8000)**.
