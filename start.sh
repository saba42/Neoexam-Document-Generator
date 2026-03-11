#!/usr/bin/env bash
export PLAYWRIGHT_BROWSERS_PATH=0
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
