# %% 
# init
import datetime
import json
import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")
AZURE_DOCUMENT_API_KEY = os.getenv("AZURE_DOCUMENT_API_KEY")

endpoint = "https://pythondocinteligence.cognitiveservices.azure.com/"

document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(AZURE_DOCUMENT_API_KEY)
)
# %%
# Analyze document

document_url = "https://tudasbazis.kulcs-soft.hu/keszletnyilvantarto/wp-content/uploads/pdf/szamla.pdf"
poller = document_analysis_client.begin_analyze_document_from_url(
    "prebuilt-invoice", document_url)
invoices = poller.result()

# %%
# Extract fields

invoice_data = []

for idx, invoice in enumerate(invoices.documents):
    invoice_info = {
        "InvoiceId": invoice.fields.get("InvoiceId").value if invoice.fields.get("InvoiceId") else None,
        "VendorName": invoice.fields.get("VendorName").value if invoice.fields.get("VendorName") else None,
        "CustomerName": invoice.fields.get("CustomerName").value if invoice.fields.get("CustomerName") else None,
        "PaymentTerm": invoice.fields.get("PaymentTerm").value if invoice.fields.get("PaymentTerm") else None,
        "DueDate": invoice.fields.get("DueDate").value.strftime("%Y-%m-%d") if invoice.fields.get("DueDate").value else None,
        "InvoiceTotal": invoice.fields.get("InvoiceTotal").value.amount if invoice.fields.get("InvoiceTotal") else None,
        "Items": []
    }
    items = invoice.fields.get("Items")
    if items:
        for item in items.value:
            invoice_item = {
                "Description": item.value.get("Description").value if item.value.get("Description") else None,
                "Quantity": item.value.get("Quantity").value if item.value.get("Quantity") else None,
                "Unit": item.value.get("Unit").value if item.value.get("Unit") else None,
                "UnitPrice": item.value.get("UnitPrice").value.amount if item.value.get("UnitPrice") else None,
                "Tax": item.value.get("Tax").value.amount if item.value.get("Tax") else None,
                "Amount": item.value.get("Amount").value.amount if item.value.get("Amount") else None
            }
            invoice_info["Items"].append(invoice_item)
    invoice_data.append(invoice_info)
invoice_data
# %% 
# Save the extracted data to a JSON file

with open('invoice_data.json', 'w',  encoding='utf-8') as json_file:
    json.dump(invoice_data, json_file, indent=4, ensure_ascii=False)
    
# %%
