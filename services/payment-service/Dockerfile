# Use a lightweight Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies directly
RUN pip install fastapi uvicorn requests

# Copy the application code
COPY main.py .

# Create the logs directory inside the container
RUN mkdir -p /app/shared-logs

# Expose the port
EXPOSE 8080

# Run the application
CMD ["python", "main.py"]