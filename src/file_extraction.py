import fitz
import docx 

def extract_file_text(file_path):
    with open(file_path, "r") as file:
        text = file.read()
        return text

def extract_file_word(file_path):
    doc = docx.Document(file_path)
    final_text = ""

    for paragraph in doc.paragraphs:
        final_text += paragraph.text + "\n"

    return final_text


def extract_file_pdf(file_path):
    file = fitz.open(file_path)
    full_text = ""
    for page_num in range(len(file)):
        page = file.load_page(page_num)
        full_text += page.get_text()
    file.close()
    return full_text
            
