# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy project files
COPY requirements.txt pyproject.toml ./
COPY src ./src

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Expose Streamlit default port
EXPOSE 8501

# Set environment variables for Streamlit
ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true

# Set environment variables for Azure Document Intelligence
ENV DOCUMENTINTELLIGENCE_ENDPOINT=""
ENV DOCUMENTINTELLIGENCE_API_KEY=""

# Run Streamlit app
CMD ["streamlit", "run", "src/app.py"]