import os
import re
from docx import Document

def extract_docs_from_word(filepath):
    """
    Parses a Word document uploaded by user to extract definitions, feature info,
    how it works, and FAQs.
    Uses regex and structural document parsing to guess parameter blocks.
    """
    db = {}
    if not os.path.exists(filepath):
        return db
        
    try:
        doc = Document(filepath)
        current_param = None
        current_section = None
        
        # Simple heuristic: bold text or specific headings might denote a parameter
        # In a real scenario, LLM extraction or strict template matching works best.
        # This acts as a naive structural parser.
        
        for p in doc.paragraphs:
            text = p.text.strip()
            if not text:
                continue
                
            lower_text = text.lower()
            
            # Identify keywords to switch context
            if "definition" in lower_text and len(text) < 30:
                current_section = "definition"
                continue
            elif "how it works" in lower_text and len(text) < 30:
                current_section = "how_it_works"
                continue
            elif "faq" in lower_text and len(text) < 30:
                current_section = "faq"
                continue
            
            # If a paragraph is short, capitalized, or bolded heavily, treat as new parameter key
            is_bold = any(run.bold for run in p.runs)
            if is_bold and len(text) < 60 and not current_section:
                current_param = text
                current_section = None
                db[current_param] = {
                    "definition": "",
                    "how_it_works": "",
                    "faq": ""
                }
                continue
                
            if current_param and current_section:
                db[current_param][current_section] += f"{text}\n"
                
    except Exception as e:
        print(f"Error parsing word doc: {e}")
        
    return db
