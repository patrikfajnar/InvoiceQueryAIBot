# %% 
# init
import json
import os
from azure.ai.formrecognizer import DocumentAnalysisClient, AnalyzeResult
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from typing import Any, Dict
import re


load_dotenv(dotenv_path=".env")
AZURE_DOCUMENT_API_KEY = os.getenv("AZURE_DOCUMENT_API_KEY")

endpoint = "https://pythondocinteligence.cognitiveservices.azure.com/"

document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(AZURE_DOCUMENT_API_KEY)
)

def analyze_document(path: str) -> AnalyzeResult:
    with open(path, "rb") as f:
        poller = document_analysis_client.begin_analyze_document("prebuilt-invoice", document=f, locale="hu")
    return poller.result()

def extract_num(content : str) -> float:
    return re.sub(r'[^0-9,]', '', content)

def extract_fields(result: AnalyzeResult) -> Dict[str, Any]:
    idx, invoice = next(enumerate(result.documents))
    getter = invoice.fields.get
    invoice_info = {
        "InvoiceId": getter("InvoiceId").value if getter("InvoiceId") else None,
        "VendorName": invoice.fields.get("VendorName").value if invoice.fields.get("VendorName") else None,
        "VendorTaxId" : invoice.fields.get("VendorTaxId").value if invoice.fields.get("VendorTaxId") else None,
        "CustomerName": invoice.fields.get("CustomerName").value if invoice.fields.get("CustomerName") else None,
        "CustomerTaxId": invoice.fields.get("CustomerTaxId").value if invoice.fields.get("CustomerTaxId") else None,
        "PaymentTerm": invoice.fields.get("PaymentTerm").value if invoice.fields.get("PaymentTerm") else None,
        "InvoiceDate" : invoice.fields.get("InvoiceDate").value.strftime("%Y-%m-%d") if invoice.fields.get("InvoiceDate") else None,
        "DueDate": invoice.fields.get("DueDate").value.strftime("%Y-%m-%d") if invoice.fields.get("DueDate") else None,
        "SubTotal": extract_num(invoice.fields.get("SubTotal").content) if invoice.fields.get("SubTotal") else None,
        "TotalTax": extract_num(invoice.fields.get("TotalTax").content) if invoice.fields.get("TotalTax") else None,
        "InvoiceTotal": extract_num(invoice.fields.get("InvoiceTotal").content) if invoice.fields.get("InvoiceTotal") else None,
        "Currency": invoice.fields.get("InvoiceTotal").value.code if invoice.fields.get("InvoiceTotal") else None,
        "Items": []
    }
    items = invoice.fields.get("Items")
    if items:
        for item in items.value:
            invoice_item = {
                "Description": item.value.get("Description").value if item.value.get("Description") else None,
                "Quantity": item.value.get("Quantity").value if item.value.get("Quantity") else None,
                "Unit": item.value.get("Unit").value if item.value.get("Unit") else None,
                "UnitPrice": extract_num(item.value.get("UnitPrice").content) if item.value.get("UnitPrice") else None,
                "TaxRate": item.value.get("TaxRate").value if item.value.get("TaxRate") else None,
                "Tax": extract_num(item.value.get("Tax").content) if item.value.get("Tax") else None,
                "Amount": extract_num(item.value.get("Amount").content) if item.value.get("Amount") else None
            }
            invoice_info["Items"].append(invoice_item)
    return invoice_info

def write_to_file(invoice_info: Dict[str, Any], folder: str):
    filename = (f"{invoice_info["InvoiceDate"]}_{invoice_info["VendorName"]}_{invoice_info['InvoiceId']}.json")
    invalid_filename_chars = r'[<>:"/\\|?*\n\t\r\a\b\f\v]'
    sanitized_filename = re.sub(invalid_filename_chars, '', filename)
    with open(os.path.join(folder, sanitized_filename), 'w',  encoding='utf-8') as json_file:
        json.dump(invoice_info, json_file, indent=4, ensure_ascii=False)

# %% 
# Extract one file

result = analyze_document(r"C:\Data\OneDrive - kryonet.hu\PythonAI\számlák\számla\11_PDFsam_2024_01.pdf")
invoice_info = extract_fields(result)
write_to_file(invoice_info, r'C:\Data\OneDrive - kryonet.hu\PythonAI\számlák\program\json')

# %%
# Extract multiple pdf from dir

base_dir = r"C:\Data\OneDrive - kryonet.hu\PythonAI\számlák\program"
to_process_dir = os.path.join(base_dir, "toprocess")
processed_dir = os.path.join(base_dir, "processed")
json_dir = os.path.join(base_dir, "json")

pdf_files = []
num_files = 3

for filename in os.listdir(to_process_dir)[:num_files]:
    if filename.endswith(".pdf"):
        pdf_files.append(os.path.join(to_process_dir, filename))

for path in pdf_files:
    result = analyze_document(path)
    invoice_info = extract_fields(result)   
    write_to_file(invoice_info, json_dir)
    destination_path = os.path.join(processed_dir, os.path.basename(path))
    os.rename(path, destination_path)
    print(f'moved: {path}')

# %%
