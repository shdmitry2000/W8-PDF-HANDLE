

# Use an official Ubuntu image as the base image
FROM ubuntu:23.10

# Set environment variables to avoid interaction during installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Update package lists and install necessary packages
# RUN apt-get update && apt-get install -y \
#     software-properties-common \
#     python3.11 \
#     python3.11-dev \
#     python3-pip \
#     && rm -rf /var/lib/apt/lists/*

# Update package lists and install necessary packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    poppler-utils 

# Install Tesseract and its dependencies from the official Tesseract repository
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    # tesseract-ocr-eng \
    tesseract-ocr-all \
    && rm -rf /var/lib/apt/lists/*
RUN rm -rf /usr/lib/python3.11/EXTERNALLY-MANAGED

# Set the working directory inside the container
WORKDIR /fastapi

# Copy your Python script or other project files into the container
COPY . .

# Install Python dependencies (if you have a requirements.txt file)
RUN pip3 install -r requirements.txt

# Make port 8000 and 8501 available to the world outside this container
EXPOSE 8000


# Define environment variable
ENV NAME ubuntu_tesseract_python_w8

# Define the command to run Python from outside the container
# Run FastAPI and Streamlit together when the container launches
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

# CMD  sh -c 'uvicorn api:app --host "0.0.0.0" --port "8000" &&  streamlit run app.py'

# Define the command to run your Python script
# CMD ["python3", "your_script.py"]


