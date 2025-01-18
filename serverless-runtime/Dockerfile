FROM python:3.9-slim-bullseye

# Install dependencies
RUN apt-get update && apt-get install -y unzip && rm -rf /var/lib/apt/lists/*

# Copy runtime source code
COPY context.py /app/context.py
COPY runtime.py /app/runtime.py
COPY requirements.txt /app/requirements.txt
COPY entrypoint.sh /app/entrypoint.sh

# Ensure the entrypoint script has executable permissions
RUN chmod +x /app/entrypoint.sh

WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set runtime entry point
ENTRYPOINT ["/app/entrypoint.sh"]
