# %%
# import json
from datetime import datetime
from typing import List, Tuple
from langchain_core.tools import tool
import json 


@tool(response_format="content_and_artifact")
def extract_invoice_ids_tool(start_date: str, end_date:str) -> Tuple[str, List[str]]:
    """Get invoice id list (comma separated values) of invoices where the Invoice Date is between start_date and end_date. Date format: YYYY-MM-DD"""
    merged_json_file_path = r'c:\Data\OneDrive - kryonet.hu\PythonAI\számlák\program\merged_invoices.json'
    with open(merged_json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    invoice_ids = [
        invoice['InvoiceId']
        for invoice in data['data']
        if invoice['InvoiceDate'] and start_date <= datetime.strptime(invoice['InvoiceDate'], "%Y-%m-%d") <= end_date
    ]

    return ",".join(invoice_ids), invoice_ids

tools = [extract_invoice_ids_tool]
tools_by_name = { tool.name : tool for tool in tools}
# %%
