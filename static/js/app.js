// Handwritten Answer Sheets Evaluator Web Application
document.addEventListener("DOMContentLoaded", () => {
  // App State
  const state = {
    modelType: "vit",
    rotation: 0,
    answerKey: [
      "False", "True", "False", "True", "True",
      "False", "True", "False", "True", "True"
    ],
    selectedFile: null,
    selectedSampleName: null,
    previewUrl: null,
    samples: [],
    roster: [], // List of { id, name, type, sampleName, file, thumbUrl }
    theme: localStorage.getItem("theme") || "dark"
  };

  // Presets
  const PRESETS = {
    preset1: ["False", "True", "False", "True", "True", "False", "True", "False", "True", "True"],
    preset2: ["True", "True", "False", "False", "True", "False", "True", "False", "False", "True"],
    allTrue: Array(10).fill("True"),
    allFalse: Array(10).fill("False")
  };

  // Sample Names for Auto-Fill
  const SAMPLE_STUDENT_NAMES = [
    "Aarav Patel",
    "Pooja Sharma",
    "Rohan Gupta",
    "Sneha Rao",
    "Vikram Singh",
    "Ananya Iyer",
    "Kabir Verma",
    "Meera Nair",
    "Aditya Sen",
    "Divya Joshi"
  ];

  // DOM Elements - Global
  const themeToggleBtn = document.getElementById("themeToggleBtn");
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");
  const modelInputs = document.querySelectorAll("input[name='modelType']");
  const answerGrid = document.getElementById("answerGrid");
  const rotationButtons = document.querySelectorAll(".btn-rot");
  const imageModal = document.getElementById("imageModal");
  const modalImg = document.getElementById("modalImg");
  const modalClose = document.getElementById("modalClose");

  // DOM Elements - Single Evaluation
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  const previewBanner = document.getElementById("previewBanner");
  const bannerThumb = document.getElementById("bannerThumb");
  const bannerFilename = document.getElementById("bannerFilename");
  const bannerFilesize = document.getElementById("bannerFilesize");
  const removeFileBtn = document.getElementById("removeFileBtn");
  const evaluateBtn = document.getElementById("evaluateBtn");
  const evalSpinner = document.getElementById("evalSpinner");
  const evalBtnText = document.getElementById("evalBtnText");
  const resultsCard = document.getElementById("resultsCard");
  const annotatedSheetImg = document.getElementById("annotatedSheetImg");
  const cellCardsList = document.getElementById("cellCardsList");

  // DOM Elements - Student Roster & Leaderboard
  const addStudentBtn = document.getElementById("addStudentBtn");
  const autoFill5Btn = document.getElementById("autoFill5Btn");
  const autoFill10Btn = document.getElementById("autoFill10Btn");
  const clearRosterBtn = document.getElementById("clearRosterBtn");
  const studentRowsList = document.getElementById("studentRowsList");
  const rosterCount = document.getElementById("rosterCount");
  const evaluateRosterBtn = document.getElementById("evaluateRosterBtn");
  const rosterSpinner = document.getElementById("rosterSpinner");
  const rosterBtnText = document.getElementById("rosterBtnText");
  const rosterResults = document.getElementById("rosterResults");
  const exportStudentsCsvBtn = document.getElementById("exportStudentsCsvBtn");
  const rosterTotalStudents = document.getElementById("rosterTotalStudents");
  const rosterAvgScore = document.getElementById("rosterAvgScore");
  const rosterAvgPct = document.getElementById("rosterAvgPct");
  const rosterHighestScore = document.getElementById("rosterHighestScore");
  const rosterPassRate = document.getElementById("rosterPassRate");
  const rosterPassedCount = document.getElementById("rosterPassedCount");
  const podiumContainer = document.getElementById("podiumContainer");
  const bottomRankedCard = document.getElementById("bottomRankedCard");
  const bottomRankedList = document.getElementById("bottomRankedList");
  const rosterTableBody = document.getElementById("rosterTableBody");

  // DOM Elements - Batch
  const batchDropzone = document.getElementById("batchDropzone");
  const batchFileInput = document.getElementById("batchFileInput");
  const batchSampleBtn = document.getElementById("batchSampleBtn");
  const batchEvaluateBtn = document.getElementById("batchEvaluateBtn");
  const batchSpinner = document.getElementById("batchSpinner");
  const batchBtnText = document.getElementById("batchBtnText");
  const batchResults = document.getElementById("batchResults");
  const batchTableBody = document.getElementById("batchTableBody");
  const batchTotalSheets = document.getElementById("batchTotalSheets");
  const batchAvgScore = document.getElementById("batchAvgScore");
  const batchPassRate = document.getElementById("batchPassRate");
  const batchAvgPercent = document.getElementById("batchAvgPercent");
  const exportCsvBtn = document.getElementById("exportCsvBtn");

  // DOM Elements - Gallery
  const galleryGrid = document.getElementById("galleryGrid");

  // Theme Handling
  document.documentElement.setAttribute("data-theme", state.theme);
  updateThemeIcon();

  themeToggleBtn.addEventListener("click", () => {
    state.theme = state.theme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", state.theme);
    localStorage.setItem("theme", state.theme);
    updateThemeIcon();
  });

  function updateThemeIcon() {
    themeToggleBtn.innerHTML = state.theme === "dark" ? "☀️" : "🌙";
  }

  // Tab Navigation
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      tabButtons.forEach(b => b.classList.remove("active"));
      tabContents.forEach(c => c.style.display = "none");

      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      document.getElementById(targetId).style.display = "block";

      if (targetId === "tab-gallery" && state.samples.length === 0) {
        loadSamples();
      }
    });
  });

  // Model Selection
  modelInputs.forEach(input => {
    input.addEventListener("change", (e) => {
      state.modelType = e.target.value;
    });
  });

  // Rotation Selection
  rotationButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      rotationButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      state.rotation = parseInt(btn.getAttribute("data-rot"), 10);
      if (state.previewUrl) {
        bannerThumb.style.transform = `rotate(${state.rotation}deg)`;
      }
    });
  });

  // Render Answer Key Grid
  function renderAnswerGrid() {
    answerGrid.innerHTML = "";
    state.answerKey.forEach((val, idx) => {
      const chip = document.createElement("div");
      chip.className = `answer-chip val-${val.toLowerCase()}`;
      chip.innerHTML = `
        <span class="q-label">Q${idx + 1}</span>
        <span class="q-val">${val}</span>
      `;
      chip.addEventListener("click", () => {
        state.answerKey[idx] = state.answerKey[idx] === "True" ? "False" : "True";
        renderAnswerGrid();
      });
      answerGrid.appendChild(chip);
    });
  }

  // Answer Key Presets
  document.querySelectorAll(".btn-preset").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const presetKey = e.target.getAttribute("data-preset");
      if (presetKey === "invert") {
        state.answerKey = state.answerKey.map(v => v === "True" ? "False" : "True");
      } else if (PRESETS[presetKey]) {
        state.answerKey = [...PRESETS[presetKey]];
      }
      renderAnswerGrid();
    });
  });

  renderAnswerGrid();

  // =========================================================
  // SINGLE EVALUATION LOGIC
  // =========================================================
  dropzone.addEventListener("click", () => fileInput.click());

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleSelectedFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleSelectedFile(e.target.files[0]);
    }
  });

  function handleSelectedFile(file) {
    state.selectedFile = file;
    state.selectedSampleName = null;
    state.previewUrl = URL.createObjectURL(file);

    bannerThumb.src = state.previewUrl;
    bannerThumb.style.transform = `rotate(${state.rotation}deg)`;
    bannerFilename.textContent = file.name;
    bannerFilesize.textContent = `${(file.size / (1024 * 1024)).toFixed(2)} MB • Ready to evaluate`;

    dropzone.style.display = "none";
    previewBanner.style.display = "flex";
    evaluateBtn.disabled = false;
  }

  removeFileBtn.addEventListener("click", () => {
    state.selectedFile = null;
    state.selectedSampleName = null;
    state.previewUrl = null;
    fileInput.value = "";

    previewBanner.style.display = "none";
    dropzone.style.display = "block";
    evaluateBtn.disabled = true;
  });

  evaluateBtn.addEventListener("click", async () => {
    if (!state.selectedFile && !state.selectedSampleName) return;

    evaluateBtn.disabled = true;
    evalSpinner.style.display = "inline-block";
    evalBtnText.textContent = "Processing & Grading...";

    try {
      const formData = new FormData();
      if (state.selectedFile) {
        formData.append("file", state.selectedFile);
      } else if (state.selectedSampleName) {
        formData.append("sample_name", state.selectedSampleName);
      }
      formData.append("model_type", state.modelType);
      formData.append("correct_answers_json", JSON.stringify(state.answerKey));
      formData.append("rotation", state.rotation);

      const resp = await fetch("/api/evaluate", {
        method: "POST",
        body: formData
      });

      if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.detail || "Evaluation failed");
      }

      const data = await resp.json();
      renderSingleResults(data);

    } catch (err) {
      alert(`Error evaluating sheet: ${err.message}`);
    } finally {
      evaluateBtn.disabled = false;
      evalSpinner.style.display = "none";
      evalBtnText.textContent = "Evaluate Answer Sheet";
    }
  });

  function renderSingleResults(data) {
    resultsCard.style.display = "flex";

    document.getElementById("resScore").textContent = `${data.total_score} / ${data.max_score}`;
    document.getElementById("resScoreSub").textContent = `${data.percentage}% Correct`;
    document.getElementById("resGrade").textContent = data.letter_grade;
    document.getElementById("resModel").textContent = data.model_used;
    document.getElementById("resTime").textContent = `${data.processing_time_sec}s`;

    const scoreBox = document.getElementById("statBoxScore");
    scoreBox.className = `stat-box ${data.percentage >= 50 ? 'success' : 'fail'}`;

    annotatedSheetImg.src = data.annotated_image;

    cellCardsList.innerHTML = "";
    data.cells.forEach(cell => {
      const card = document.createElement("div");
      card.className = "cell-card";

      const predPillClass = cell.predicted.toLowerCase() === "true"
        ? "pill-true"
        : (cell.predicted.toLowerCase() === "false" ? "pill-false" : "pill-empty");

      const markBadgeClass = cell.is_correct ? "mark-correct" : "mark-wrong";
      const markIcon = cell.is_correct ? "✓ +1" : "✗ 0";

      card.innerHTML = `
        <div class="cell-qno">Q${cell.qno}</div>
        <img class="cell-thumb-img" src="${cell.cell_thumbnail}" alt="Crop Q${cell.qno}" />
        <div class="cell-info">
          <div class="cell-pills">
            <span class="pill ${predPillClass}">Predicted: ${cell.predicted}</span>
            <span class="pill pill-key">Key: ${cell.correct_answer}</span>
          </div>
          <div class="conf-bar-bg" title="Confidence: ${cell.confidence}%">
            <div class="conf-bar-fill" style="width: ${cell.confidence}%;"></div>
          </div>
        </div>
        <div class="cell-mark">
          <span class="mark-badge ${markBadgeClass}">${markIcon}</span>
          <span style="font-size: 0.7rem; color: var(--text-muted);">${cell.confidence}%</span>
        </div>
      `;
      cellCardsList.appendChild(card);
    });

    resultsCard.scrollIntoView({ behavior: "smooth" });
  }

  // Modal Image Zoom
  annotatedSheetImg.addEventListener("click", () => {
    modalImg.src = annotatedSheetImg.src;
    imageModal.classList.add("open");
  });

  modalClose.addEventListener("click", () => {
    imageModal.classList.remove("open");
  });

  imageModal.addEventListener("click", (e) => {
    if (e.target === imageModal) {
      imageModal.classList.remove("open");
    }
  });

  // =========================================================
  // STUDENT ROSTER & LEADERBOARD RANKING LOGIC
  // =========================================================
  let nextStudentId = 1;

  function renderRosterRows() {
    studentRowsList.innerHTML = "";
    rosterCount.textContent = state.roster.length;
    evaluateRosterBtn.disabled = state.roster.length === 0;

    if (state.roster.length === 0) {
      studentRowsList.innerHTML = `
        <div style="text-align: center; padding: 2rem; color: var(--text-muted);">
          No students added yet. Click <strong>"➕ Add Student"</strong> or <strong>"⚡ Fill 5 Sample Students"</strong> above to begin!
        </div>
      `;
      return;
    }

    state.roster.forEach((student, index) => {
      const row = document.createElement("div");
      row.className = "student-row";

      // Options for sample select
      let sampleOptionsHtml = `<option value="">-- Choose Sample Paper --</option>`;
      state.samples.forEach(s => {
        const selected = s.filename === student.sampleName ? "selected" : "";
        sampleOptionsHtml += `<option value="${s.filename}" ${selected}>${s.filename} (${s.size_mb} MB)</option>`;
      });

      row.innerHTML = `
        <div class="student-idx">#${index + 1}</div>
        <div>
          <input type="text" class="student-input" data-id="${student.id}" value="${student.name}" placeholder="Student Name (e.g. Rahul Sharma)" />
        </div>
        <div class="paper-selector">
          <img class="paper-thumb-preview" src="${student.thumbUrl || '/static/css/placeholder.png'}" alt="Sheet Preview" />
          <div class="paper-info">
            <select class="paper-select-dropdown" data-id="${student.id}">
              ${sampleOptionsHtml}
            </select>
            <div style="display: flex; gap: 0.5rem; align-items: center; margin-top: 0.2rem;">
              <label class="btn-xs" style="cursor: pointer;">
                📁 Upload Custom Paper
                <input type="file" class="student-file-input" data-id="${student.id}" accept="image/jpeg,image/png,image/jpg" style="display: none;" />
              </label>
              <span class="paper-filename">${student.sampleName || (student.file ? student.file.name : 'No paper attached')}</span>
            </div>
          </div>
        </div>
        <div>
          <button class="btn-icon btn-remove-student" data-id="${student.id}" title="Remove Student" style="color: var(--accent-rose);">✕</button>
        </div>
      `;

      studentRowsList.appendChild(row);
    });

    // Attach row events
    document.querySelectorAll(".student-input").forEach(input => {
      input.addEventListener("input", (e) => {
        const id = parseInt(e.target.getAttribute("data-id"), 10);
        const st = state.roster.find(s => s.id === id);
        if (st) st.name = e.target.value;
      });
    });

    document.querySelectorAll(".paper-select-dropdown").forEach(sel => {
      sel.addEventListener("change", (e) => {
        const id = parseInt(e.target.getAttribute("data-id"), 10);
        const st = state.roster.find(s => s.id === id);
        if (st) {
          st.type = "sample";
          st.sampleName = e.target.value;
          st.file = null;
          st.thumbUrl = e.target.value ? `/api/samples/${e.target.value}` : "";
          renderRosterRows();
        }
      });
    });

    document.querySelectorAll(".student-file-input").forEach(inp => {
      inp.addEventListener("change", (e) => {
        const id = parseInt(e.target.getAttribute("data-id"), 10);
        const st = state.roster.find(s => s.id === id);
        if (st && e.target.files && e.target.files.length > 0) {
          const file = e.target.files[0];
          st.type = "upload";
          st.file = file;
          st.sampleName = file.name;
          st.thumbUrl = URL.createObjectURL(file);
          renderRosterRows();
        }
      });
    });

    document.querySelectorAll(".btn-remove-student").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const id = parseInt(e.target.getAttribute("data-id"), 10);
        state.roster = state.roster.filter(s => s.id !== id);
        renderRosterRows();
      });
    });
  }

  function addStudent(name = "", sampleName = "") {
    const student = {
      id: nextStudentId++,
      name: name || `Student ${state.roster.length + 1}`,
      type: "sample",
      sampleName: sampleName || (state.samples.length > 0 ? state.samples[state.roster.length % state.samples.length].filename : ""),
      file: null,
      thumbUrl: ""
    };
    if (student.sampleName) {
      student.thumbUrl = `/api/samples/${student.sampleName}`;
    }
    state.roster.push(student);
    renderRosterRows();
  }

  addStudentBtn.addEventListener("click", () => {
    addStudent();
  });

  autoFill5Btn.addEventListener("click", () => {
    fillSampleStudents(5);
  });

  autoFill10Btn.addEventListener("click", () => {
    fillSampleStudents(10);
  });

  function fillSampleStudents(count) {
    state.roster = [];
    nextStudentId = 1;
    const numToFill = Math.min(count, SAMPLE_STUDENT_NAMES.length);

    for (let i = 0; i < numToFill; i++) {
      const sName = SAMPLE_STUDENT_NAMES[i];
      const sampleFile = state.samples.length > 0 ? state.samples[i % state.samples.length].filename : "";
      state.roster.push({
        id: nextStudentId++,
        name: sName,
        type: "sample",
        sampleName: sampleFile,
        file: null,
        thumbUrl: sampleFile ? `/api/samples/${sampleFile}` : ""
      });
    }
    renderRosterRows();
  }

  clearRosterBtn.addEventListener("click", () => {
    state.roster = [];
    renderRosterRows();
    rosterResults.style.display = "none";
  });

  // Evaluate Student Roster & Generate Rankings
  evaluateRosterBtn.addEventListener("click", async () => {
    if (state.roster.length === 0) return;

    evaluateRosterBtn.disabled = true;
    rosterSpinner.style.display = "inline-block";
    rosterBtnText.textContent = "Grading & Ranking Class...";

    try {
      const formData = new FormData();
      formData.append("model_type", state.modelType);
      formData.append("correct_answers_json", JSON.stringify(state.answerKey));
      formData.append("rotation", state.rotation);

      // Build manifest and attach any custom uploaded files
      const manifest = [];
      let uploadFileIndex = 0;

      state.roster.forEach(st => {
        if (st.type === "upload" && st.file) {
          formData.append("files", st.file);
          manifest.push({
            name: st.name,
            type: "upload",
            file_index: uploadFileIndex++
          });
        } else {
          manifest.push({
            name: st.name,
            type: "sample",
            sample_name: st.sampleName
          });
        }
      });

      formData.append("students_manifest", JSON.stringify(manifest));

      const resp = await fetch("/api/evaluate-students", {
        method: "POST",
        body: formData
      });

      if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.detail || "Student evaluation failed");
      }

      const data = await resp.json();
      renderRosterRankings(data);

    } catch (err) {
      alert(`Ranking Error: ${err.message}`);
    } finally {
      evaluateRosterBtn.disabled = false;
      rosterSpinner.style.display = "none";
      rosterBtnText.textContent = "🏆 Evaluate Class & Rank Students";
    }
  });

  function renderRosterRankings(data) {
    rosterResults.style.display = "flex";

    // Summary Cards
    rosterTotalStudents.textContent = data.total_students;
    rosterAvgScore.textContent = `${data.average_score} / 10`;
    rosterAvgPct.textContent = `${data.average_percentage}% Average`;
    rosterHighestScore.textContent = `${data.highest_score} / 10`;
    rosterPassRate.textContent = `${data.pass_rate}%`;
    rosterPassedCount.textContent = `${data.passed_count} / ${data.total_students} Passed`;

    // Render Podium for Top Ranked (Rank 1, 2, 3)
    podiumContainer.innerHTML = "";
    const crowns = ["🥇", "🥈", "🥉"];
    const podiumStyles = ["podium-rank-1", "podium-rank-2", "podium-rank-3"];

    data.top_ranked.forEach((student, idx) => {
      const pCard = document.createElement("div");
      pCard.className = `podium-card ${podiumStyles[idx] || ''}`;

      pCard.innerHTML = `
        <div class="podium-crown">${crowns[idx] || '🏅'}</div>
        <div class="podium-name">${student.student_name}</div>
        <div class="podium-score">${student.total_score} <span style="font-size: 1.1rem; color: var(--text-muted);">/ 10</span></div>
        <span class="podium-grade-pill">${student.letter_grade} (${student.percentage}%)</span>
        <p style="font-size: 0.75rem; color: var(--text-muted); word-break: break-all;">Sheet: ${student.filename}</p>
        ${student.annotated_image ? `<img src="${student.annotated_image}" class="paper-thumb-preview" style="width: 80px; height: 80px; cursor: pointer; border-radius: 6px;" onclick="window.zoomSheet('${student.annotated_image}')" title="Click to view sheet" />` : ''}
      `;
      podiumContainer.appendChild(pCard);
    });

    // Render Bottom Ranked / Needs Attention
    if (data.bottom_ranked && data.bottom_ranked.length > 0 && data.total_students > 1) {
      bottomRankedCard.style.display = "flex";
      bottomRankedList.innerHTML = "";
      data.bottom_ranked.forEach(student => {
        const item = document.createElement("div");
        item.className = "attention-item";
        item.innerHTML = `
          <strong>${student.student_name}</strong>
          <span style="color: var(--accent-rose); font-weight: 700;">Score: ${student.total_score}/10</span>
          <span class="pill pill-false">${student.letter_grade}</span>
        `;
        bottomRankedList.appendChild(item);
      });
    } else {
      bottomRankedCard.style.display = "none";
    }

    // Complete Standings Table
    rosterTableBody.innerHTML = "";
    data.full_roster.forEach(student => {
      const tr = document.createElement("tr");

      let rankBadgeHtml = `<span class="rank-badge rank-normal">#${student.rank}</span>`;
      if (student.rank === 1) rankBadgeHtml = `<span class="rank-badge rank-gold">🥇 1</span>`;
      else if (student.rank === 2) rankBadgeHtml = `<span class="rank-badge rank-silver">🥈 2</span>`;
      else if (student.rank === 3) rankBadgeHtml = `<span class="rank-badge rank-bronze">🥉 3</span>`;

      const statusBadge = student.status === "Pass"
        ? `<span class="status-badge" style="font-size: 0.72rem;">✓ Pass</span>`
        : `<span class="status-badge" style="background: rgba(244, 63, 94, 0.15); color: var(--accent-rose); border-color: rgba(244, 63, 94, 0.3); font-size: 0.72rem;">✗ Remedial</span>`;

      const previewThumbHtml = student.annotated_image
        ? `<img src="${student.annotated_image}" class="paper-thumb-preview" style="cursor: zoom-in;" onclick="window.zoomSheet('${student.annotated_image}')" title="Zoom Sheet" />`
        : `<span style="font-size: 0.75rem; color: var(--text-muted);">${student.filename}</span>`;

      tr.innerHTML = `
        <td>${rankBadgeHtml}</td>
        <td><strong>${student.student_name}</strong></td>
        <td>${previewThumbHtml}</td>
        <td><strong style="font-size: 1.05rem; color: var(--accent-emerald);">${student.total_score}</strong> / ${student.max_score}</td>
        <td>${student.percentage}%</td>
        <td><span class="pill pill-key">${student.letter_grade}</span></td>
        <td>${statusBadge}</td>
      `;
      rosterTableBody.appendChild(tr);
    });

    rosterResults.scrollIntoView({ behavior: "smooth" });
  }

  window.zoomSheet = function(src) {
    modalImg.src = src;
    imageModal.classList.add("open");
  };

  exportStudentsCsvBtn.addEventListener("click", () => {
    window.location.href = "/api/export-students-csv";
  });

  // =========================================================
  // BATCH EVALUATION LOGIC
  // =========================================================
  let batchFilesList = [];
  batchDropzone.addEventListener("click", () => batchFileInput.click());

  batchFileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files.length > 0) {
      batchFilesList = Array.from(e.target.files);
      document.getElementById("batchFileCount").textContent = `${batchFilesList.length} files selected`;
      batchEvaluateBtn.disabled = false;
    }
  });

  batchSampleBtn.addEventListener("click", () => {
    runBatchEvaluation(true);
  });

  batchEvaluateBtn.addEventListener("click", () => {
    runBatchEvaluation(false);
  });

  async function runBatchEvaluation(useSamples = false) {
    batchEvaluateBtn.disabled = true;
    batchSampleBtn.disabled = true;
    batchSpinner.style.display = "inline-block";
    batchBtnText.textContent = "Grading Batch Sheets...";

    try {
      const formData = new FormData();
      formData.append("use_samples", useSamples ? "true" : "false");
      formData.append("model_type", state.modelType);
      formData.append("correct_answers_json", JSON.stringify(state.answerKey));
      formData.append("rotation", state.rotation);

      if (!useSamples) {
        batchFilesList.forEach(file => {
          formData.append("files", file);
        });
      }

      const resp = await fetch("/api/evaluate-batch", {
        method: "POST",
        body: formData
      });

      if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.detail || "Batch evaluation failed");
      }

      const data = await resp.json();
      renderBatchResults(data);

    } catch (err) {
      alert(`Batch Error: ${err.message}`);
    } finally {
      batchEvaluateBtn.disabled = false;
      batchSampleBtn.disabled = false;
      batchSpinner.style.display = "none";
      batchBtnText.textContent = "Evaluate Uploaded Files";
    }
  }

  function renderBatchResults(data) {
    batchResults.style.display = "flex";
    batchTotalSheets.textContent = data.total_sheets;
    batchAvgScore.textContent = `${data.average_score} / ${data.max_score}`;
    batchPassRate.textContent = `${data.pass_rate}%`;
    batchAvgPercent.textContent = `${data.average_percentage}%`;

    batchTableBody.innerHTML = "";
    data.results.forEach((row, idx) => {
      const tr = document.createElement("tr");
      const gradeClass = row.percentage >= 50 ? "mark-correct" : "mark-wrong";

      tr.innerHTML = `
        <td><strong>#${idx + 1}</strong></td>
        <td>${row.filename}</td>
        <td><strong class="${gradeClass}">${row.total_score}</strong> / ${row.max_score}</td>
        <td>${row.percentage}%</td>
        <td><span class="pill pill-key">${row.letter_grade}</span></td>
        <td>${row.model_used}</td>
        <td><span class="status-badge" style="font-size: 0.72rem;">${row.status}</span></td>
      `;
      batchTableBody.appendChild(tr);
    });

    exportCsvBtn.style.display = "inline-flex";
    batchResults.scrollIntoView({ behavior: "smooth" });
  }

  exportCsvBtn.addEventListener("click", () => {
    window.location.href = "/api/export-csv";
  });

  // =========================================================
  // SAMPLE GALLERY LOGIC
  // =========================================================
  async function loadSamples() {
    try {
      const resp = await fetch("/api/samples");
      if (!resp.ok) return;
      const data = await resp.json();
      state.samples = data.samples || [];

      galleryGrid.innerHTML = "";
      state.samples.forEach(sample => {
        const card = document.createElement("div");
        card.className = "gallery-card";
        card.innerHTML = `
          <img class="gallery-thumb" src="${sample.url}" alt="${sample.filename}" loading="lazy" />
          <div class="gallery-info">
            <h4>${sample.filename}</h4>
            <p style="font-size: 0.78rem; color: var(--text-muted);">${sample.size_mb} MB</p>
            <button class="btn-primary btn-test-sample" data-filename="${sample.filename}" style="padding: 0.5rem; font-size: 0.85rem;">
              ⚡ Test This Sheet
            </button>
          </div>
        `;
        galleryGrid.appendChild(card);
      });

      document.querySelectorAll(".btn-test-sample").forEach(btn => {
        btn.addEventListener("click", (e) => {
          const fname = e.target.getAttribute("data-filename");
          selectSampleForEval(fname);
        });
      });

      // Also refresh roster row dropdowns if roster is open
      renderRosterRows();

    } catch (err) {
      console.error("Failed to load samples:", err);
    }
  }

  function selectSampleForEval(filename) {
    state.selectedFile = null;
    state.selectedSampleName = filename;
    state.previewUrl = `/api/samples/${filename}`;

    bannerThumb.src = state.previewUrl;
    bannerThumb.style.transform = `rotate(${state.rotation}deg)`;
    bannerFilename.textContent = filename;
    bannerFilesize.textContent = "Repository Sample • Ready to evaluate";

    dropzone.style.display = "none";
    previewBanner.style.display = "flex";
    evaluateBtn.disabled = false;

    tabButtons[0].click();
    evaluateBtn.click();
  }

  // Initial load
  loadSamples();
});
