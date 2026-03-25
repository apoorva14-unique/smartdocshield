// 🔐 LOGIN CHECK
if (!localStorage.getItem("loggedIn")) {
    window.location.href = "login.html";
}

const fileInput = document.getElementById('fileInput');
const fileNameDisplay = document.getElementById('fileName');
const dropZone = document.getElementById('dropZone');
const browseBtn = document.getElementById('browseBtn');
const vaultList = document.getElementById('vaultList');
const emptyMsg = document.getElementById('emptyMsg');

let maskedTextGlobal = "";
let downloadURL = "";
let chart;

// ---------------- Browse ----------------
browseBtn.addEventListener("click", () => {
    fileInput.click();
});

// ---------------- Drag & Drop ----------------
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

// ---------------- File ----------------
fileInput.addEventListener('change', updateFileName);

function updateFileName() {
    if (fileInput.files.length > 0) {
        fileNameDisplay.innerText = "Selected: " + fileInput.files[0].name;
    } else {
        fileNameDisplay.innerText = "No file selected";
    }
}

// ---------------- Vault ----------------
function addToVault(name) {
    if (emptyMsg) emptyMsg.remove();

    const fileItem = document.createElement('div');
    fileItem.className = 'file-item';
    fileItem.innerHTML = `<span>📄 ${name.split('.')[0]}_Masked</span>`;
    vaultList.prepend(fileItem);
}

// ---------------- Upload ----------------
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
        const response = await fetch('http://127.0.0.1:5000/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        loading.style.display = 'none';

        if (data.masked_text) {

            maskedTextGlobal = data.masked_text;
            downloadURL = data.download_url;

            let riskColor = "#22c55e";
            if (data.risk === "MEDIUM") riskColor = "#f59e0b";
            if (data.risk === "HIGH") riskColor = "#ef4444";

            const docType = classifyDocument(data.masked_text);

            const piiSummary = `
Aadhaar: ${data.pii.aadhaar.length}  
PAN: ${data.pii.pan.length}  
Phone: ${data.pii.phone.length}  
DOB: ${data.pii.dob.length}  
Email: ${data.pii.email.length}
            `;

            outputText.innerHTML = `
🔥 <b>Risk Level:</b> <span style="color:${riskColor}">${data.risk}</span>

📂 <b>File Type:</b> ${data.file_type.toUpperCase()}

📑 <b>Document Type:</b> ${docType}

📊 <b>PII Summary:</b>
${piiSummary}

📄 <b>Protected Text:</b>
${highlightMasked(data.masked_text)}

🧠 <b>AI Detection:</b>
👤 Names: ${data.ai?.names?.join(", ") || "None"}
📍 Locations: ${data.ai?.locations?.join(", ") || "None"}

🔍 <b>Detected PII:</b>
${JSON.stringify(data.pii, null, 2)}
            `;

            // ✅ CHART UPDATE
            renderChart(data.pii);

            addToVault(fileInput.files[0].name);

        } else {
            outputText.innerText = "❌ Error: " + (data.error || "Unknown error");
        }

    } catch (error) {
        loading.style.display = 'none';
        outputText.innerText = "❌ Backend not connected.";
    }
});

// ---------------- Chart ----------------
function renderChart(pii) {

    const data = {
        labels: ["Aadhaar", "PAN", "Phone", "DOB", "Email"],
        datasets: [{
            label: "Detected Count",
            data: [
                pii.aadhaar.length,
                pii.pan.length,
                pii.phone.length,
                pii.dob.length,
                pii.email.length
            ]
        }]
    };

    if (chart) chart.destroy();

    chart = new Chart(document.getElementById("piiChart"), {
        type: "bar",
        data: data
    });
}

// ---------------- Highlight ----------------
function highlightMasked(text) {

    text = text.replace(/XXXX/g,
        '<span style="background:red;color:white;">XXXX</span>'
    );

    text = text.replace(/XXXXX[A-Z0-9]{5}/g,
        '<span style="background:purple;color:white;">$&</span>'
    );

    return text;
}

// ---------------- Classifier ----------------
function classifyDocument(text) {

    const t = text.toUpperCase();

    if (t.includes("AADHAAR") || t.includes("UIDAI"))
        return "Aadhaar Card";

    if (t.includes("INCOME TAX") || t.includes("PERMANENT ACCOUNT"))
        return "PAN Card";

    return "General Document";
}

// ---------------- Copy ----------------
function copyResult() {
    if (!maskedTextGlobal) return alert("No text to copy!");
    navigator.clipboard.writeText(maskedTextGlobal);
    alert("Copied!");
}

// ---------------- Download ----------------
function downloadResult() {
    if (!downloadURL) return alert("No file available!");
    window.location.href = downloadURL;
}