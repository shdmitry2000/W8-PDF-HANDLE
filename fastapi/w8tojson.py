
# from PyPDF2 import PdfReader
from fillpdf import fillpdfs
# from pdfrw import PdfReader
import re , sys
import json
# import PyPDF2
# import pdfrw
import re
# import fitz  # PyMuPDF

from enum import Enum
import re
import PyPDF2
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

from abc import ABCMeta, abstractmethod

class FormType(Enum):
    W8BEN = "W-8BEN"
    W9 = "W-9"
    W8IN = "W-8IN"

class BaseForm:
    def __init__(self, form_type,pdf_path):
            self.form_type = form_type
            self.pdf_path=pdf_path
            
    @staticmethod       
    def load_json_structure(class_name):
        json_filename = f"{class_name}.json"
        with open(json_filename, 'r') as json_file:
            return json.load(json_file)
    
    # @abstractmethod()
    # def getFields():
    #     pass
    
    # Define keywords for each form type
    form_keywords = {
        "W-8BEN": ["W-8BEN", "foreign status"],
        "W-9": ["W-9", "Taxpayer Identification Number"],
        "W-8BEN-E": ["W-8BEN-E", "foreign status Company"]
    }
    
    @staticmethod 
    def readpdf_fields(pdf_file_name):
   
        fields=fillpdfs.get_form_fields(pdf_file_name,sort=False)
        # print(fields)
        return fields

    # def has_form_fields(pdf_path):
    #     return readpdf_fields
    @staticmethod  
    def extract_text_from_pdf(pdf_path):
        images = convert_from_path(pdf_path)
        extracted_text = ''

        for img in images:
            img_text = pytesseract.image_to_string(img,config='--psm 12 --oem 3')
            extracted_text += img_text + '\n'

        return extracted_text

    @staticmethod
    def identify_form_type_pic_and_all(pdf_path):
        form_type = None
        extracted_text=BaseForm.extract_text_from_pdf(pdf_path)
        
        for form_name, keywords in BaseForm.form_keywords.items():
            found_all_keywords = all(re.search(keyword, extracted_text, re.IGNORECASE) for keyword in keywords)
            if found_all_keywords:
                form_type = form_name
                break
        
        return form_type
    
    @staticmethod
    def identify_form_type_searchable(pdf_path):
        form_type = None

        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            for page in pdf_reader.pages:
                text = page.extract_text()
                
                # print(text)
                
                for form_name, keywords in BaseForm.form_keywords.items():
                    found_all_keywords = all(re.search(keyword, text, re.IGNORECASE) for keyword in keywords)
                    if found_all_keywords:
                        form_type = form_name
                        break
        
        return form_type
    
    @staticmethod
    def isformwithFields(pdf_path):
        return BaseForm.readpdf_fields(pdf_path)
        
        
        
    @staticmethod
    def identify_form_type(pdf_path):
        if (BaseForm.isformwithFields(pdf_path)):
            return BaseForm.identify_form_type_searchable(pdf_path)
        else:
            return BaseForm.identify_form_type_pic_and_all(pdf_path)
        

    # @staticmethod
    # def readpdf_fields_byPypdf(pdf_file_name):
    #     f = PyPDF2.PdfReader(pdf_file_name)
    #     fields = f.get_fields()
    #     fdfinfo = dict((k, v.get('/V', '')) for k, v in fields.items())
    #     return fdfinfo

    # @staticmethod
    # def readpdf_fields_by_pdfrw(pdf_file_name):
    #     pdf = pdfrw.PdfReader(pdf_file_name)
    #     # print(pdf.keys())
    #     # print(pdf.Info)
    #     # print(pdf.Root.keys())
    #     # field_index=1

    #     all_fields={}
    #     for page in pdf.pages:
    #         annotations = page['/Annots']
    #         if annotations is None:
    #             continue
            
    #         for annotation in annotations:
    #             if annotation['/Subtype']=='/Widget':
    #                 if annotation['/T']:
    #                     key = annotation['/T'].to_unicode()
    #                     value = annotation['/V']
    #                     all_fields[key] = value
                    
    #     return all_fields    
    
    

         
            


