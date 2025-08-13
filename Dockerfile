# Use an official Python runtime as a parent image
FROM python:3.13-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . .

# Set the PYTHONPATH to include the src directory
ENV PYTHONPATH=/app/src

# Expose the port the app runs on
EXPOSE 10000

# Run the uvicorn server when the container launches
CMD ["uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "10000"]
