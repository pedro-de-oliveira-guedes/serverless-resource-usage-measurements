#!/bin/bash
base64 -d /app/serverless_function.zip.b64 > /app/serverless_function.zip
unzip /app/serverless_function.zip -d /app
python /app/runtime.py
