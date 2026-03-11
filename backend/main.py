import asyncio
import io
import json
import zipfile
import shutil
import uuid
import re
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, Response, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

import os
import sys

# ALWAYS Add the 'backend' directory to sys.path first 
# to fix Render root execution ModuleNotFoundErrors.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from automation.portal_scraper import scrape_parameters
from document.doc_generator import generate_document as generate_document_docx
from storage.supabase_loader import get_source_document_path
from supabase import create_client, Client

SUPABASE_URL = "https://kdxtytslsxchjjcckgco.supabase.co"
SUPABASE_KEY = "sb_publishable_0C2D22ybemtor6zOtTlz6w_5kKcd00N"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Exam Parameter Document Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StatusManager:
    def __init__(self):
        self.queues = []

    async def broadcast(self, data: dict):
        msg = json.dumps(data)
        for q in self.queues:
            await q.put(msg)

status_manager = StatusManager()

@app.get("/status")
async def status_stream():
    q = asyncio.Queue()
    status_manager.queues.append(q)

    async def event_generator():
        try:
            while True:
                data = await q.get()
                yield f"data: {data}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            if q in status_manager.queues:
                status_manager.queues.remove(q)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/generate")
async def generate_document(
    portal_url: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        contents = await file.read()
        filename = file.filename.lower()
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(contents))
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            return JSONResponse(status_code=400, content={"status": "error", "message": "Unsupported file format. Please upload a .csv or .xlsx file."})

        required_columns = ["course_name", "module_name", "test_name"]
        for col in required_columns:
            if col not in df.columns:
                return JSONResponse(status_code=400, content={"status": "error", "message": f"Missing required column: {col}"})
                
        if df.empty:
            return JSONResponse(status_code=400, content={"status": "error", "message": "The uploaded file is empty."})

        await status_manager.broadcast({"step": 1, "message": "Connecting to portal..."})
        await asyncio.sleep(0.5)

        await status_manager.broadcast({"step": 2, "message": "Verifying documentation cache..."})
        try:
            # We don't need to store the path since doc_generator calls it internally
            # We just call it here to trigger the cache so the user gets an early error if it fails
            get_source_document_path()
        except FileNotFoundError as e:
            error_msg = {"status": "error", "message": str(e)}
            await status_manager.broadcast(error_msg)
            # We DONT return an error, we let it proceed so parameters are marked "coming soon"
            pass
            
        await asyncio.sleep(0.5)

        generated_files = []

        for index, row in df.iterrows():
            course_name = row["course_name"]
            module_name = row["module_name"]
            test_name = row["test_name"]
            output_filename = row.get("output_filename", f"{module_name}_{test_name}_Params.docx")
            if pd.isna(output_filename) or not str(output_filename).strip():
                output_filename = f"{module_name}_{test_name}_Params.docx"
            output_filename = str(output_filename).strip()
            
            # Sanitize filename to prevent directory traversal crashes (e.g. "React/Redux")
            output_filename = re.sub(r'[\\/*?:"<>|]', '_', output_filename)
                
            if not output_filename.endswith(".docx"):
                output_filename += ".docx"

            await status_manager.broadcast({"step": 3, "message": "Navigating to course..."})
            await asyncio.sleep(0.5)
            
            await status_manager.broadcast({"step": 4, "message": "Finding test..."})
            await asyncio.sleep(0.5)
            
            await status_manager.broadcast({"step": 5, "message": "Reading parameters..."})
            
            scraped_data = await scrape_parameters(portal_url, email, password, course_name, module_name, test_name)

            await status_manager.broadcast({"step": 6, "message": "Building document..."})
            doc_filepath = generate_document_docx(scraped_data, course_name, test_name, output_filename)
            
            with open(doc_filepath, "rb") as f:
                doc_stream = io.BytesIO(f.read())
                
            try:
                os.remove(doc_filepath)
            except Exception:
                pass
            
            generated_files.append((output_filename, doc_stream))

        await status_manager.broadcast({"step": 7, "message": "Done!", "download_ready": True})
        await asyncio.sleep(0.5)

        # Save to a temporary job directory
        job_id = str(uuid.uuid4())
        job_dir = Path("/tmp/neoexam") / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the master docx / zip so the user can download it repeatedly or convert it
        export_filename = "Generated_Documents.zip" if len(generated_files) > 1 else generated_files[0][0]
        export_path = job_dir / export_filename
        
        if len(generated_files) == 1:
            with open(export_path, "wb") as f:
                f.write(generated_files[0][1].getvalue())
        else:
            with zipfile.ZipFile(export_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for out_filename, doc_stream in generated_files:
                    zf.writestr(out_filename, doc_stream.getvalue())
                    
        return JSONResponse(status_code=200, content={
            "status": "success",
            "job_id": job_id,
            "filename": export_filename,
            "is_zip": len(generated_files) > 1
        })
        
    except Exception as e:
        error_msg = {"status": "error", "message": f"Server Error: {str(e)}"}
        await status_manager.broadcast(error_msg)
        return JSONResponse(status_code=500, content=error_msg)

@app.post("/seed")
async def seed_supabase(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        filename = file.filename.lower()
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(contents))
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            return JSONResponse(status_code=400, content={"status": "error", "message": "Only .csv or .xlsx files are supported."})
            
        success_count = 0
        error_count = 0
        
        for _, row in df.iterrows():
            # Check if this row has the minimum required columns to be considered a parameter row
            if "parameter_key" not in row or "display_name" not in row:
                continue
                
            data = {
                "parameter_key": str(row.get("parameter_key", "")).strip(),
                "display_name": str(row.get("display_name", "")).strip(),
                "definition": str(row.get("definition", "")).strip() if pd.notna(row.get("definition")) else "",
                "how_it_works": str(row.get("how_it_works", "")).strip() if pd.notna(row.get("how_it_works")) else "",
                "faq": str(row.get("faq", "")).strip() if pd.notna(row.get("faq")) else ""
            }
            
            # Skip empty keys
            if not data["parameter_key"] or not data["display_name"]:
                continue
                
            try:
                # Upsert to avoid duplicates crashing the import (if parameter_key is unique in DB)
                # Or just simple insert
                supabase.table("parameters").insert(data).execute()
                success_count += 1
            except Exception as e:
                print(f"Failed to insert {data['parameter_key']}: {e}")
                error_count += 1
                
        return {"status": "success", "message": f"Successfully imported {success_count} parameters. ({error_count} errors)"}
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Server Error: {str(e)}"})

@app.get("/api/download/docx/{job_id}")
async def download_docx(job_id: str, filename: str):
    job_dir = Path("/tmp/neoexam") / job_id
    file_path = job_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File expired or not found")
        
    media_type = "application/zip" if filename.endswith(".zip") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return FileResponse(path=file_path, filename=filename, media_type=media_type)

@app.get("/api/download/pdf/{job_id}")
async def download_pdf(job_id: str, filename: str):
    job_dir = Path("/tmp/neoexam") / job_id
    docx_path = job_dir / filename
    
    if not docx_path.exists():
        raise HTTPException(status_code=404, detail="File expired or not found")
        
    if filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Cannot convert a ZIP file directly to PDF. Please generate documents individually.")
        
    pdf_filename = filename.replace(".docx", ".pdf")
    pdf_path = job_dir / pdf_filename
    
    if not pdf_path.exists():
        try:
            from docx2pdf import convert
            # Run docx2pdf in a threadpool to prevent blocking the async event loop
            await asyncio.to_thread(convert, str(docx_path), str(pdf_path))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF Conversion Failed: {str(e)}")
            
    return FileResponse(path=pdf_path, filename=pdf_filename, media_type="application/pdf")

# Serve React frontend LAST
# so API routes take priority
frontend_dist = os.path.join(
    os.path.dirname(__file__),
    "..", "frontend", "dist"
)
if os.path.exists(frontend_dist):
    app.mount(
        "/",
        StaticFiles(
            directory=frontend_dist,
            html=True
        ),
        name="static"
    )