class W8BENForm(BaseForm):
    
    def __init__(self,pdf_path):
        super().__init__(FormType.W8BEN,pdf_path)
        self.fields = self.loadFields(pdf_path)
        # print(self.fields)
        
    def loadFields(self,pdf_path):
        return BaseForm.readpdf_fields(pdf_path)

    # Define the JSON structure for W-8BEN form fields
    form_structure =  BaseForm.load_json_structure("W8BENForm")

    
        
    def isvalid(self):
        for field_info in self.form_structure:
            field_identifier = field_info["field_identifier"]
            is_mandatory = field_info["mandatory"]
            validation_type = field_info["validation_type"]

            field_value = self.fields.get(field_identifier)
            if is_mandatory and field_value is None:
                return False
        
            # if field_value is not None:
            #     if validation_type == "text":
            #         if not isinstance(field_value, str) or len(field_value.strip()) == 0:
            #             print(field_identifier,field_value,is_mandatory)
            #             print('false')
            #             return False
            #     elif validation_type == "boolean":
            #         if not isinstance(field_value, bool):
            #             return False
    
        return True

        
    def getpdffields(self):
        # w8ben_json_data = {
        #     self.getw8ben_field_names_mapping().get(identifier, identifier): value
        #     for identifier, value in self.fields.items()
        # }
        # return json.dumps(w8ben_json_data, indent=4)
        mapped_data = {}
    
        for field_info in self.form_structure:
            field_identifier = field_info["field_identifier"]
            field_name = field_info["field_name"]
            
            if field_identifier in self.fields:
                mapped_data[field_name] = self.fields[field_identifier]
        return mapped_data
    
    def getFields(self):
        return self.fields
        

