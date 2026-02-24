import io
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

# Load the model once
ocr_model = ocr_predictor(pretrained=True)

def extract_text(image_bytes):
    try:
        # Convert bytes to file-like object for docTR
        doc = DocumentFile.from_images(image_bytes)
        result = ocr_model(doc)
        
        extracted_text = ""
        export_data = result.export()
        
        for page in export_data["pages"]:
            for block in page["blocks"]:
                for line in block["lines"]:
                    for word in line["words"]:
                        if word["confidence"] > 0.4:
                            extracted_text += word["value"] + " "
        
        return extracted_text.strip()
    except Exception as e:
        print(f"Vision Error: {e}")
        return ""