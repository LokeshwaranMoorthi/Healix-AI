from pinecone import Pinecone

pc = Pinecone(api_key="pcsk_785cdJ_G5xa4e91oc31wKNtWvWho5gi64VQeZmzUfie93uYnNhHgiR3NHez198y66p6aZr")
index = pc.Index("healix-medical-rag")

def medical_ask(query_text, namespace="patti-remedies"):
    print(f"\n👵 Consulting Grandma's Remedies [{namespace}] for: '{query_text}'...")
    
    try:
        # 1. Manual Embedding (The reliable way)
        query_embedding = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=[f"query: {query_text}"],
            parameters={"input_type": "query"}
        )
        vector_data = query_embedding[0].values

        # 2. Querying the specific Grandma's namespace
        results = index.query(
            namespace=namespace,
            vector=vector_data,
            top_k=3,
            include_metadata=True
        )
        
        matches = results.get('matches', [])
        if not matches:
            print("❌ Grandma doesn't have a remedy for that one.")
            return

        print(f"✅ Found {len(matches)} traditional suggestions:")
        for match in matches:
            meta = match.get('metadata', {})
            print(f"\n🌿 Remedy Confidence: {match['score']:.4f}")
            print(f"📖 Instruction: {meta.get('text', 'N/A')[:500]}...")
            print(f"📄 Source: {meta.get('source', 'N/A')}")
            print("-" * 50)

    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    # Common traditional remedy search
    medical_ask("remedy for cough and cold using ginger or tulsi")