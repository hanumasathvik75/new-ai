import os
import sys
import uvicorn

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    print("=" * 65)
    print("  Automatic Evaluation of Handwritten Answer Sheets")
    print("  FastAPI Server + HTML/CSS/JS Web Interface")
    print("=" * 65)
    print("  Server URL: http://127.0.0.1:8000")
    print("  Docs URL:   http://127.0.0.1:8000/docs")
    print("=" * 65)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, log_level="info")
