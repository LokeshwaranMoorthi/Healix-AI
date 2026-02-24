import os
from pinecone import Pinecone
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. Configuration
PINECONE_API_KEY = "pcsk_785cdJ_G5xa4e91oc31wKNtWvWho5gi64VQeZmzUfie93uYnNhHgiR3NHez198y66p6aZr"
INDEX_NAME = "healix-medical-rag"

print("--- Initializing Pinecone Connection ---")
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

def ingest_document(file_path, namespace):
    if not os.path.exists(file_path):
        print(f"❌ ERROR: File not found at {file_path}")
        return

    print(f"\n📖 Reading PDF: {file_path}...")
    loader = PyPDFLoader(file_path)
    data = loader.load()
    
    # 800 chars ensures we don't exceed the E5 model's token limit
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    docs = text_splitter.split_documents(data)
    print(f"✂️ Split into {len(docs)} chunks.")

    records = []
    for i, doc in enumerate(docs):
        # FLAT STRUCTURE: No nested 'metadata' dictionary.
        # Everything is a top-level field for upsert_records.
        records.append({
            "id": f"{namespace}-{i}",
            "text": doc.page_content, 
            "source": os.path.basename(file_path),
            "page": str(doc.metadata.get("page", 0)) # Must be a string
        })

    # Upload in batches
    batch_size = 50
    print(f"☁️ Uploading to Pinecone (Namespace: {namespace})...")
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        try:
            # This triggers the automatic embedding generation
            index.upsert_records(namespace=namespace, records=batch)
            print(f"✅ {namespace}: {min(i + batch_size, len(records))}/{len(records)} uploaded")
        except Exception as e:
            print(f"❌ Batch failed: {e}")

if __name__ == "__main__":
    print("\n--- Healix AI Final Ingestion Pipeline ---")
    
    # Add your files here
    files = [
        ("data/pdfcoffee.com_ciims-india-drug-reference-bookpdf-pdf-free.pdf", "pharmacy-cims"),
        ("data/guideline-170-en.pdf", "clinical-msf"),
        ("data/dli.rmrl.000299.pdf", "patti-remedies")
    ]
    
    for path, ns in files:
        ingest_document(path, ns)
        
    print("\n🏁 PIPELINE FINISHED. Your data is now properly embedded.")