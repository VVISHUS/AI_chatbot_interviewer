import os
import pymupdf  # PyMuPDF
import docx


class parser():
    def __init__(self, store_in_db: bool = False):
        self.store_db = store_in_db
    
    def extract_text_from_pdf(self, pdf_path):
        text = ""
        try:
            with pymupdf.open(pdf_path) as doc:
                for page in doc:
                    text += page.get_text()
        except Exception as e:
            print(f"❌ Error reading PDF {pdf_path}: {e}")
        return text

    def extract_text_from_docx(self, docx_path):
        text = ""
        try:
            doc = docx.Document(docx_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print(f"❌ Error reading DOCX {docx_path}: {e}")
        return text

    def extract_text(self, doc_path):
        if doc_path.endswith(".pdf"):
            return self.extract_text_from_pdf(doc_path)
        elif doc_path.endswith(".docx"):
            return self.extract_text_from_docx(doc_path)
        else:
            raise ValueError("Unsupported file type. Only .pdf and .docx are supported.")
        
    def extract_add_doc_text(self, add_doc_path):
        if add_doc_path.endswith(".pdf"):
            return self.extract_text_from_pdf(add_doc_path)
        elif add_doc_path.endswith(".docx"):
            return self.extract_text_from_docx(add_doc_path)
        else:
            raise ValueError("Unsupported file type. Only .pdf and .docx are supported.")

# if __name__ == "__main__":
#     parser=parser()
#     content = parser.extract_text(doc_path="G:/scripts/PG-AGI/hiring-assistant-chatbot/submissions/resumes/VAIBHAV_SINGH_5dbc5831-cea0-4c22-b30a-29d2300c8254_resume.pdf")
#     print("\n📄 Extracted Content:\n")
#     print(content[:2000] + "...\n" if len(content) > 2000 else content)
