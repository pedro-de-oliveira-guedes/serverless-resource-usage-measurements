FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y unzip && rm -rf /var/lib/apt/lists/*

# Copy runtime source code
COPY context.py /app/context.py
COPY runtime.py /app/runtime.py
COPY requirements.txt /app/requirements.txt

WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set runtime entry point
CMD ["python", "runtime.py"]
