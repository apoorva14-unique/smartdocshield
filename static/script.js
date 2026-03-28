// 🔐 CHECK LOGIN
async function checkLogin() {
    try {
        const res = await fetch("/check-auth", {
            credentials: "include"
        });

        const data = await res.json();

        if (!data.loggedIn) {
            window.location.href = "/";
        }

    } catch (err) {
        console.log("Auth check failed");
        window.location.href = "/";
    }
}

checkLogin();

let chart;
let maskedTextGlobal = "";
let downloadURL = "";

// ---------------- FILE HANDLING ----------------
const fileInput = document.getElementById('fileInput');
const fileNameDisplay = document.getElementById('fileName');
const dropZone = document.getElementById('dropZone');
const browseBtn = document.getElementById('browseBtn');
const vaultList = document.getElementById('vaultList');
const emptyMsg = document.getElementById('emptyMsg');

browseBtn.addEventListener("click", () => fileInput.click());

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(event => {
    dropZone.addEventListener(event, e => {
        e.preventDefault();
        e.stopPropagation();
    });
});

dropZone.addEventListener('dragover', () => dropZone.classList.add('dragover'));
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));

dropZone.addEventListener('drop', (e) => {
    dropZone.classList.remove('dragover');
    fileInput.files = e.dataTransfer.files;
    updateFileName();
});

fileInput.addEventListener('change', updateFileName);

function updateFileName() {
    if (fileInput.files.length > 0) {
        fileNameDisplay.innerText = "Selected: " + fileInput.files[0].name;
    } else {
        fileNameDisplay.innerText = "No file selected";
    }
}

// ---------------- UPLOAD ----------------
document.getElementById('uploadBtn').addEventListener('click', async () => {

    const resultArea = document.getElementById('resultArea');
    const outputText = document.getElementById('outputText');
    const loading = document.getElementById('loading');

    if (!fileInput.files.length) {
        alert("Please select a file first.");
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    resultArea.style.display = 'block';
    loading.style.display = 'block';
    outputText.innerText = '';

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
            credentials: "include"
        });

        if (!response.ok) {
            throw new Error("Server error: " + response.status);
        }

        const data = await response.json();
        loading.style.display = 'none';

        if (data && data.masked_text) {

            maskedTextGlobal = data.masked_text;
            downloadURL = data.download_url;

            const risk = data.risk || "LOW";
            const fileType = data.file_type ? data.file_type.toUpperCase() : "UNKNOWN";

            let riskColor = "#22c55e";
            if (risk === "MEDIUM") riskColor = "#f59e0b";
            if (risk === "HIGH") riskColor = "#ef4444";

            const piiSummary = `
Aadhaar: ${data.pii?.aadhaar?.length || 0}  
PAN: ${data.pii?.pan?.length || 0}  
Bank: ${data.pii?.bank?.length || 0}  
Card: ${data.pii?.card?.length || 0}  
DOB: ${data.pii?.dob?.length || 0}
`;

            outputText.innerHTML = `
🔥 <b>Risk Level:</b> <span style="color:${riskColor}">${risk}</span>

📂 <b>File Type:</b> ${fileType}

📊 <b>PII Summary:</b>
${piiSummary}

📄 <b>Protected Text:</b>
${highlightMasked(data.masked_text)}

🧠 <b>AI Detection:</b>
👤 Names: ${data.ai?.names?.join(", ") || "None"}

🔍 <b>Detected PII:</b>

Aadhaar: ${data.pii?.aadhaar?.join(", ") || "None"}  
PAN: ${data.pii?.pan?.join(", ") || "None"}  
Card: ${data.pii?.card?.join(", ") || "None"}  
Bank: ${data.pii?.bank?.join(", ") || "None"}  
DOB: ${data.pii?.dob?.join(", ") || "None"}
            `;

            renderChart(data.pii);
            addToVault(fileInput.files[0].name, data.download_url);

        } else {
            outputText.innerText = "❌ Error: " + (data.error || "Processing failed");
        }

    } catch (error) {
        loading.style.display = 'none';
        console.error(error);

        outputText.innerText = "❌ Error: Backend not responding / crashed";
    }
});

// ---------------- CHART ----------------
function renderChart(pii) {

    const data = {
        labels: ["Aadhaar", "PAN", "Bank", "Card"],
        datasets: [{
            label: "Detected Sensitive Data",
            data: [
                pii?.aadhaar?.length || 0,
                pii?.pan?.length || 0,
                pii?.bank?.length || 0,
                pii?.card?.length || 0
            ]
        }]
    };

    if (chart) chart.destroy();

    chart = new Chart(document.getElementById("piiChart"), {
        type: "bar",
        data: data
    });
}

// ---------------- VAULT ----------------
function addToVault(name, url) {

    if (emptyMsg) emptyMsg.remove();

    const fileItem = document.createElement('div');
    fileItem.className = 'file-item';

    fileItem.innerHTML = `
        <span>📄 ${name}</span>
        <button onclick="openFile('${url}')">Open</button>
    `;

    vaultList.prepend(fileItem);
}

function openFile(url) {
    window.open(url, "_blank");
}

// ---------------- HIGHLIGHT ----------------
function highlightMasked(text) {

    text = text.replace(/XXXX/g,
        '<span style="background:red;color:white;">XXXX</span>'
    );

    text = text.replace(/XXXXX[A-Z0-9]{5}/g,
        '<span style="background:purple;color:white;">$&</span>'
    );

    return text;
}

// ---------------- COPY ----------------
function copyResult() {
    if (!maskedTextGlobal) return alert("No text to copy!");
    navigator.clipboard.writeText(maskedTextGlobal);
    alert("Copied!");
}

// ---------------- DOWNLOAD ----------------
function downloadResult() {
    if (!downloadURL) return alert("No file available!");
    window.location.href = downloadURL;
}

// ---------------- LOGOUT ----------------
async function logout() {
    await fetch("/logout", {
        credentials: "include"
    });

    window.location.href = "/";
}