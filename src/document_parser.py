from pathlib import Path
from file_extraction import extract_file_pdf, extract_file_text, extract_file_word
#function to process text 
def process_text(text):
    text = text.strip()
    if text == " ":
        raise ValueError("text cannot be empty")
    return (text)

#function to process uploaded files
def process_file(file_path):
    path = Path(file_path)
    allowed_extenions = {".txt", ".pdf", ".docx"}
    extension = path.suffix 
    if extension in allowed_extenions:
        if extension == ".pdf":
            return extract_file_pdf(file_path)
        elif extension == ".txt":
            return extract_file_text(file_path)
        elif extension == ".docx":
            return extract_file_word(file_path)
        
    else:
        raise ValueError('invalid fle uploaded')    

    
print(process_text("    testng    white spaces     c"))
print(process_text("  hello  "))

