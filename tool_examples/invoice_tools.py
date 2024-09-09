# %%
# import json
from datetime import datetime
from typing import List, Tuple, Dict
from langchain_core.tools import tool
from pydantic import BaseModel
import json 

merged_json_file_path = r'c:\Data\OneDrive - kryonet.hu\PythonAI\számlák\program\merged_invoices.json'

class InvoiceIdsResponse(BaseModel):
    invoice_ids: List[str]
    

@tool
def extract_invoice_ids_tool(start_date: str, end_date:str) -> InvoiceIdsResponse:
    """Get invoice id list of invoices where the Invoice Date is between start_date and end_date. Date format: YYYY-MM-DD"""
    with open(merged_json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    invoice_ids = [
        invoice['InvoiceId']
        for invoice in data['data']
        if invoice['InvoiceDate'] and start_date <= datetime.strptime(invoice['InvoiceDate'], "%Y-%m-%d") <= end_date
    ]

    return InvoiceIdsResponse(invoice_ids=invoice_ids)

class InvoiceTotalsResponse(BaseModel):
    invoice_totals: Dict[str, str]  # Dictionary of invoice_id -> total

@tool()
def get_invoice_totals(invoice_ids: str) -> InvoiceTotalsResponse:
    """Get the total amounts (the currency is Ft) for the given invoice IDs."""

    with open(merged_json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)["data"]

    result = {}
    for invoice in data:
        if invoice["InvoiceId"] in invoice_ids:
            result[invoice["InvoiceId"]] = invoice["InvoiceTotal"]
    
    return InvoiceTotalsResponse(invoice_totals=result)

invoice_tools_list = [extract_invoice_ids_tool, get_invoice_totals]
tools_by_name = { tool.name : tool for tool in invoice_tools_list}
# %%
