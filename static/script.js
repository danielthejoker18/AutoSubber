const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const filePreview = document.getElementById('filePreview');
const fileNameSpan = document.getElementById('fileName');
const fileSizeSpan = document.getElementById('fileSize');
const removeFileBtn = document.getElementById('removeFile');
const startBtn = document.getElementById('startBtn');
const terminalOutput = document.getElementById('terminalOutput');
const processStatus = document.getElementById('processStatus');
const resultsSection = document.getElementById('resultsSection');

let currentFile = null;
let uploadedFilename = null;

// --- Drag and Drop Logic ---

dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
        handleFileSelect(e.dataTransfer.files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleFileSelect(file) {
    currentFile = file;
    fileNameSpan.textContent = file.name;
    fileSizeSpan.textContent = formatBytes(file.size);

    // Show preview, hide drop prompt
    dropZone.querySelector('.drop-content').style.display = 'none';
    filePreview.style.display = 'flex';

    // Upload immediately or wait? Let's upload immediately for simplicity
    uploadFile(file);
}

removeFileBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    currentFile = null;
    uploadedFilename = null;
    fileInput.value = '';

    // Reset UI
    dropZone.querySelector('.drop-content').style.display = 'block';
    filePreview.style.display = 'none';
    startBtn.disabled = true;
});

function formatBytes(bytes, decimals = 2) {
    if (!+bytes) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

// --- Upload Logic ---

function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    log("Uploading file...", 'system');

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                log(`Upload Error: ${data.error}`, 'error');
                return;
            }
            uploadedFilename = data.filename;
            log(`File uploaded successfully: ${data.filename}`, 'info');
            startBtn.disabled = false;
        })
        .catch(err => {
            log(`Upload Failed: ${err}`, 'error');
        });
}

// --- Log Streaming ---

const eventSource = new EventSource('/stream_logs');
eventSource.onmessage = function (e) {
    if (e.data.includes('PROCESS_COMPLETE')) {
        finishProcess();
    } else {
        log(e.data, 'system');
    }
};

function log(message, type = 'system') {
    const div = document.createElement('div');
    div.className = `log-line ${type}`;
    div.textContent = `> ${message}`;
    terminalOutput.appendChild(div);
    terminalOutput.scrollTop = terminalOutput.scrollHeight;
}

// --- Process Logic ---

startBtn.addEventListener('click', () => {
    if (!uploadedFilename) return;

    const srcLang = document.getElementById('srcLang').value;
    const tgtLang = document.getElementById('tgtLang').value;
    const model = document.getElementById('modelSize').value;

    startBtn.disabled = true;
    processStatus.textContent = "Processing...";
    processStatus.style.color = "#ebb305"; // yellow

    fetch('/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            filename: uploadedFilename,
            src_lang: srcLang,
            tgt_lang: tgtLang,
            model: model
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                log(data.error, 'error');
                startBtn.disabled = false;
            } else {
                log(`Task started! Output video will vary based on input type.`, 'info');
            }
        })
        .catch(err => {
            log(`Request Failed: ${err}`, 'error');
            startBtn.disabled = false;
        });
});

function finishProcess() {
    processStatus.textContent = "Completed";
    processStatus.style.color = "#10b981"; // green

    // Set download links
    const baseName = uploadedFilename.split('_').slice(1).join('_').split('.')[0];

    // Note: The filename from server might be different (uuid prefix), 
    // but the endpoints rely on the output folder content which uses 
    // the UUID prefix (based on app.py logic).
    // Let's rely on the fact that app.py uses the same base name for outputs.

    // Actually, in `app.py`:
    // base_name = os.path.splitext(filename)[0]  <-- This includes UUID
    // output_video_name = f"{base_name}_subbed.mp4"

    const serverBaseName = uploadedFilename.split('.')[0]; // includes UUID

    document.getElementById('dlVideo').href = `/download/${serverBaseName}_subbed.mp4`;
    document.getElementById('dlSrt').href = `/download/${serverBaseName}.srt`;
    document.getElementById('dlTxt').href = `/download/${serverBaseName}.txt`;

    resultsSection.style.display = 'block';
    startBtn.disabled = false;
    startBtn.innerHTML = '<i class="fa-solid fa-rotate-right"></i> Start New';
}
