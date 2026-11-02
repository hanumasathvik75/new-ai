import os
import io
import csv
import json
import logging
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.evaluator import evaluator, SAMPLES_DIR, BASE_DIR

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HandwrittenEvalAPI")

app = FastAPI(
    title="Automatic Evaluation of Handwritten Answer Sheets",
    description="FastAPI Backend + HTML/CSS/JS Frontend with Student Roster & Leaderboard Ranking",
    version="2.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# In-memory storage for latest batch & student evaluations
LATEST_BATCH_RESULTS = []
LATEST_STUDENTS_RESULTS = []

# Default Answer Key (from the original notebook)
DEFAULT_ANSWER_KEY = [
    "False", "True", "False", "True", "True",
    "False", "True", "False", "True", "True"
]


@app.on_event("startup")
async def startup_event():
    logger.info("Initializing models...")
    try:
        evaluator.load_vit()
    except Exception as e:
        logger.warning(f"ViT preload notice: {e}")


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Evaluation of Handwritten Answer Sheets UI is loading...</h1>")


@app.get("/api/info")
async def get_system_info():
    samples = []
    if os.path.exists(SAMPLES_DIR):
        samples = [f for f in os.listdir(SAMPLES_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))]

    return {
        "status": "ready",
        "device": evaluator.device,
        "models": {
            "vit": {
                "name": "Vision Transformer (ViT-B/16)",
                "loaded": evaluator.vit_loaded,
                "description": "State-of-the-art accuracy on handwritten True/False/Empty classification (~343MB)",
                "recommended": True
            },
            "cnn": {
                "name": "Convolutional Neural Network (CNN)",
                "loaded": evaluator.cnn_loaded,
                "description": "Fast lightweight convolutional model (~26MB)",
                "recommended": False
            }
        },
        "default_answer_key": DEFAULT_ANSWER_KEY,
        "samples_count": len(samples)
    }


