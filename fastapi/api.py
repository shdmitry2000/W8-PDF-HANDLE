from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pdf2image import convert_from_path
import pdfplumber
import tempfile
import os
import w8tojson 
import subprocess

app = FastAPI()

class ValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)


def file_proccess(pdf_path):
    isfieldsExist=w8tojson.BaseForm.isformwithFields(pdf_path)
    detected_form_type = w8tojson.BaseForm.identify_form_type(pdf_path)
    # if detected_form_type:
    #         print(f"Detected Form Type: {detected_form_type}")

    # Perform actions based on the detected form type
    isOcr="YES"
    if detected_form_type == "W-8BEN":
        # Handle W-8BEN form
        if (isfieldsExist):
            form=w8tojson.W8BENForm(pdf_path)
            isOcr="NO"
        else:
            form=w8tojson.W8BENOCRForm(pdf_path)
        pass
    elif detected_form_type == "W-9":
        # Handle W-9 form
        form=w8tojson.W9Form(pdf_path)
        pass
    elif detected_form_type == "W-8BEN-E":
        # Handle W-8IN form
        if (isfieldsExist):
            form=w8tojson.W8BENEForm(pdf_path)
        else:
            form=w8tojson.W8BENEOCRForm(pdf_path)
        pass
    else:
        raise ValidationError("Could not determine the form type.")
        

    if(form.isvalid()):
            # print(form.getFields(),"\n\n\n")
            return {"validity":"valid","OCR": isOcr,"fields":form.getpdffields()}
            # print(form.getpdffields())
    else:
        return {"validity":"not valid","OCR": isOcr,"fields":form.getpdffields()}
            
      
async def run_docker_command(command: str):
    try:
        # Run the Docker command and capture the output
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout = result.stdout
        stderr = result.stderr

        # Check if the command was successful (return code 0)
        if result.returncode == 0:
            return {"stdout": stdout, "stderr": stderr}
        else:
            return {"error": "Command failed", "stdout": stdout, "stderr": stderr}
    except Exception as e:
        return {"error": str(e)}
    
          
            
@app.post("/process-pdf")
async def process_pdf(pdf_file: UploadFile):
    if pdf_file.content_type != "application/pdf":
        return JSONResponse(content={"error": "Invalid file format"}, status_code=400)

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(pdf_file.file.read())
        
        
    json_out =file_proccess(tmp_file.name)
    os.remove(tmp_file.name)

    # You can process pdf_text and convert it to JSON as needed
    # For simplicity, let's just return the extracted text as a list
    return json_out


@app.post("/process-pdf-in-docker")
async def process_pdf(pdf_file: UploadFile):
    if pdf_file.content_type != "application/pdf":
        return JSONResponse(content={"error": "Invalid file format"}, status_code=400)

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(pdf_file.file.read())
        
        
    json_out =run_docker_command("docker run -v /Users/dmitryshlymovich/workspace/ocr/w8/:/app w8-ubuntu-tesseract-python python3 w8tojson.py /app/"+tmp_file.name)
    os.remove(tmp_file.name)

    # You can process pdf_text and convert it to JSON as needed
    # For simplicity, let's just return the extracted text as a list
    return json_out


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
