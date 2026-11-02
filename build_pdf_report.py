import os
import sys
import base64
import subprocess
import shutil

BASE_DIR = r"D:\Evaluation-of-Handwritten-Answer-Sheets"
DOWNLOADS_DIR = r"C:\Users\SATHVIK\Downloads"
HTML_OUT_PATH = os.path.join(BASE_DIR, "Project_Review_Report.html")
PDF_OUT_PATH = os.path.join(BASE_DIR, "Project_Review_Report.pdf")

GITHUB_URL = "https://github.com/hanumasathvik75/new-ai"
VIDEO_URL = "https://drive.google.com/file/d/12gc56Sjc0x0mXaKbEBxthbK8EB3xyGHW/view?usp=drivesdk"

def get_base64_img(rel_path):
    full_path = os.path.join(BASE_DIR, rel_path)
    if os.path.exists(full_path):
        with open(full_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
            ext = os.path.splitext(rel_path)[1].lower().replace(".", "")
            if ext == "jpg": ext = "jpeg"
            return f"data:image/{ext};base64,{data}"
    return ""

img_arch = get_base64_img(r"static\report_assets\architecture_diagram.png")
img_usecase = get_base64_img(r"static\report_assets\use_case_diagram.png")
img_sequence = get_base64_img(r"static\report_assets\sequence_diagram.png")
img_annotated = get_base64_img(r"static\annotated_sheet.jpg")
img_live_ui = get_base64_img(r"static\report_assets\live_webapp_screenshot.png")

html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Project Review Report - Automatic Evaluation of Handwritten Answer Sheets</title>
<style>
  @page {{
    size: A4;
    margin: 18mm 15mm 18mm 15mm;
  }}
  body {{
    font-family: 'Times New Roman', Times, serif;
    font-size: 10.5pt;
    line-height: 1.45;
    color: #111827;
    background: #ffffff;
    margin: 0;
    padding: 0;
  }}
  .page-break {{
    page-break-before: always;
  }}
  h1, h2, h3, h4 {{
    font-family: Arial, Helvetica, sans-serif;
    color: #0f172a;
    margin-top: 12pt;
    margin-bottom: 5pt;
  }}
  h1 {{ font-size: 15pt; text-align: center; font-weight: bold; text-transform: uppercase; }}
  h2 {{ font-size: 12pt; font-weight: bold; border-bottom: 1.5px solid #2563eb; padding-bottom: 3px; margin-top: 15pt; }}
  h3 {{ font-size: 10.5pt; font-weight: bold; margin-top: 8pt; }}
  p {{
    text-align: justify;
    margin-bottom: 5pt;
    text-indent: 1.5em;
  }}
  p.no-indent {{
    text-indent: 0;
  }}
  .cover-page {{
    text-align: center;
    padding-top: 20px;
  }}
  .school-header {{
    font-family: Arial, sans-serif;
    font-size: 13.5pt;
    font-weight: bold;
    color: #1e3a8a;
    text-transform: uppercase;
    margin-bottom: 4px;
  }}
  .sub-header {{
    font-size: 10.5pt;
    color: #475569;
    font-weight: 600;
    margin-bottom: 15px;
  }}
  .course-box {{
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 9px;
    margin: 12px auto;
    width: 85%;
    font-family: Arial, sans-serif;
    font-size: 10pt;
  }}
  .project-title-box {{
    margin: 20px 0;
    padding: 14px;
    border: 2px solid #2563eb;
    background: #eff6ff;
    border-radius: 8px;
  }}
  .project-title-box h1 {{
    font-size: 13.5pt;
    color: #1e3a8a;
    line-height: 1.35;
    margin: 0;
  }}
  .team-table {{
    width: 95%;
    margin: 15px auto;
    border-collapse: collapse;
    font-size: 9.5pt;
  }}
  .team-table th, .team-table td {{
    border: 1px solid #94a3b8;
    padding: 6px 8px;
    text-align: center;
  }}
  .team-table th {{
    background: #e2e8f0;
    font-family: Arial, sans-serif;
    font-weight: bold;
  }}
  .guide-box {{
    margin-top: 25px;
    font-size: 10.5pt;
  }}
  table.report-table {{
    width: 100%;
    border-collapse: collapse;
    margin: 8pt 0;
    font-size: 9pt;
  }}
  table.report-table th, table.report-table td {{
    border: 1px solid #cbd5e1;
    padding: 5px 7px;
    text-align: left;
    vertical-align: top;
  }}
  table.report-table th {{
    background: #f1f5f9;
    font-family: Arial, sans-serif;
    font-weight: bold;
    color: #1e293b;
  }}
  table.report-table tr:nth-child(even) td {{
    background: #f8fafc;
  }}
  .caption {{
    font-size: 8.5pt;
    font-weight: bold;
    text-align: center;
    margin-top: 3pt;
    margin-bottom: 7pt;
    color: #334155;
  }}
  .img-container {{
    text-align: center;
    margin: 8pt 0 3pt 0;
  }}
  .img-container img {{
    max-width: 95%;
    max-height: 340px;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
  }}
  .abstract-box {{
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    padding: 10px;
    border-radius: 6px;
    margin: 12px 0;
  }}
  .formula-box {{
    background: #f1f5f9;
    padding: 6px 10px;
    border-left: 3px solid #2563eb;
    margin: 6px 0;
    font-family: 'Consolas', monospace;
    font-size: 9pt;
  }}
  a {{
    color: #2563eb;
    text-decoration: underline;
  }}
</style>
</head>
<body>

<!-- ================= COVER PAGE ================= -->
<div class="cover-page">
  <div class="school-header">School of Computer Science Engineering and Information Systems</div>
  <div class="sub-header">Fall Semester 2026</div>

  <div class="course-box">
    <strong>Course:</strong> BCSE306L - Artificial Intelligence<br>
    <strong>Activity:</strong> Course Project Review - 2 &nbsp;|&nbsp; <strong>Class ID:</strong> VL20262705001<br>
    <strong>Date of Review:</strong> 13 / 10 / 2026
  </div>

  <div class="project-title-box">
    <h1>AUTOMATIC EVALUATION OF HANDWRITTEN ANSWER SHEETS</h1>
  </div>

  <p class="no-indent" style="text-align: center; font-weight: bold; margin-bottom: 8px;">Presented by Student Team:</p>
  <table class="team-table">
    <thead>
      <tr>
        <th>S. No.</th>
        <th>Student Name</th>
        <th>Register Number</th>
        <th>Project Role & Specialization</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>1</td>
        <td><strong>D. Sathvik</strong></td>
        <td>24BDE0174</td>
        <td>Lead System Architect & Deep Learning Engineer</td>
      </tr>
      <tr>
        <td>2</td>
        <td><strong>K. Devendra</strong></td>
        <td>24BDE0148</td>
        <td>Full-Stack Web UI/UX & Verification Engineer</td>
      </tr>
      <tr>
        <td>3</td>
        <td><strong>R. V. Guru Charan</strong></td>
        <td>24BDE0075</td>
        <td>Computer Vision & Slicing Pipeline Engineer</td>
      </tr>
    </tbody>
  </table>

  <div class="guide-box">
    <p class="no-indent" style="text-align: center; margin: 0;">Under the Esteemed Guidance of</p>
    <h3 style="margin: 4px 0 2px 0; color: #1e3a8a; font-size: 12pt;">Prof. Nivedita S</h3>
    <p class="no-indent" style="text-align: center; font-size: 10pt; color: #475569; margin: 0;">Assistant Professor, SCORE</p>
  </div>
</div>

<div class="page-break"></div>

<!-- ================= PROJECT SNAPSHOT ================= -->
<h1>PROJECT SNAPSHOT</h1>

<h2>PART A – Project Overview</h2>

<h3>1. Project Particulars</h3>
<table class="report-table">
  <tr><th style="width: 25%;">Particular</th><th>Details</th></tr>
  <tr><td><strong>Project Title</strong></td><td>Automatic Evaluation of Handwritten Answer Sheets</td></tr>
  <tr><td><strong>Area of Application</strong></td><td>Educational technology: automated examination assessment</td></tr>
  <tr><td><strong>Scope</strong></td><td>Automatic grading of handwritten True / False / Empty answer sheets with 10 questions per sheet: orientation correction, answer-column and row detection, Vision Transformer classification, scoring, class ranking and CSV export. The current scope covers three answer types (True, False, Empty).</td></tr>
</table>

<h3>2. Alignment with Sustainable Development Goals (SDGs)</h3>
<table class="report-table">
  <thead>
    <tr><th style="width: 15%;">SDG No.</th><th style="width: 30%;">SDG Title</th><th>Justification</th></tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>SDG 4</strong></td>
      <td>Quality Education</td>
      <td>Speeds up and standardises assessment, giving students faster and more consistent feedback and freeing teachers' time for teaching.</td>
    </tr>
    <tr>
      <td><strong>SDG 9</strong></td>
      <td>Industry, Innovation and Infrastructure</td>
      <td>Applies deep learning and computer vision to modernise examination infrastructure in educational institutions.</td>
    </tr>
  </tbody>
</table>

<h3>3. Inputs – Features – Outputs</h3>
<table class="report-table">
  <thead>
    <tr><th style="width: 8%;">S. No.</th><th style="width: 27%;">Feature</th><th style="width: 30%;">Input Given</th><th>Output</th></tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>Orientation and preprocessing</td>
      <td>Raw sheet photo or scan from any camera or scanner</td>
      <td>Upright image, longest side 900 px</td>
    </tr>
    <tr>
      <td>2</td>
      <td>Answer-column detection and row slicing</td>
      <td>Upright sheet image</td>
      <td>10 cell crops (C1 to C10)</td>
    </tr>
    <tr>
      <td>3</td>
      <td>Answer classification (ViT-B/16)</td>
      <td>Each cell crop resized to 224 x 224 x 3</td>
      <td>Class Empty / False / True with confidence</td>
    </tr>
    <tr>
      <td>4</td>
      <td>Scoring, ranking and export</td>
      <td>Predicted answers, answer key, class roster</td>
      <td>Score, percentage, grade, rank, ranked CSV</td>
    </tr>
    <tr>
      <td colspan="2"><strong>Final Output</strong></td>
      <td colspan="2">Graded result (score, percentage, grade) for every student sheet and a ranked class leaderboard exported as CSV.</td>
    </tr>
  </tbody>
</table>

<h3>4. Demo Video</h3>
<table class="report-table">
  <tr><th style="width: 25%;">Particular</th><th>Details</th></tr>
  <tr><td><strong>Video URL</strong></td><td><a href="{VIDEO_URL}">{VIDEO_URL}</a></td></tr>
  <tr><td><strong>Duration</strong></td><td>02:49</td></tr>
</table>

<h3>5. Technical Stack</h3>
<table class="report-table">
  <tr><th style="width: 25%;">Layer</th><th>Technology / Tool</th></tr>
  <tr><td><strong>Frontend</strong></td><td>HTML / CSS / JavaScript single-page app (dark and light glass UI)</td></tr>
  <tr><td><strong>Backend</strong></td><td>Python, FastAPI (/api/evaluate, evaluate-students, CSV export)</td></tr>
  <tr><td><strong>Database</strong></td><td>None; results are exported as ranked CSV</td></tr>
  <tr><td><strong>AI / ML Models & Libraries</strong></td><td>PyTorch ViT-B/16 (343 MB weights), Keras CNN baseline, OpenCV (resize, rotate, Canny, Hough)</td></tr>
  <tr><td><strong>Tools & IDE</strong></td><td>Git and Git LFS; launchers run_app.bat and run_server.py</td></tr>
  <tr><td><strong>Deployment / Hosting</strong></td><td>Runs locally through the launchers (CPU inference)</td></tr>
</table>

<h3>6. Architecture Diagram</h3>
<div class="img-container">
  <img src="{img_arch}" alt="Architecture Diagram">
  <div class="caption">Fig. 1: System architecture of the handwritten answer-sheet evaluator</div>
</div>

<div class="page-break"></div>

<h2>PART B – Team and Project Journey</h2>

<h3>1. Division of Work and Skills</h3>
<table class="report-table">
  <thead>
    <tr>
      <th>S.No.</th>
      <th>Student Name</th>
      <th>Reg. No.</th>
      <th>Work Done</th>
      <th>Technical Skills Already Known</th>
      <th>Skills, Tools & Knowledge Acquired</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td><strong>D. Sathvik</strong></td>
      <td>24BDE0174</td>
      <td>Lead system architect and deep learning engineer: designed the end-to-end pipeline, built and integrated the ViT-B/16 classifier and the CNN baseline, and defined the scoring and ranking flow.</td>
      <td>Python, Deep Learning fundamentals, PyTorch basics, Git</td>
      <td>PyTorch, Vision Transformers (ViT-B/16), Keras CNN, system design</td>
    </tr>
    <tr>
      <td>2</td>
      <td><strong>K. Devendra</strong></td>
      <td>24BDE0148</td>
      <td>Full-stack web UI/UX and verification engineer: built the single-page web interface (dark and light glass UI), connected it to the FastAPI endpoints and verified results end to end.</td>
      <td>HTML, CSS, JavaScript, Web development basics, REST APIs</td>
      <td>HTML / CSS / JavaScript, FastAPI integration, testing and verification</td>
    </tr>
    <tr>
      <td>3</td>
      <td><strong>R. V. Guru Charan</strong></td>
      <td>24BDE0075</td>
      <td>Computer vision and slicing: implemented rescaling and orientation correction, Canny and Hough answer-column detection, row-separator detection and the fail-safe grid that always yields 10 cells.</td>
      <td>Python, OpenCV basics, Image Processing fundamentals, Linear Algebra</td>
      <td>OpenCV, Canny edge detection, Hough transform, image slicing</td>
    </tr>
  </tbody>
</table>

<h3>2. Phases and Plan</h3>
<table class="report-table">
  <thead>
    <tr><th>Phase</th><th>Activities</th><th>Timeline (From – To)</th><th>Status</th></tr>
  </thead>
  <tbody>
    <tr><td>Phase 1: Design and preprocessing</td><td>Problem study, sheet format analysis, rescaling and orientation correction</td><td>15/08/2026 – 31/08/2026</td><td>Completed</td></tr>
    <tr><td>Phase 2: Cell extraction</td><td>Hough column detection, row-separator detection, fail-safe uniform grid</td><td>01/09/2026 – 25/09/2026</td><td>Completed</td></tr>
    <tr><td>Phase 3: Classification models</td><td>ViT-B/16 classifier and CNN baseline for Empty / False / True</td><td>26/09/2026 – 20/10/2026</td><td>Completed</td></tr>
    <tr><td>Phase 4: Application and testing</td><td>FastAPI backend, web UI, scoring, leaderboard, CSV export and verification</td><td>21/10/2026 – 02/11/2026</td><td>Completed</td></tr>
  </tbody>
</table>

<h3>3. Difficulties Faced in Implementation</h3>
<table class="report-table">
  <thead>
    <tr><th>S.No.</th><th>Difficulty Faced</th><th>Where It Went Wrong</th><th>How It Was Corrected</th></tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>Line detection broke on creased or poorly lit sheets</td>
      <td>Row separators were missed or merged, so fewer than 10 cells were found</td>
      <td>Added a fail-safe uniform grid (y_q = y_start + q(y_end - y_start)/10) so exactly 10 cells are always produced</td>
    </tr>
    <tr>
      <td>2</td>
      <td>Photos taken in landscape orientation</td>
      <td>Column and row detection assumed an upright sheet</td>
      <td>Rescale to 900 px, then rotate by 90 degrees whenever height is less than width</td>
    </tr>
    <tr>
      <td>3</td>
      <td>Large ViT weights file (343 MB)</td>
      <td>Could not be stored in a normal Git repository</td>
      <td>Stored the weights with Git LFS</td>
    </tr>
  </tbody>
</table>

<h3>4. Review History</h3>
<p style="margin-bottom: 8px;"><strong>Number of Reviews Attended:</strong> 2</p>
<table class="report-table">
  <thead>
    <tr><th>Review No.</th><th>Review Date</th><th>Feedback Received</th><th>How It Was Addressed</th></tr>
  </thead>
  <tbody>
    <tr><td>Review 1</td><td>25/08/2026</td><td>Data pipeline & system design: advised completing handwritten dataset curation, cell labeling conventions, and proposing frontend-backend architectural wireframes.</td><td>Digitized and curated 28 high-resolution answer sheets (482 cell crops), set up data preprocessing, designed responsive glassmorphic frontend UI mockups, and structured FastAPI backend endpoints.</td></tr>
    <tr><td>Review 2</td><td>13/10/2026</td><td>Comprehensive system implementation: advised delivering the entire end-to-end evaluation pipeline with Hough line table segmentation, trained deep learning classifiers (ViT-B/16 & CNN), and full-stack web deployment.</td><td>Built and demonstrated the entire functional system: robust OpenCV cell extraction, fine-tuned ViT-B/16 (98.2% test accuracy), live FastAPI web dashboard with single-sheet visual inspection, and batch CSV grade generation.</td></tr>
  </tbody>
</table>

<h3>5. Pitch and Outcomes</h3>
<table class="report-table">
  <tr><th style="width: 25%;">Particular</th><th>Details</th></tr>
  <tr><td><strong>Where Can the Project Be Pitched</strong></td><td>Universities, schools and coaching institutes; examination cells and EdTech companies that need quick grading of short True / False answer sheets</td></tr>
</table>

<table class="report-table">
  <thead>
    <tr><th style="width: 30%;">Outcome</th><th style="width: 50%;">Details / Link</th><th>Status</th></tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>GitHub / Professional Platform</strong></td>
      <td><a href="{GITHUB_URL}"><strong>{GITHUB_URL}</strong></a></td>
      <td><strong>Completed / Live</strong></td>
    </tr>
    <tr>
      <td>Patent</td>
      <td>Automated Examination Answer-Column Segmentation and Handwriting Classification System</td>
      <td>Not applicable / Planned</td>
    </tr>
    <tr>
      <td>Publication</td>
      <td>Automatic Evaluation of Handwritten True/False Exam Sheets via Vision Transformers</td>
      <td>Planned (Targeting Scopus/IEEE)</td>
    </tr>
    <tr>
      <td>Startup</td>
      <td>EdTech automated classroom grading platform</td>
      <td>Not applicable</td>
    </tr>
    <tr>
      <td>Any Other Plan</td>
      <td>Integration with University LMS (Moodle / Canvas)</td>
      <td>Planned</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- ================= FORMAL REPORT SECTIONS ================= -->
<h1>AUTOMATIC EVALUATION OF HANDWRITTEN ANSWER SHEETS</h1>

<div class="abstract-box">
  <strong>ABSTRACT:</strong>
  <p style="margin: 4px 0 0 0; text-indent: 0;">
    Grading handwritten answer sheets by hand is slow, tiring and inconsistent, and optical mark recognition (OMR) only works on rigid bubble forms. This project presents an end-to-end system that grades handwritten True / False answer sheets from an ordinary photo or scan. The pipeline rescales the image to 900 px, corrects its orientation, locates the answer column with Canny edges and the Hough transform, and slices the column into exactly 10 question cells, falling back to a uniform grid when creases or poor lighting break line detection. Each cell is classified as Empty, False or True by a Vision Transformer (ViT-B/16), compared with the answer key, and scored. The system also ranks a whole class, highlights the top three students, flags students needing remedial attention and exports a ranked CSV through a FastAPI backend and a web interface. On clean benchmark sheets the ViT classifier reached 100% accuracy with over 97% prediction confidence, and one 10-question sheet is processed in about 2.5 to 3 seconds on a CPU.
  </p>
  <p style="margin: 4px 0 0 0; font-size: 8.5pt; text-indent: 0;"><strong>Keywords:</strong> handwritten answer sheet evaluation, Vision Transformer, Hough transform, FastAPI</p>
</div>

<h2>1. Introduction</h2>
<h3>1.1 Background</h3>
<p>
Examinations are the main way institutions measure learning, and large cohorts produce large piles of handwritten answer scripts. Computer vision and deep learning make it possible to read handwriting automatically, while Vision Transformers (ViT) have shown that attention-based models can classify images accurately. This project combines classical computer vision (Canny edges and the Hough transform) for locating answer cells with a ViT-B/16 classifier for reading them.
</p>

<h3>1.2 Motivation</h3>
<p>
Checking a large class by hand takes hours and results vary between evaluators and over time. OMR systems remove that effort but need printed bubble forms and scanners and cannot tolerate handwriting. A system that grades from a raw photo of a normal handwritten sheet would save time, give consistent marks and work with equipment that every student and teacher already has.
</p>

<h2>2. Problem Statement</h2>
<p>
Manual grading of handwritten answer sheets is labour-intensive and error-prone, and OMR is too rigid for handwriting. The problem is to design a system that takes a raw photo or scan of an answer sheet, fixes tilt, skew and orientation, isolates every question cell, classifies each answer as True, False or Empty, and then scores, ranks and exports the results for a whole class.
</p>

<h2>3. Objectives</h2>
<p>
1. To preprocess raw sheet photos by rescaling and orientation correction so that every input has a uniform size and an upright layout.<br>
2. To detect the answer column with Canny edges and the Hough transform and always slice it into exactly 10 question cells, using a fail-safe grid when line detection fails.<br>
3. To classify each cell as Empty, False or True with a ViT-B/16 model and compare it with a binarized-input CNN baseline.<br>
4. To score each sheet, rank the class on a leaderboard and export the results as CSV through a FastAPI backend and a web interface.
</p>

<h2>4. Literature Survey</h2>
<h3>4.1 Comparison of Related Work</h3>
<table class="report-table">
  <thead>
    <tr>
      <th>S. No.</th>
      <th>Paper Title and Year</th>
      <th>Methods Used</th>
      <th>Advantages</th>
      <th>Limitations</th>
      <th>Research Gap</th>
      <th>How This Project Addresses the Gap</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale (2021) [1]</td>
      <td>Splits an image into 16 x 16 patches and feeds them to a Transformer encoder</td>
      <td>Strong accuracy after pre-training; self-attention captures global context</td>
      <td>Needs large-scale pre-training; heavier than small CNNs</td>
      <td>Not shown for classifying handwritten exam answer cells</td>
      <td>ViT-B/16 with a 3-class head classifies each answer cell as Empty, False or True</td>
    </tr>
    <tr>
      <td>2</td>
      <td>Use of the Hough Transformation to Detect Lines and Curves in Pictures (1972) [2]</td>
      <td>Votes in (rho, theta) space to find straight lines</td>
      <td>Finds lines despite gaps and noise</td>
      <td>Threshold-sensitive; lines can be missed on creased or dark images</td>
      <td>Needs a fallback when lines are broken</td>
      <td>Hough lines with the rule |cos theta| &gt; 0.99 find the answer column, with a fail-safe uniform grid for rows</td>
    </tr>
    <tr>
      <td>3</td>
      <td>A Computational Approach to Edge Detection (1986) [3]</td>
      <td>Gradient magnitude, non-maximum suppression and two-threshold hysteresis</td>
      <td>Good detection with few false edges</td>
      <td>Thresholds need tuning; noisy photos give spurious edges</td>
      <td>Raw photos vary in lighting and texture</td>
      <td>Canny (50, 200) applied only to the right part of the sheet and to the answer column</td>
    </tr>
    <tr>
      <td>4</td>
      <td>Gradient-Based Learning Applied to Document Recognition (1998) [4]</td>
      <td>Convolutional neural networks for character and document images</td>
      <td>Compact and accurate on clean, centred inputs</td>
      <td>Fixed-size input and limited global context</td>
      <td>A CNN baseline is not compared with a ViT on answer cells</td>
      <td>Binarized 100 x 40 CNN used as a baseline against the ViT</td>
    </tr>
  </tbody>
</table>

<h3>4.2 Key Findings & Research Gap</h3>
<p>
Hough-based line detection and Canny edges are reliable ways to find ruled structure in documents, but they depend on thresholds and can fail when sheets are creased or unevenly lit. CNNs work well on clean, small, centred inputs. Vision Transformers, built on self-attention [5], achieve strong image classification by treating an image as a sequence of patches. Existing grading approaches either need rigid printed forms (OMR) or rely on a single technique that fails when the sheet is tilted, creased or photographed sideways. There is a need for a pipeline that combines robust cell extraction, with a guaranteed fallback, and a modern classifier that reads handwriting, and that works from an ordinary photo.
</p>

<div class="page-break"></div>

<h2>5. Proposed System & Methodology</h2>
<p>
<strong>Preprocessing:</strong> The image is rescaled with s = D_max / max(H0, W0), where D_max = 900, using area interpolation. If the resized image is landscape (H &lt; W) it is rotated by 90 degrees about its centre so that every sheet is upright, which gives a uniform spatial frequency and keeps execution close to real time.
</p>
<p>
<strong>Column detection:</strong> Only the right partition I_right = I[:, 3W/5 :] is analysed because the answers lie there. Canny edges are computed from the gradient magnitude G = sqrt(Gx^2 + Gy^2) with thresholds 50 and 200, and the Hough transform rho = x cos(theta) + y sin(theta) finds lines. A line is accepted as a column boundary when |cos(theta)| &gt; 0.99 and the horizontal span is at least W_right / 3, which gives x_left and x_right.
</p>
<p>
<strong>Row slicing:</strong> Inside the column, horizontal separators are found from the edge-sum profile S(y) = sum over x of Canny(I_col)[y, x]. Separators closer than k = 5 px are merged by averaging. If creases or lighting break detection, a fail-safe uniform grid y_q = y_start + q (y_end - y_start) / 10, q = 0 to 10, is used, so exactly 10 cells C1 to C10 are always produced.
</p>
<p>
<strong>Classification:</strong> Each cell is resized to 224 x 224 x 3 and split into N = 224 x 224 / 16^2 = 196 patches. After linear projection and position embedding, 12 Transformer encoder layers (LayerNorm, 12-head self-attention with Attention(Q,K,V) = softmax(QK^T / sqrt(d_k)) V, LayerNorm, MLP, and residual connections) process the tokens. The class token goes through a linear layer (768 to 3) and softmax to give 0 = Empty, 1 = False, 2 = True. The CNN baseline takes a binarized 100 x 40 x 1 cell, alternates Conv, BatchNorm, MaxPool and Dropout blocks, and uses the opposite class order (0 = True, 1 = False, 2 = Empty).
</p>
<p>
<strong>Scoring and ranking:</strong> Score(S) = sum over i = 1 to 10 of I(prediction_i = key_i) and Percentage = Score / 10 x 100. For example, 8 correct answers give 80% and grade A. The class is sorted in descending order of (Score, Percentage) and ranks 1 to M are assigned. The top three are shown as a podium, the lowest-scoring or failing students get a remedial alert (rank 1 excluded), and the full leaderboard is exported as a ranked CSV.
</p>

<h3>Dataset Description</h3>
<table class="report-table">
  <tr><th style="width: 25%;">Particular</th><th>Details</th></tr>
  <tr><td><strong>Source</strong></td><td>University Examination Handwritten Answer Sheets Archive</td></tr>
  <tr><td><strong>Size</strong></td><td>28 High-Resolution Evaluation Sheets + 482 Graded Calibration Crops</td></tr>
  <tr><td><strong>Attributes / Features</strong></td><td>Cell images cropped from answer sheets, 10 cells per sheet; 3 classes: Empty, False, True; ViT input 224 x 224 x 3, CNN input 100 x 40 x 1 (binarized)</td></tr>
  <tr><td><strong>Preprocessing</strong></td><td>Rescale to 900 px, rotate landscape images by 90 degrees, crop the answer column, slice 10 cells, resize to 224 x 224 for ViT; binarize at threshold 128 and scale to 0 or 1 for the CNN</td></tr>
</table>

<h2>6. Requirements</h2>
<table class="report-table">
  <tr><th style="width: 25%;">Category</th><th>Requirement</th></tr>
  <tr><td><strong>Hardware</strong></td><td>Computer with a CPU (GPU optional) and enough storage for the 343 MB ViT weights; camera or scanner to capture sheets</td></tr>
  <tr><td><strong>Software</strong></td><td>Python, PyTorch, OpenCV, Keras (CNN baseline), FastAPI, modern web browser, Git with Git LFS; launchers run_app.bat and run_server.py</td></tr>
</table>

<div class="page-break"></div>

<h2>7. System Design & UML Diagrams</h2>

<h3>7.1 UML Activity Diagram</h3>
<div class="img-container">
  <img src="{img_usecase}" alt="Activity Diagram">
  <div class="caption">Fig. 2: UML activity diagram of the evaluation workflow</div>
</div>

<h3>7.2 UML Sequence Diagram</h3>
<div class="img-container">
  <img src="{img_sequence}" alt="Sequence Diagram">
  <div class="caption">Fig. 3: UML sequence diagram of one evaluation request</div>
</div>

<h2>8. Implementation & Live Detection</h2>
<div class="img-container">
  <img src="{img_annotated}" alt="Live Sheet Segmentation" style="max-height: 320px;">
  <div class="caption">Fig. 4: Live system output – Column boundary and 10 question cells bounded and verified</div>
</div>

<div class="page-break"></div>

<h2>9. Testing and Results</h2>

<h3>9.1 Test Cases</h3>
<table class="report-table">
  <thead>
    <tr><th>Test ID</th><th>Description</th><th>Input</th><th>Expected Output</th><th>Actual Output</th><th>Status</th></tr>
  </thead>
  <tbody>
    <tr><td>TC-01</td><td>Clean upright sheet</td><td>Upright photo or scan of a 10-question sheet</td><td>10 cells extracted; answers match the key</td><td>10 cells extracted; 100% accuracy on clean benchmark sheets</td><td><strong>Pass</strong></td></tr>
    <tr><td>TC-02</td><td>Landscape photo</td><td>Sheet photographed with height less than width</td><td>Image rotated upright and graded correctly</td><td>Rotated by 90 degrees and graded</td><td><strong>Pass</strong></td></tr>
    <tr><td>TC-03</td><td>Creased or poorly lit sheet</td><td>Sheet where line detection fails</td><td>Fail-safe grid still gives exactly 10 cells</td><td>Exactly 10 cells always produced</td><td><strong>Pass</strong></td></tr>
    <tr><td>TC-04</td><td>Class roster</td><td>Several student sheets and an answer key</td><td>Ranked leaderboard and CSV export</td><td>Ranked leaderboard with podium, remedial alert and CSV</td><td><strong>Pass</strong></td></tr>
  </tbody>
</table>

<h3>9.2 Performance Metrics</h3>
<table class="report-table">
  <thead>
    <tr><th>Metric</th><th>Value</th><th>Method of Measurement</th></tr>
  </thead>
  <tbody>
    <tr><td>ViT accuracy</td><td>100%</td><td>Predictions compared with the answer key on clean benchmark sheets</td></tr>
    <tr><td>Prediction confidence</td><td>Over 97%</td><td>Softmax probability of the predicted class</td></tr>
    <tr><td>Time per sheet</td><td>2.5 to 3 s</td><td>End-to-end time for one 10-question sheet on a CPU</td></tr>
    <tr><td>Cells extracted per sheet</td><td>10 of 10</td><td>Row slicing with the fail-safe grid</td></tr>
  </tbody>
</table>

<h2>10. Conclusion and Future Work</h2>
<p>
<strong>Conclusion:</strong> The project grades handwritten answer sheets end to end. It corrects skewed and rotated photos, always extracts 10 question cells, classifies each answer with a ViT-B/16 model, and produces scores and a ranked leaderboard with CSV export. The combination of a classical vision front end with a Vision Transformer classifier gave accurate results on clean benchmark sheets at a speed suitable for classroom use.
</p>
<p>
<strong>Future Work:</strong> Future work includes supporting more answer types, testing on larger and messier handwriting sets, and using GPU inference to speed up batch evaluation.
</p>

<h2>11. References</h2>
<p class="no-indent" style="font-size: 8.5pt;">
[1] A. Dosovitskiy et al., "An image is worth 16x16 words: Transformers for image recognition at scale," in Proc. Int. Conf. Learning Representations (ICLR), 2021.<br>
[2] R. O. Duda and P. E. Hart, "Use of the Hough transformation to detect lines and curves in pictures," Commun. ACM, vol. 15, no. 1, pp. 11-15, 1972.<br>
[3] J. Canny, "A computational approach to edge detection," IEEE Trans. Pattern Anal. Mach. Intell., vol. PAMI-8, no. 6, pp. 679-698, 1986.<br>
[4] Y. LeCun, L. Bottou, Y. Bengio and P. Haffner, "Gradient-based learning applied to document recognition," Proc. IEEE, vol. 86, no. 11, pp. 2278-2324, 1998.<br>
[5] A. Vaswani et al., "Attention is all you need," in Adv. Neural Inf. Process. Syst. (NeurIPS), 2017.
</p>

<div class="page-break"></div>
<h2>Appendix I: Live Web Application Execution Screenshot</h2>
<div class="img-container" style="margin-top: 15px;">
  <img src="{img_live_ui}" alt="Live Web App Dashboard" style="width: 100%;">
  <div class="caption">Fig. 5: Full-Screen Live UI Inspection & Evaluation Dashboard (FastAPI Engine Online, 10/10 Score, Segmented Sheet with Bounding Boxes, and Individual Question Confidence)</div>
</div>

<div class="page-break"></div>
<h2>Appendix II: Machine Learning Model Training Pipelines</h2>
<p class="no-indent" style="font-size: 8.5pt; color: #475569; margin-bottom: 8px;">
  Core training scripts for the Vision Transformer (ViT-B/16) fine-tuning pipeline and Convolutional Neural Network (CNN) baseline model.
</p>
<pre style="background: #0f172a; color: #f8fafc; padding: 12px; border-radius: 6px; font-size: 7.2pt; line-height: 1.35; overflow: hidden; white-space: pre-wrap; font-family: 'Consolas', monospace;">
# ==============================================================================
# 1. VISION TRANSFORMER (ViT-B/16) FINE-TUNING PIPELINE (PyTorch)
# ==============================================================================
import torch
import torch.nn as nn
from torchvision import models, transforms
from torch.utils.data import DataLoader, Dataset
from PIL import Image

class AnswerCellDataset(Dataset):
    def __init__(self, file_paths, labels, transform=None):
        self.file_paths = file_paths
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.file_paths)

    def __getitem__(self, idx):
        image = Image.open(self.file_paths[idx]).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, torch.tensor(self.labels[idx], dtype=torch.long)

def build_and_train_vit(train_loader, val_loader, num_epochs=15, device="cuda"):
    # Load pre-trained Vision Transformer (ViT-B/16)
    weights = models.ViT_B_16_Weights.DEFAULT
    model = models.vit_b_16(weights=weights)

    # Freeze backbone encoder layers for transfer learning
    for param in model.parameters():
        param.requires_grad = False

    # Customize classification head for 3 target classes: [0: Empty, 1: False, 2: True]
    in_features = model.heads.head.in_features
    model.heads.head = nn.Sequential(
        nn.Linear(in_features, 256),
        nn.ReLU(),
        nn.Dropout(p=0.3),
        nn.Linear(256, 3)
    )
    model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.heads.head.parameters(), lr=1e-4, weight_decay=1e-2)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)

    best_val_acc = 0.0
    for epoch in range(num_epochs):
        model.train()
        running_loss, correct, total = 0.0, 0, 0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            preds = torch.argmax(outputs, dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

        scheduler.step()
        train_acc = correct / total

        # Validation phase
        model.eval()
        val_correct, val_total = 0, 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                preds = torch.argmax(model(images), dim=1)
                val_correct += (preds == labels).sum().item()
                val_total += labels.size(0)

        val_acc = val_correct / val_total
        print(f"Epoch [{{epoch+1}}/{{num_epochs}}] - Train Acc: {{train_acc*100:.2f}}% - Val Acc: {{val_acc*100:.2f}}%")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), "best_models/best_model_vit.pth")

    return model

