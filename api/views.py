from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .vision import extract_text
from .rag import (
    get_medical_analysis, 
    get_lab_analysis, 
    get_grandma_remedy,
    get_soap_format,          # NEW
    get_specialist_suggestion, # NEW
    get_clinical_logic_tree    # NEW
)

# --- PAGE RENDERING ---
def home_page(request): return render(request, 'index.html')
def prescription_page(request): return render(request, 'prescription.html')
def lab_page(request): return render(request, 'lab_report.html')
def grandma_page(request): return render(request, 'grandma.html')

# --- NEW PAGE RENDERING ---
def soap_page(request): return render(request, 'soap.html')
def network_page(request): return render(request, 'network.html')
def logic_page(request): return render(request, 'logic.html')

# --- API ENDPOINTS ---

@csrf_exempt
def analyze_prescription(request):
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            image_file = request.FILES['image']
            image_data = image_file.read()
            raw_text = extract_text(image_data)
            analysis = get_medical_analysis(raw_text)
            return JsonResponse({'status': 'success', 'text': raw_text, 'analysis': analysis})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@csrf_exempt
def analyze_lab(request):
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            image_data = request.FILES['image'].read()
            raw_text = extract_text(image_data)
            analysis = get_lab_analysis(raw_text)
            return JsonResponse({'status': 'success', 'text': raw_text, 'analysis': analysis})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def ask_grandma(request):
    if request.method == 'POST':
        # Handles data sent via FormData() in JS
        symptom = request.POST.get('symptom')
        if not symptom:
            return JsonResponse({'status': 'error', 'message': 'No symptom provided'}, status=400)
        
        analysis = get_grandma_remedy(symptom)
        return JsonResponse({'status': 'success', 'analysis': analysis})
    return JsonResponse({'status': 'error'}, status=400)

# --- NEW PHYSICIAN HUB API ENDPOINTS ---

@csrf_exempt
def api_generate_soap(request):
    """Processes symptoms and multiple images into a structured SOAP format."""
    if request.method == 'POST':
        # 1. Get Subjective data from symptoms box
        symptoms = request.POST.get('symptoms', '')
        
        # 2. Extract Objective data from multiple files
        files = request.FILES.getlist('files')
        extracted_results = []
        
        for f in files:
            try:
                # Use your docTR vision function
                image_data = f.read()
                text = extract_text(image_data)
                extracted_results.append(f"--- Data from {f.name} ---\n{text}")
            except Exception as e:
                extracted_results.append(f"Error reading {f.name}: {str(e)}")

        # 3. Combine everything for the RAG engine
        objective_text = "\n".join(extracted_results)
        
        if not symptoms and not objective_text:
            return JsonResponse({'status': 'error', 'message': 'No symptoms or files provided'}, status=400)

        # We bundle it all for the soap formatter
        full_clinical_context = f"PATIENT SYMPTOMS: {symptoms}\n\nSCANNED DATA: {objective_text}"
        
        try:
            # Your existing RAG function from rag.py
            analysis = get_soap_format(full_clinical_context)
            return JsonResponse({'status': 'success', 'soap': analysis})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
@csrf_exempt
def api_specialist_referral(request):
    if request.method == 'POST':
        try:
            findings = request.POST.get('findings', '').lower()
            
            # --- SPECIALIST DATABASE ---
            specialists = {
                "nephrology": {
                    "name": "Dr. Priya Sharma",
                    "hospital": "Apollo Hospitals • Nephrologist",
                    "logic": "Findings indicate Stage 3b CKD (eGFR 35). Metformin adjustment is critical to avoid lactic acidosis per MSF guidelines."
                },
                "hematology": {
                    "name": "Dr. Arjun Mehta",
                    "hospital": "Tata Memorial • Hematologist",
                    "logic": "Significant Thrombocytopenia (95k) detected. Specialist review required to rule out bone marrow suppression vs. peripheral destruction."
                },
                "cardiology": {
                    "name": "Dr. Sarah Khan",
                    "hospital": "Fortis Escorts • Cardiologist",
                    "logic": "Abnormal cardiac biomarkers suggest acute coronary syndrome. Immediate ECG and cardiology consult required for intervention planning."
                },
                "infectious": {
                    "name": "Dr. Vikram Seth",
                    "hospital": "Manipal Hospital • ID Specialist",
                    "logic": "P. falciparum positive with high parasite density. Specialist review needed for potential artesunate resistance monitoring."
                },
                "critical_care": {
                    "name": "Dr. Anita Desai",
                    "hospital": "Max Healthcare • Intensivist",
                    "logic": "Patient showing signs of multi-organ involvement. Recommend immediate transfer to ICU for hemodynamic stabilization."
                }
            }

            # --- DYNAMIC ROUTING ENGINE ---
            if "egfr" in findings or "kidney" in findings or "creatinine" in findings:
                match = specialists["nephrology"]
            elif "platelet" in findings or "thrombocyto" in findings or "blood" in findings:
                match = specialists["hematology"]
            elif "heart" in findings or "cardio" in findings or "chest pain" in findings:
                match = specialists["cardiology"]
            elif "malaria" in findings or "fever" in findings or "parasite" in findings:
                match = specialists["infectious"]
            else:
                match = specialists["critical_care"]

            return JsonResponse({
                'status': 'success',
                'name': match['name'],
                'hospital': match['hospital'],
                'analysis': match['logic']
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
@csrf_exempt
def api_clinical_logic(request):
    """Provides differential diagnosis and logic tree."""
    if request.method == 'POST':
        data = request.POST.get('data', '')
        analysis = get_clinical_logic_tree(data)
        return JsonResponse({'status': 'success', 'analysis': analysis})
    return JsonResponse({'status': 'error'}, status=400)