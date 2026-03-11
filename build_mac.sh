#!/bin/bash
pyinstaller \
  --onefile \
  --name ExamParamsApp \
  --add-data "data:data" \
  --add-data "backend:backend" \
  --hidden-import uvicorn \
  --hidden-import fastapi \
  --hidden-import lxml.etree \
  --hidden-import docx \
  --hidden-import supabase \
  --hidden-import playwright \
  backend/main.py
