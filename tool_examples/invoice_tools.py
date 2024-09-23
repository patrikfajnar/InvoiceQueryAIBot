from datetime import datetime
from typing import List, Tuple, Dict
from langchain_core.tools import tool
from pydantic import BaseModel
from dal.invoice_database import Invoice, get_new_session

class InvoiceIdsResponse(BaseModel):
    invoice_ids: List[str]
    
@tool
def extract_invoice_ids_tool(start_date: str, end_date:str) -> InvoiceIdsResponse:
    """Get invoice id list of invoices where the Invoice Date is between start_date and end_date. Date format: YYYY-MM-DD"""
    session = get_new_session()
    
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    invoice_ids = session.query(Invoice.InvoiceId).filter(
        Invoice.InvoiceDate.between(start_date, end_date)
    ).all()

    invoice_ids = [invoice_id[0] for invoice_id in invoice_ids]

    session.close()
    return InvoiceIdsResponse(invoice_ids=invoice_ids)

class InvoiceTotalsResponse(BaseModel):
    invoice_totals: Dict[str, str]

@tool()
def get_invoice_totals(invoice_ids: list[str]) -> InvoiceTotalsResponse:
    """Get the total amounts (the currency is Ft) for the given invoice IDs."""
    session = get_new_session()
    invoices = session.query(Invoice).with_entities(Invoice.InvoiceId, Invoice.InvoiceTotal).filter(Invoice.InvoiceId.in_(invoice_ids)).all()
    result = {invoice.InvoiceId: invoice.InvoiceTotal for invoice in invoices}
    session.close()
    return InvoiceTotalsResponse(invoice_totals=result)

invoice_tools_list = [extract_invoice_ids_tool, get_invoice_totals]
tools_by_name = { tool.name : tool for tool in invoice_tools_list}


print(get_invoice_totals.invoke({"invoice_ids": ["KE23/52095"]}))