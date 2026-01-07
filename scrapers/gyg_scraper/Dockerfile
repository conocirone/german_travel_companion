# Use the official Python Playwright image
# This includes Python, Node, and the browser binaries pre-installed.
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Copy requirements and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install the browsers (Chromium is usually enough)
RUN playwright install chromium

# Copy the scraper script
COPY scraper.py .

# Command to run the scraper
CMD ["python", "scraper.py"]