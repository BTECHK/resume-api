# Use the official Python 3.11 slim image as a parent image.
# "Slim" images are smaller than the full images, containing only the minimal packages needed to run Python.
FROM python:3.11-slim

# Set the working directory in the container to /app.
# This is where the application code will live and where subsequent commands will run.
WORKDIR /app

# Copy the requirements.txt file into the container at /app.
# This file lists all the Python dependencies needed for the application.
COPY requirements.txt .

# Install the Python dependencies specified in requirements.txt.
# --no-cache-dir disables the pip cache to keep the image size smaller.
# -r specifies the requirements file to use.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the 'api' directory from the host to the container's /app/api directory.
# This directory contains the main FastAPI application source code.
COPY ./api ./api

# Copy the SQLite database file into the container.
# This ensures the application has access to its data.
COPY ./data/analytics.db ./data/analytics.db

# Expose port 8080.
# This informs Docker that the container listens on this network port at runtime.
# It's a documentation/metadata instruction; it doesn't actually publish the port.
# Cloud Run requires applications to listen on port 8080.
EXPOSE 8080

# Define the command to run the application using uvicorn.
# This will be executed when the container starts.
# 'uvicorn': The ASGI server.
# 'api.main:app': The path to the FastAPI application instance ('app' object in 'api/main.py').
# '--host 0.0.0.0': Makes the server accessible from outside the container.
# '--port 8080': The port the server will listen on, matching the EXPOSE instruction.
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
