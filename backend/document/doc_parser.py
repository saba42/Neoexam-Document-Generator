import os
import re
from docx import Document

def normalize(text):
    text = text.strip().rstrip(":")
    text = text.replace("&", "and")
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = re.sub(r'\s+', ' ', text)
    return text.lower()

def find_param_data(db, checked_name):
    norm = normalize(checked_name)
    for cat in db:
        for key in db[cat]:
            norm_key = normalize(key)
            # Exact match
            if norm == norm_key:
                return db[cat][key]
            # One contains the other
            if norm in norm_key or norm_key in norm:
                return db[cat][key]
            # Word overlap >= 60%
            w1 = set(norm.split())
            w2 = set(norm_key.split())
            overlap = len(w1 & w2)
            total = len(w1 | w2)
            if total > 0 and overlap/total >= 0.6:
                return db[cat][key]
    return None

def parse_source_document(filepath):
    """
    Parses the Word document containing parameters grouped under 7 categories.
    Returns a dictionary of categories -> parameters -> details.
    """
    db = {}
    if not os.path.exists(filepath):
        return db
        
    try:
        doc = Document(filepath)
        
        categories = [
            "Test Control & Restrictions - Basic",
            "Results Control",
            "Programming Question Options",
            "Test Control & Restrictions - Advanced",
            "Manual Evaluation",
            "Choice based questions",
            "Section score cutoff restrictions"
        ]
        cat_lower_map = {c.lower(): c for c in categories}
        
        current_cat = None
        current_param = None
        current_mode = None # "description" or "faqs"
        current_q = None
        current_a_lines = []
        current_a_blocks = [] # for inline images in faqs
        
        def save_current_faq():
            nonlocal current_q, current_a_lines, current_cat, current_param, current_a_blocks
            if current_cat and current_param and current_q:
                ans = "\n".join(current_a_lines).strip()
                db[current_cat][current_param]["faqs"].append({
                    "question": current_q,
                    "answer": ans,
                    "answer_blocks": current_a_blocks
                })
            current_q = None
            current_a_lines = []
            current_a_blocks = []

        def get_images_from_para(p):
            imgs = []
            for r in p.runs:
                # Check modern drawing nodes
                drawings = r._element.xpath('.//w:drawing')
                for drawing in drawings:
                    blips = drawing.xpath('.//a:blip')
                    for blip in blips:
                        rId = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                        if rId and rId in doc.part.related_parts:
                            imgs.append(doc.part.related_parts[rId].blob)
                            
                # Check legacy VML pict nodes
                picts = r._element.xpath('.//w:pict')
                for pict in picts:
                    imagedatas = pict.xpath('.//v:imagedata')
                    for idata in imagedatas:
                        rId = idata.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                        if rId and rId in doc.part.related_parts:
                            imgs.append(doc.part.related_parts[rId].blob)
            return imgs

        # Reconstruct into logical lines tracking exact bold runs
        raw_lines = []

        for p in doc.paragraphs:

            def get_run_imgs(run):
                imgs = []
                for elem in run._element.iter():
                    try:
                        from lxml import etree
                        local = etree.QName(elem.tag).localname
                    except:
                        continue
                    if local == 'blip':
                        for attr, val in elem.attrib.items():
                            if 'embed' in attr:
                                if val in doc.part.related_parts:
                                    imgs.append(
                                        doc.part.related_parts[val].blob
                                    )
                return imgs

            has_any = bool(p.text.strip())
            if not has_any:
                for run in p.runs:
                    if get_run_imgs(run):
                        has_any = True
                        break
            if not has_any:
                continue

            current_text = ""
            current_bold = False
            current_imgs = []

            def flush_line():
                t = current_text.strip()
                if t or current_imgs:
                    raw_lines.append(
                        (t, current_bold, list(current_imgs))
                    )

            def reset_line():
                nonlocal current_text
                nonlocal current_bold
                nonlocal current_imgs
                current_text = ""
                current_bold = False
                current_imgs = []

            for run in p.runs:
                run_bold = run.bold is True
                run_imgs = get_run_imgs(run)
                run_text = run.text
                parts = run_text.split('\n')

                for idx, part in enumerate(parts):
                    if idx > 0:
                        flush_line()
                        reset_line()
                    if part.strip():
                        current_text += part
                        if run_bold:
                            current_bold = True
                    if run_imgs:
                        current_imgs.extend(run_imgs)
                        run_imgs = []

            flush_line()
            reset_line()

        for text, is_bold, imgs in raw_lines:
            lower_text = text.lower().replace("–", "-").replace("—", "-")
            
            # Check Category
            matched_cat = None
            for cl in cat_lower_map:
                if cl in lower_text and len(lower_text) < len(cl) + 10:
                    matched_cat = cat_lower_map[cl]
                    break
                    
            if matched_cat:
                save_current_faq()
                
                current_cat = matched_cat
                if current_cat not in db:
                    db[current_cat] = {}
                
                current_param = current_cat
                current_mode = "description"
                
                if current_param not in db[current_cat]:
                    db[current_cat][current_param] = {
                        "description": "",
                        "description_blocks": [],
                        "faqs": []
                    }
                
                continue
                
            if current_cat:
                if lower_text == "faqs" or lower_text == "faqs:":
                    current_mode = "faqs"
                    save_current_faq()
                    continue
                
                q_match = re.match(r'^q\d+', text, re.IGNORECASE)
                
                if current_mode == "faqs" and q_match:
                    save_current_faq()
                    current_q = text
                    continue
                    
                is_admin_student_label = lower_text.strip() in ["admin side", "student side", "admin side:", "student side:", "note:", "example:"]
                
                if is_admin_student_label:
                    # Treat these as part of description if they happen
                    if current_mode == "description" and current_param:
                        db[current_cat][current_param]["description"] += "\n" + text
                        db[current_cat][current_param]["description_blocks"].append({"type": "text", "content": text})
                        for img in imgs:
                            db[current_cat][current_param]["description_blocks"].append({"type": "image", "blob": img})
                    continue

                if is_bold and len(text) < 150 and not lower_text.startswith("description") and not lower_text.startswith("solution") and not q_match and not is_admin_student_label:
                    # New feature header detected
                    save_current_faq()
                    current_q = None
                    current_a_lines = []
                    current_a_blocks = []
                    
                    current_param = text

                    # Sanitize parameter name
                    current_param = current_param.replace(":", "").strip()
                    
                    current_mode = "description"
                    # Initialize ONLY IF NOT EXISTS to prevent overwriting same parameters
                    if current_param not in db[current_cat]:
                        db[current_cat][current_param] = {
                            "description": "",
                            "description_blocks": [],
                            "faqs": []
                        }
                    
                    # If this header line also contains images inline, save them!
                    for img in imgs:
                        db[current_cat][current_param]["description_blocks"].append({"type": "image", "blob": img})
                    continue
                    
                if current_mode == "faqs" and current_q is not None:
                    if text:
                        current_a_lines.append(text)
                        current_a_blocks.append({"type": "text", "content": text})
                    for img in imgs:
                        current_a_blocks.append({"type": "image", "blob": img})
                    continue
                    
                if current_param and current_mode == "description":
                    if lower_text.startswith("description:"):
                        text = text[len("description:"):].strip()
                        if not text and not imgs:
                            continue
                    
                    if db[current_cat][current_param]["description"]:
                        db[current_cat][current_param]["description"] += "\n" + text
                    else:
                        db[current_cat][current_param]["description"] = text
                        
                    if text:
                        db[current_cat][current_param]["description_blocks"].append({"type": "text", "content": text})
                        
                    for img in imgs:
                        db[current_cat][current_param]["description_blocks"].append({"type": "image", "blob": img})
                    
        save_current_faq()

    except Exception as e:
        import traceback
        traceback.print_exc()
        
    return db