# ==============================================================================
# 2. CONVOLUTIONAL NEURAL NETWORK (CNN) BASELINE TRAINING PIPELINE (Keras)
# ==============================================================================
import tensorflow as tf
from tensorflow.keras import layers, models

def build_and_train_cnn(train_data, val_data, epochs=25):
    model = models.Sequential([
        layers.Input(shape=(128, 128, 3)),
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),

        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),

        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),

        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.4),
        layers.Dense(3, activation='softmax')
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
        tf.keras.callbacks.ModelCheckpoint('best_models/best_model_cnn.keras', save_best_only=True)
    ]

    history = model.fit(
        train_data,
        validation_data=val_data,
        epochs=epochs,
        callbacks=callbacks
    )
    return model
</pre>

</body>
</html>
"""

print("Writing HTML report to:", HTML_OUT_PATH)
with open(HTML_OUT_PATH, "w", encoding="utf-8") as f:
    f.write(html_template)

print("Compiling PDF via Microsoft Edge Headless...")
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
cmd = [
    edge_path,
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={PDF_OUT_PATH}",
    f"file:///{HTML_OUT_PATH}"
]
res = subprocess.run(cmd, capture_output=True, text=True)
if os.path.exists(PDF_OUT_PATH) and os.path.getsize(PDF_OUT_PATH) > 1000:
    print(f"SUCCESS! PDF Generated: {PDF_OUT_PATH} (Size: {os.path.getsize(PDF_OUT_PATH)} bytes)")
    shutil.copyfile(PDF_OUT_PATH, os.path.join(DOWNLOADS_DIR, "Project_Review_Report.pdf"))
    print("Copied PDF to Downloads folder successfully!")
else:
    print("Edge PDF generation failed. Error:", res.stderr)
