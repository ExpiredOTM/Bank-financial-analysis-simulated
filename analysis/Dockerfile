FROM python:3.11-slim

# Set working directory

WORKDIR /app

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . /app

# Default command
CMD ["python", "analysis/05_integrated_risk_dashboard.py"] 