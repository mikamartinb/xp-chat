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

# Copy the `key.secret` file
COPY key.secret .

# Expose port 5001 (mapped to the server's URL)
EXPOSE 5001

# Set the Streamlit configuration to use port 5001
ENV STREAMLIT_SERVER_PORT=5001 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=5001"]