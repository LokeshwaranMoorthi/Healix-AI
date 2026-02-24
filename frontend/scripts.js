let analysisResultText = "";
const synth = window.speechSynthesis;

// 1. VOICE ENGINE
function initVoices() { synth.getVoices(); }
initVoices();
if (synth.onvoiceschanged !== undefined) synth.onvoiceschanged = initVoices;

function speakResults(text) {
    if (!text) return;
    synth.cancel();
    const cleanText = text.replace(/[*#!!]/g, ''); 
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 0.95;
    const voices = synth.getVoices();
    const indianVoice = voices.find(v => v.lang.includes('en-IN')) || voices[0];
    if (indianVoice) utterance.voice = indianVoice;
    synth.speak(utterance);
}

// 2. DOM INITIALIZATION
document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');

    if (dropZone && fileInput) {
        dropZone.onclick = (e) => { if (e.target !== fileInput) fileInput.click(); };
        fileInput.onchange = (e) => {
            if (e.target.files.length > 0) {
                const fileNameDisplay = document.getElementById('file-name');
                if (fileNameDisplay) fileNameDisplay.innerText = "Selected: " + e.target.files[0].name;
            }
        };
    }
});

// 3. UPGRADED PRESCRIPTION ANALYZER
async function analyzePrescription() {
    const fileInput = document.getElementById('file-input');
    const btn = document.getElementById('analyze-btn');
    const panel = document.getElementById('insights-panel');
    const content = document.getElementById('analysis-content');
    
    if (!fileInput || !fileInput.files[0]) return alert("Please upload an image!");

    btn.disabled = true;
    btn.innerText = "Healix is interpreting...";

    const formData = new FormData();
    formData.append('image', fileInput.files[0]);

    try {
        const response = await fetch('/api/analyze/', { 
            method: 'POST', 
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        const data = await response.json();
        
        if(data.status === 'success') {
            analysisResultText = data.analysis;
            const ocrText = data.text || "";

            // --- THE VISUAL FEEDBACK LOGIC (INLINE FORCE FIX) ---
            const riskCard = document.getElementById('risk-card');
            const riskText = document.getElementById('risk-text');
            const riskLabel = document.getElementById('risk-label');
            
            const isHigh = analysisResultText.includes("!!DANGER!!");

            if (riskCard && riskText) {
                if (isHigh) {
                    riskCard.style.backgroundColor = "#fee2e2"; 
                    riskCard.style.border = "3px solid #ef4444";
                    riskCard.style.animation = "pulse-red 1.5s infinite";
                    if(riskLabel) { riskLabel.innerText = "CRITICAL WARNING"; riskLabel.style.color = "#b91c1c"; }
                    riskText.innerText = "HIGH RISK";
                    riskText.style.color = "#991b1b";
                } else {
                    riskCard.style.backgroundColor = "#f0fdf4"; 
                    riskCard.style.border = "3px solid #22c55e";
                    riskCard.style.animation = "none"; 
                    if(riskLabel) { riskLabel.innerText = "SAFETY STATUS"; riskLabel.style.color = "#16a34a"; }
                    riskText.innerText = "STABLE";
                    riskText.style.color = "#15803d";
                }
            }

            // --- DIETARY & ORDERING ---
            const takeList = document.getElementById('foods-take');
            const avoidList = document.getElementById('foods-avoid');
            if (takeList) takeList.innerHTML = "<li>Water (Hydration)</li><li>Probiotic Yogurt</li><li>Vitamin-C fruits</li>";
            if (avoidList) avoidList.innerHTML = "<li>Alcohol (Strict)</li><li>Oily Foods</li><li>Caffeine</li>";

            const linksContainer = document.getElementById('medicine-links');
            const orderSection = document.getElementById('order-section');
            const knownMeds = ["Dolo", "Crocin", "Okacet", "Pan 40", "Cetirizine", "Paracetamol", "Amoxicillin", "Pantoprazole", "Azithromycin", "Atorvastatin", "Montelukast","Betaloc", "Cimetidine", "Oxprenolol", "Dorzolamide"];
            let found = false;
            
            if (linksContainer) {
                linksContainer.innerHTML = "";
                knownMeds.forEach(med => {
                    if (analysisResultText.toLowerCase().includes(med.toLowerCase()) || ocrText.toLowerCase().includes(med.toLowerCase())) {
                        found = true;
                        linksContainer.innerHTML += `<a href="https://pharmeasy.in/search/all?name=${med}" target="_blank" class="bg-white border border-indigo-200 px-3 py-2 rounded-xl text-xs font-bold text-indigo-600 hover:bg-indigo-50 transition-all">Buy ${med}</a>`;
                    }
                });
            }
            if (found && orderSection) orderSection.classList.remove('hidden');

            content.innerHTML = `<div class="prose prose-indigo max-w-none">${analysisResultText.replace(/\n/g, '<br>')}</div>`;
            panel.classList.remove('hidden');
            btn.innerText = "Analysis Complete ✅";
            speakResults(analysisResultText);
        }
    } catch (err) {
        btn.innerText = "Error - Try Again";
    } finally {
        btn.disabled = false;
    }
}

// 4. LAB BUDDY (UPGRADED: FIXED DISPLAY & UI RESET)
async function analyzeLabReport() {
    const fileInput = document.getElementById('file-input');
    const btn = document.getElementById('analyze-btn');
    const panel = document.getElementById('insights-panel');
    const content = document.getElementById('analysis-content'); 
    
    // Prescription-specific UI elements to hide for Lab reports
    const orderSection = document.getElementById('order-section');
    const riskCard = document.getElementById('risk-card');
    
    if (!fileInput || !fileInput.files[0]) return alert("Upload your lab report!");

    btn.disabled = true;
    btn.innerText = "Healix is checking biomarkers...";

    const formData = new FormData();
    formData.append('image', fileInput.files[0]);

    try {
        const response = await fetch('/api/analyze-lab/', { 
            method: 'POST', 
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        const data = await response.json();
        
        if (data.status === 'success' || data.analysis) {
            analysisResultText = data.analysis;
            
            if (content) {
                const timestamp = new Date().toLocaleString();
                content.innerHTML = `
                    <div style="margin-bottom: 20px; padding: 10px; background: #f0fdf4; border-left: 4px solid #10b981; font-size: 0.8rem; color: #065f46;">
                        <b>HEALIX AI LAB ANALYSIS VERIFIED</b><br>
                        Source: MSF Guidelines & CIMS Reference | ${timestamp}
                    </div>
                    <div class="prose prose-emerald max-w-none">${analysisResultText.replace(/\n/g, '<br>')}</div>
                `;
            }

            // UI Cleanup: Hide ordering and reset risk to stable for labs
            if (orderSection) orderSection.classList.add('hidden');
            if (riskCard) {
                riskCard.style.backgroundColor = "#f0fdf4"; 
                riskCard.style.border = "2px solid #22c55e";
                riskCard.style.animation = "none";
                document.getElementById('risk-text').innerText = "STABLE";
                document.getElementById('risk-text').style.color = "#15803d";
            }

            panel.classList.remove('hidden');
            btn.innerText = "Report Decoded ✅";
            speakResults(analysisResultText);
        }
    } catch (err) {
        btn.innerText = "Error - Try Again";
    } finally {
        btn.disabled = false;
    }
}

// 5. GRANDMA'S HOME
async function askGrandma() {
    const symptomInput = document.getElementById('symptom-input');
    const responsePanel = document.getElementById('patti-response');
    const pattiVoice = document.getElementById('patti-voice');
    
    if (!symptomInput || !symptomInput.value) return alert("Tell Grandma what's wrong!");

    const formData = new FormData();
    formData.append('symptom', symptomInput.value);

    try {
        const response = await fetch('/api/ask-grandma/', { 
            method: 'POST', 
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        const data = await response.json();
        
        if (pattiVoice) {
            pattiVoice.innerHTML = `<div class="prose max-w-none text-slate-700">${data.analysis.replace(/\n/g, '<br>')}</div>`;
        }
        
        responsePanel.classList.remove('hidden');
        speakResults(data.analysis);
    } catch (err) {
        alert("Grandma is busy right now!");
    }
}

// 6. PDF DOWNLOADER (STRICT VERSION)
function downloadPDF() {
    const element = document.getElementById('insights-panel');
    
    if (!element) {
        alert("Report not found!");
        return;
    }

    // Ensure library is ready
    if (typeof html2pdf === 'undefined') {
        alert("PDF Library is still loading. Please wait 2 seconds and try again.");
        return;
    }

    const opt = {
        margin:       10,
        filename:     'Healix_Lab_Report.pdf',
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2, useCORS: true, letterRendering: true },
        jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    // Use a small delay to ensure the UI has finished rendering the AI response
    setTimeout(() => {
        html2pdf().set(opt).from(element).save();
    }, 500);
}