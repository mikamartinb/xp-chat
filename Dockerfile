# Use the official Python image from DockerHub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy only the necessary files to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Kopiere die `key.secret`-Datei
COPY key.secret .

# Expose Streamlit's default port
EXPOSE 8501

# Set the Streamlit configuration to allow access from all IPs
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run the Streamlit app
CMD ["streamlit", "run", "app.py"]