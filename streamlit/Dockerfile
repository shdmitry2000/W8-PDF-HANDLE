
# Use an official Python image as the base image
FROM python:3.11-slim


# Set the working directory inside the container
WORKDIR /app

# Copy your Python script or other project files into the container
COPY . .

RUN apt-get update && apt-get install -y poppler-utils

# Install Python dependencies (if you have a requirements.txt file)
RUN pip3 install -r requirements.txt

# Make port 8000 and 8501 available to the world outside this container
EXPOSE 8501

# Define environment variable
ENV NAME UIW8Container

# Define the command to run Python from outside the container
# Run FastAPI and Streamlit together when the container launches
# CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

CMD [ "streamlit", "run", "app.py"]