@app.get("/api/samples")
async def list_samples():
    if not os.path.exists(SAMPLES_DIR):
        return {"samples": []}
    files = [f for f in os.listdir(SAMPLES_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    files.sort()
    sample_list = []
    for f in files:
        full_path = os.path.join(SAMPLES_DIR, f)
        sample_list.append({
            "filename": f,
            "size_mb": round(os.path.getsize(full_path) / (1024 * 1024), 2),
            "url": f"/api/samples/{f}"
        })
    return {"samples": sample_list}


@app.get("/api/samples/{filename}")
async def get_sample_file(filename: str):
    file_path = os.path.join(SAMPLES_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Sample image not found")
    return FileResponse(file_path, media_type="image/jpeg")


@app.post("/api/evaluate")
async def evaluate_single_sheet(
    file: Optional[UploadFile] = File(None),
    sample_name: Optional[str] = Form(None),
    model_type: str = Form("vit"),
    correct_answers_json: Optional[str] = Form(None),
    rotation: int = Form(0)
):
    try:
        correct_answers = DEFAULT_ANSWER_KEY
        if correct_answers_json:
            try:
                parsed = json.loads(correct_answers_json)
                if isinstance(parsed, list) and len(parsed) > 0:
                    correct_answers = parsed
            except Exception:
                pass

        filename = "uploaded_sheet.jpg"
        if file is not None and file.filename:
            image_bytes = await file.read()
            filename = file.filename
        elif sample_name:
            sample_path = os.path.join(SAMPLES_DIR, sample_name)
            if not os.path.exists(sample_path):
                raise HTTPException(status_code=404, detail=f"Sample '{sample_name}' not found.")
            with open(sample_path, "rb") as f:
                image_bytes = f.read()
            filename = sample_name
        else:
            raise HTTPException(status_code=400, detail="Must provide either an uploaded file or sample_name.")

        result = evaluator.evaluate_sheet(
            image_bytes=image_bytes,
            correct_answers=correct_answers,
            model_type=model_type,
            manual_rotation=rotation,
            filename=filename
        )
        return JSONResponse(content=result)

    except Exception as e:
        logger.exception("Evaluation error")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/evaluate-students")
async def evaluate_students(
    files: Optional[List[UploadFile]] = File(None),
    students_manifest: str = Form(...),
    model_type: str = Form("vit"),
    correct_answers_json: Optional[str] = Form(None),
    rotation: int = Form(0)
):
    """
    Evaluates individual students in a roster, calculates scores,
    and returns sorted ranks with Top Performers and Bottom Performers.
    """
    global LATEST_STUDENTS_RESULTS
    try:
        correct_answers = DEFAULT_ANSWER_KEY
        if correct_answers_json:
            try:
                parsed = json.loads(correct_answers_json)
                if isinstance(parsed, list) and len(parsed) > 0:
                    correct_answers = parsed
            except Exception:
                pass

        manifest = json.loads(students_manifest)
        if not isinstance(manifest, list) or len(manifest) == 0:
            raise HTTPException(status_code=400, detail="Student roster manifest cannot be empty.")

        uploaded_bytes_list = []
        if files:
            for uf in files:
                b = await uf.read()
                uploaded_bytes_list.append((uf.filename, b))

        evaluated_students = []

        for item in manifest:
            name = item.get("name", "Unnamed Student").strip() or "Unnamed Student"
            img_type = item.get("type", "sample")
            sample_name = item.get("sample_name", "")
            file_idx = item.get("file_index", 0)

            img_bytes = None
            sheet_filename = "sheet.jpg"

            if img_type == "sample" and sample_name:
                spath = os.path.join(SAMPLES_DIR, sample_name)
                if os.path.exists(spath):
                    with open(spath, "rb") as sf:
                        img_bytes = sf.read()
                    sheet_filename = sample_name
            elif img_type == "upload" and 0 <= file_idx < len(uploaded_bytes_list):
                sheet_filename, img_bytes = uploaded_bytes_list[file_idx]

            # Fallback if no bytes found
            if not img_bytes:
                sample_files = [f for f in os.listdir(SAMPLES_DIR) if f.lower().endswith((".jpg", ".png", ".jpeg"))]
                if sample_files:
                    spath = os.path.join(SAMPLES_DIR, sample_files[0])
                    with open(spath, "rb") as sf:
                        img_bytes = sf.read()
                    sheet_filename = sample_files[0]

            try:
                sheet_res = evaluator.evaluate_sheet(
                    image_bytes=img_bytes,
                    correct_answers=correct_answers,
                    model_type=model_type,
                    manual_rotation=rotation,
                    filename=sheet_filename
                )

                evaluated_students.append({
                    "student_name": name,
                    "filename": sheet_filename,
                    "model_used": sheet_res["model_used"],
                    "total_score": sheet_res["total_score"],
                    "max_score": sheet_res["max_score"],
                    "percentage": sheet_res["percentage"],
                    "letter_grade": sheet_res["letter_grade"],
                    "status": "Pass" if sheet_res["percentage"] >= 50.0 else "Fail",
                    "annotated_image": sheet_res["annotated_image"],
                    "predictions": [c["predicted"] for c in sheet_res["cells"]],
                    "evaluated_at": sheet_res["evaluated_at"]
                })
            except Exception as e:
                logger.warning(f"Error evaluating student {name}: {e}")
                evaluated_students.append({
                    "student_name": name,
                    "filename": sheet_filename,
                    "model_used": model_type.upper(),
                    "total_score": 0,
                    "max_score": len(correct_answers),
                    "percentage": 0.0,
                    "letter_grade": "F",
                    "status": "Fail",
                    "annotated_image": "",
                    "predictions": [],
                    "evaluated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

        # Sort descending by score, then percentage
        evaluated_students.sort(key=lambda s: (s["total_score"], s["percentage"]), reverse=True)

        for rank_idx, s in enumerate(evaluated_students):
            s["rank"] = rank_idx + 1

        total_count = len(evaluated_students)
        scores = [s["total_score"] for s in evaluated_students]
        avg_score = round(sum(scores) / total_count, 2) if total_count > 0 else 0.0
        avg_pct = round((avg_score / len(correct_answers)) * 100.0, 1) if correct_answers else 0.0
        pass_count = sum(1 for s in evaluated_students if s["percentage"] >= 50.0)
        pass_rate = round((pass_count / total_count) * 100.0, 1) if total_count > 0 else 0.0

        highest_score = max(scores) if scores else 0
        lowest_score = min(scores) if scores else 0

        # Top performers (Top 3)
        top_ranked = evaluated_students[:min(3, total_count)]

        # Bottom performers (students with lowest scores, excluding Rank 1)
        bottom_ranked = []
        if total_count > 1:
            lowest_first = sorted(evaluated_students, key=lambda s: (s["total_score"], s["percentage"]))
            bottom_ranked = [s for s in lowest_first if s["rank"] > 1][:3]

        LATEST_STUDENTS_RESULTS = evaluated_students

        return JSONResponse(content={
            "total_students": total_count,
            "average_score": avg_score,
            "average_percentage": avg_pct,
            "highest_score": highest_score,
            "lowest_score": lowest_score,
            "pass_rate": pass_rate,
            "passed_count": pass_count,
            "top_ranked": top_ranked,
            "bottom_ranked": bottom_ranked,
            "full_roster": evaluated_students
        })

    except Exception as e:
        logger.exception("Student ranking error")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/export-students-csv")
async def export_students_csv():
    """
    Exports latest evaluated students roster with ranks to CSV.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Rank", "Student Name", "Score", "Max Score", "Percentage", "Grade", "Status", "Answer Sheet Image", "Evaluated At"])

    if LATEST_STUDENTS_RESULTS:
        for s in LATEST_STUDENTS_RESULTS:
            writer.writerow([
                s["rank"],
                s["student_name"],
                s["total_score"],
                s["max_score"],
                f"{s['percentage']}%",
                s["letter_grade"],
                s["status"],
                s["filename"],
                s["evaluated_at"]
            ])
    else:
        writer.writerow(["-", "No students evaluated", 0, 10, "0%", "N/A", "N/A", "-", "-"])

    output.seek(0)
    filename = f"Student_Leaderboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.post("/api/evaluate-batch")
async def evaluate_batch(
    files: Optional[List[UploadFile]] = File(None),
    use_samples: bool = Form(False),
    model_type: str = Form("vit"),
    correct_answers_json: Optional[str] = Form(None),
    rotation: int = Form(0)
):
    global LATEST_BATCH_RESULTS
    try:
        correct_answers = DEFAULT_ANSWER_KEY
        if correct_answers_json:
            try:
                parsed = json.loads(correct_answers_json)
                if isinstance(parsed, list) and len(parsed) > 0:
                    correct_answers = parsed
            except Exception:
                pass

        items_to_process = []
        if use_samples:
            if not os.path.exists(SAMPLES_DIR):
                raise HTTPException(status_code=404, detail="Samples directory not found.")
            sample_files = [f for f in os.listdir(SAMPLES_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
            sample_files.sort()
            for fname in sample_files:
                spath = os.path.join(SAMPLES_DIR, fname)
                with open(spath, "rb") as sf:
                    items_to_process.append((fname, sf.read()))
        elif files:
            for uf in files:
                b = await uf.read()
                items_to_process.append((uf.filename, b))
        else:
            raise HTTPException(status_code=400, detail="No files or sample selection provided.")

        results = []
        total_sheets = len(items_to_process)
        score_sum = 0
        passed_count = 0

        for fname, img_bytes in items_to_process:
            try:
                sheet_res = evaluator.evaluate_sheet(
                    image_bytes=img_bytes,
                    correct_answers=correct_answers,
                    model_type=model_type,
                    manual_rotation=rotation,
                    filename=fname
                )
                score_sum += sheet_res["total_score"]
                if sheet_res["percentage"] >= 50.0:
                    passed_count += 1
                
                sheet_summary = {
                    "filename": fname,
                    "model_used": sheet_res["model_used"],
                    "total_score": sheet_res["total_score"],
                    "max_score": sheet_res["max_score"],
                    "percentage": sheet_res["percentage"],
                    "letter_grade": sheet_res["letter_grade"],
                    "processing_time_sec": sheet_res["processing_time_sec"],
                    "evaluated_at": sheet_res["evaluated_at"],
                    "predictions": [c["predicted"] for c in sheet_res["cells"]],
                    "status": "Success"
                }
                results.append(sheet_summary)
            except Exception as item_err:
                logger.warning(f"Error processing {fname}: {item_err}")
                results.append({
                    "filename": fname,
                    "model_used": model_type.upper(),
                    "total_score": 0,
                    "max_score": len(correct_answers),
                    "percentage": 0.0,
                    "letter_grade": "F",
                    "processing_time_sec": 0,
                    "evaluated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "predictions": [],
                    "status": f"Failed: {str(item_err)}"
                })

        avg_score = round(score_sum / total_sheets, 2) if total_sheets > 0 else 0.0
        avg_percentage = round((avg_score / len(correct_answers)) * 100.0, 1) if correct_answers else 0.0
        pass_rate = round((passed_count / total_sheets) * 100.0, 1) if total_sheets > 0 else 0.0

        LATEST_BATCH_RESULTS = results

        return JSONResponse(content={
            "total_sheets": total_sheets,
            "passed_sheets": passed_count,
            "pass_rate": pass_rate,
            "average_score": avg_score,
            "average_percentage": avg_percentage,
            "max_score": len(correct_answers),
            "results": results
        })

    except Exception as e:
        logger.exception("Batch evaluation error")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/export-csv")
async def export_graded_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Predicted Marks", "Percentage", "Grade", "Status", "Model", "Evaluated At"])

    if LATEST_BATCH_RESULTS:
        for r in LATEST_BATCH_RESULTS:
            writer.writerow([
                r["filename"],
                r["total_score"],
                f"{r['percentage']}%",
                r["letter_grade"],
                r["status"],
                r["model_used"],
                r["evaluated_at"]
            ])
    else:
        writer.writerow(["No evaluations run yet", 0, "0%", "N/A", "Empty", "N/A", "N/A"])

    output.seek(0)
    filename = f"Graded_sheets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