class W8BENOCRForm(BaseForm):
    
    the_fields = {
            "Name of individual who is the beneficial owner": r'Country of citizenship.*?\n.*?\n(.*?\n)', #2
                #r'Country of citizenship\s*(.*)',
            "Country of citizenship": r'Country of citizenship.*?\n(?:.*?\n){3}(.*?\n)',  #  4
            "Permanent Residence Address": r'Permanent residence address .*?\n.*?\n(.*?\n)', #2
            
            
            "city(Permanent residence address)":  r'City or town.*?\n(?:.*?\n){3}(.*?\n)',
            "Country(Permanent residence address)": r'City or town.*?\n(?:.*?\n){5}(.*?\n)', #6
            
            
            "Mailing Address": r'Mailing address .*?\n(?:.*?\n){1}(.*?\n)',
            
            "City(Mailing address)": r'Mailing address .*?\n(?:.*?\n){7}(.*?\n)',
            "Country(Mailing address)": r'Mailing address .*?\n(?:.*?\n){9}(.*?\n)',
    
    
            "U.S. taxpayer identification number (TIN)": r'U.S. taxpayer identification number .*?\n(?:.*?\n){1}(.*?\n)',
            
            "Foreign tax identifying number":r'Foreign tax identifying number .*?\n(?:.*?\n){3}(.*?\n)',
            "Check if FTIN not legally required":r'4\. not supported \s*([\s\S]*?)5\.',
            "Reference number":r'Reference number.*?\n(?:.*?\n){3}(.*?\n)',
                
            "Date of birth": r'Reference number.*?\n(?:.*?\n){5}(.*?\n)',
            "certify that the beneficial owner is a resident of": r'certify that the beneficial owner is a resident of\s+([A-Za-z]+)',
            "Type of beneficial owner": r'Special rates and conditions.*?\n(?:.*?\n){1}(.*?\n)',
            "Percent(Special rates and conditions)": r'(\d+)\s*% rate of withholding on ',
            
            
            "Special rates and conditions":r'rate of withholding on.*?\n(?:.*?\n){1}(.*?\n)',
            "additional conditions":r'eligible for the rate of withholding:(.*?)',
            "f2(Special rates and conditions)":r'4\. not supported \s*([\s\S]*?)5\.',
            "f3":r'4\. not supported \s*([\s\S]*?)5\.',
            "Signature(Signature)":r'4\. not supported \s*([\s\S]*?)5\.',
            "approve(Signature)":r'Sign Here »(.*?)',
            "date(Signature)":r'Sign Here.*?\n(?:.*?\n){1}(.*?\n)',
            "Full name":r'Signature of beneficial owner.*?\n(?:.*?\n){3}(.*?\n)'
        }

    # Define the JSON structure for W-8BEN form fields
    form_structure =  BaseForm.load_json_structure("W8BENForm")


    def __init__(self,pdf_path):
        super().__init__(FormType.W8BEN,pdf_path)
        self.fields = self.loadFields(pdf_path)
        

    def loadFields(self,pdf_path):
        pdf_text=BaseForm.extract_text_from_pdf(pdf_path)
        # Define a dictionary to store extracted values
        extracted_values = {}

        # Define regular expressions for specific fields
        
        for field_info in self.form_structure:
            field_identifier = field_info["field_identifier"]
            field_name = field_info["field_name"]
            pattern=self.the_fields[field_name]
            match = re.search(pattern, pdf_text, re.DOTALL)
            if match:
                extracted_values[field_identifier] = match.group(1).strip()
    
        #     # Iterate through the defined fields and extract values
        # for field, pattern in W8BENOCRForm.the_fields.items():
        #     match = re.search(pattern, pdf_text, re.DOTALL)
        #     if match:
        #         extracted_values[field] = match.group(1).strip()
   
        return extracted_values
    
        
    def isvalid(self):
        for field_info in self.form_structure:
            field_identifier = field_info["field_identifier"]
            is_mandatory = field_info["mandatory"]
            validation_type = field_info["validation_type"]

            field_value = self.fields.get(field_identifier)
            if is_mandatory and field_value is None:
                return False
        
            # if field_value is not None:
            #     if validation_type == "text":
            #         if not isinstance(field_value, str) or len(field_value.strip()) == 0:
            #             print(field_identifier,field_value,is_mandatory)
            #             print('false')
            #             return False
            #     elif validation_type == "boolean":
            #         if not isinstance(field_value, bool):
            #             return False
    
        return True

        
    def getpdffields(self):
        # w8ben_json_data = {
        #     self.getw8ben_field_names_mapping().get(identifier, identifier): value
        #     for identifier, value in self.fields.items()
        # }
        # return json.dumps(w8ben_json_data, indent=4)
        mapped_data = {}
    
        for field_info in self.form_structure:
            field_identifier = field_info["field_identifier"]
            field_name = field_info["field_name"]
            
            if field_identifier in self.fields:
                mapped_data[field_name] = self.fields[field_identifier]
        return mapped_data
    
    def getFields(self):
        return self.fields
        






def cmd_args():
    if len(sys.argv) != 2:
        print("Usage: python w8ben_mapper.py <class_name>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    return pdf_path

if __name__ == "__main__":
    pdf_path = cmd_args()
    # pdf_path='input.pdf'
    # pdf_path='W8_ben.pdf'
    isfieldsExist=BaseForm.isformwithFields(pdf_path)
    detected_form_type = BaseForm.identify_form_type(pdf_path)
    # if detected_form_type:
    #         print(f"Detected Form Type: {detected_form_type}")

    # Perform actions based on the detected form type
    if detected_form_type == "W-8BEN":
        # Handle W-8BEN form
        if (isfieldsExist):
            form=W8BENForm(pdf_path)
        else:
            form=W8BENOCRForm(pdf_path)
        pass
    elif detected_form_type == "W-9":
        # Handle W-9 form
        form=W9Form(pdf_path)
        pass
    elif detected_form_type == "W-8BEN-E":
        # Handle W-8IN form
        if (isfieldsExist):
            form=W8BENEForm(pdf_path)
        else:
            form=W8BENEOCRForm(pdf_path)
        pass
    else:
        print("Could not determine the form type.")
        exit -1

    if(form.isvalid()):
            # print(form.getFields(),"\n\n\n")
            print(form.getpdffields())