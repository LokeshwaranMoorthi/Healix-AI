import os
from groq import Groq
from pinecone import Pinecone

# --- INITIALIZATION ---
client = Groq(api_key="") # Your key here
pc = Pinecone(api_key="")   # Your Pinecone key
index = pc.Index("healix-medical-rag")

# --- CORE RAG RETRIEVAL FUNCTION ---
def get_pinecone_context(query_text, namespace):
    """Retrieves real medical data from your PDFs."""
    try:
        query_embedding = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=[f"query: {query_text}"],
            parameters={"input_type": "query"}
        )
        vector_data = query_embedding[0].values
        
        results = index.query(
            namespace=namespace,
            vector=vector_data,
            top_k=3,
            include_metadata=True
        )
        
        # Combine the snippets into one context block
        context = "\n".join([match['metadata']['text'] for match in results['matches']])
        return context if context else "No specific data found in medical records."
    except Exception as e:
        return f"Retrieval Error: {e}"

# --- 1. CLINICAL PERSONA (Unified with CIMS Data) ---
def get_medical_analysis(ocr_text):
    # Fetch real drug data from CIMS namespace
    context = get_pinecone_context(ocr_text, "pharmacy-cims")
    
    system_prompt = (
        f"You are Healix AI, a clinical pharmacist expert. \n"

        f"CONTEXT FROM MEDICAL REFERENCE BOOKS:\n{context}\n\n"
        "STRICT SAFETY RULES:\n"
        "1. If you find a direct drug-drug interaction in the context, you MUST include the tag '!!DANGER!!'.\n"
        "2. If no dangerous interactions are found, conclude with 'Safety Status: Stable'.\n\n"

        "Analyze the OCR text using the context above. Respond exactly in this format:\n\n"

        "**Analysis of Clinical Text:**\n\n"

        "1. **Identified Medicines:**\n- List each medicine and map brand to generic.\n\n"

        "2. **Simple Explanation:**\n- How they work based on reference data.\n\n"

        "3. **Critical Safety Warnings:**\n- Mention interactions found in the context.\n\n"

        "4. **Generic Alternatives:**\n- Suggest cost-saving generics.\n\n"

        "**Note:** Always consult with a healthcare professional..."
    )
    return call_groq(system_prompt, ocr_text)

# --- 2. EMPATHETIC COACH (Unified with MSF Guidelines) ---
def get_lab_analysis(ocr_text):
    # Fetch clinical guidelines from MSF namespace
    context = get_pinecone_context(ocr_text, "clinical-msf")
    
    system_prompt = (
        f"Role: Healix Medical Intelligence Engine. \n"
        f"CLINICAL GUIDELINES:\n{context}\n\n"
        "1. Extraction: Biomarkers, Results, Units.\n"
        "2. Evaluation: Categorize [CRITICAL], [ABNORMAL], [OPTIMAL] using guidelines.\n"
        "3. Tone: High-energy, supportive Medical Coach.\n"
        "4. Root Cause: 'Why it matters' and 'Healix Habit'.\n"
        "Output: Motivational greeting, biomarker list, Action Plan."
    )
    return call_groq(system_prompt, ocr_text)

# --- 3. GRANDMA PERSONA (Unified with Patti Remedies) ---
def get_grandma_remedy(symptom):
    # Fetch ancient wisdom from Patti-Remedies namespace
    context = get_pinecone_context(symptom, "patti-remedies")
    
    system_prompt = (
        f"You are Healix Grandma (Patti). \n"
        f"ANCIENT TAMIL WISDOM DATA:\n{context}\n\n"
        "Suggest natural remedies based ON THE CONTEXT PROVIDED. "
        "Tone: Warm, motherly, using 'Kannu'. Explain the ancient wisdom clearly."
    )
    return call_groq(system_prompt, symptom)

def call_groq(system, user_input):
    completion = client.chat.completions.create(
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user_input}],
        model="llama-3.3-70b-versatile",
    )
    return completion.choices[0].message.content
# --- 4. S.O.A.P. SCRIBE (Automated Clinical Documentation) ---
def get_soap_format(clinical_context): # <--- Ensure this name matches
    system_prompt = f"""
    CONTEXT DATA:
    {clinical_context} 

    TASK:
    Generate a professional SOAP note based ONLY on the context provided.
    
    STRICT FORMATTING RULES:
    - Use EXACTLY these headers: 'S:', 'O:', 'A:', 'P:'.
    - Do not use markdown bolding (like **S:**) on the headers.
    - Do not include introductory or concluding remarks.

    S: Summarize patient history and complaints.
    O: List all findings from the lab report (e.g., Malaria POSITIVE, Hb 11.8 g/dL, Platelets 95,000).
    A: Diagnosis based on MSF guidelines (e.g., Uncomplicated P. falciparum Malaria).
    P: Treatment plan based on CIMS (e.g., Artemether-lumefantrine dosage).
    """
    
    # Passing both the prompt and the context to your Groq caller
    return call_groq(system_prompt, clinical_context)

# --- 5. PEER NETWORK LOGIC (Specialist Referral Engine) ---
def get_specialist_suggestion(findings):
    """Analyzes findings to suggest the most relevant specialist."""
    # Context check against MSF clinical paths
    context = get_pinecone_context(findings, "clinical-msf")
    
    system_prompt = (
        f"You are a Chief Medical Officer. Based on the following findings and clinical guidelines:\n{context}\n\n"
        "Identify which specialist the patient should be referred to (e.g., Nephrologist, Cardiologist, etc.).\n"
        "Provide a brief 'Reason for Referral' based on the specific abnormalities found."
    )
    return call_groq(system_prompt, findings)

# --- 6. CLINICAL LOGIC (Differential Diagnosis Engine) ---
def get_clinical_logic_tree(data):
    """Provides evidence-based differential diagnosis."""
    # Deep search in MSF guidelines for diagnostic trees
    logic_context = get_pinecone_context(data, "clinical-msf")
    
    system_prompt = (
        f"You are a Diagnostic Intelligence Engine.\n"
        f"CLINICAL EVIDENCE BASE:\n{logic_context}\n\n"
        "Analyze the patient data and provide:\n"
        "1. Primary Diagnosis: Most likely condition.\n"
        "2. Differential Diagnoses: 3 other possibilities to investigate.\n"
        "3. Red Flags: Symptoms that require immediate ER intervention.\n"
        "Always cite the clinical logic used."
    )
    return call_groq(system_prompt, data)