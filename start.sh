#!/bin/bash
apt-get update && apt-get install -y ffmpeg
pip install --no-cache-dir openai-whisper
uvicorn main:app --host=0.0.0.0 --port=$PORT
