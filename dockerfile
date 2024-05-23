# Use the official Python image as base
FROM python:3.8-slim

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Install required system dependencies
RUN apt-get update \
    && apt-get install -y gcc freetds-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install Flask and required packages
RUN pip install --no-cache-dir Flask pymssql

# Expose the port Flask runs on
EXPOSE 5000

# Command to run the Flask application
CMD ["flask", "run"]
