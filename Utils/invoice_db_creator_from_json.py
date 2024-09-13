# %%

import json
from langchain_community.utilities import SQLDatabase
import sqlite3

merged_json_file_path = r'c:\Data\OneDrive - kryonet.hu\PythonAI\számlák\program\merged_invoices.json'

with open(merged_json_file_path, 'r', encoding='utf-8') as reader:
    data = json.load(reader)

conn = sqlite3.connect('invoices.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Invoices (
    InvoiceId TEXT PRIMARY KEY,
    VendorName TEXT,
    VendorTaxId TEXT,
    CustomerName TEXT,
    CustomerTaxId TEXT,
    PaymentTerm TEXT,
    InvoiceDate TEXT,
    DueDate TEXT,
    SubTotal TEXT,
    TotalTax TEXT,
    InvoiceTotal TEXT,
    Currency TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS InvoiceItems (
    ItemId INTEGER PRIMARY KEY AUTOINCREMENT,
    InvoiceId TEXT,
    Description TEXT,
    Quantity REAL,
    Unit TEXT,
    UnitPrice TEXT,
    TaxRate TEXT,
    Tax TEXT,
    Amount TEXT,
    FOREIGN KEY (InvoiceId) REFERENCES Invoices (InvoiceId)
)
''')

for invoice in data['data']:
    cursor.execute('''
    INSERT INTO Invoices (InvoiceId, VendorName, VendorTaxId, CustomerName, CustomerTaxId, PaymentTerm, InvoiceDate, DueDate, SubTotal, TotalTax, InvoiceTotal, Currency)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        invoice['InvoiceId'], invoice['VendorName'], invoice['VendorTaxId'], invoice['CustomerName'], invoice['CustomerTaxId'],
        invoice['PaymentTerm'], invoice['InvoiceDate'], invoice['DueDate'], invoice['SubTotal'], invoice['TotalTax'], invoice['InvoiceTotal'], invoice['Currency']
    ))

    for item in invoice['Items']:
        cursor.execute('''
        INSERT INTO InvoiceItems (InvoiceId, Description, Quantity, Unit, UnitPrice, TaxRate, Tax, Amount)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            invoice['InvoiceId'], item['Description'], item['Quantity'], item['Unit'], item['UnitPrice'], item['TaxRate'], item['Tax'], item['Amount']
        ))

conn.commit()
conn.close()
# %%

import sqlite3

conn = sqlite3.connect('../data/invoices.db')
cursor = conn.cursor()

cursor.execute('SELECT * FROM Invoices')
invoices = cursor.fetchall()

print("Invoices:")
for invoice in invoices:
    print(invoice)

cursor.execute("""SELECT ItemId, InvoiceId, Description, Quantity, Unit, UnitPrice, TaxRate, Tax, Amount 
FROM InvoiceItems 
WHERE InvoiceId IN (
    SELECT InvoiceId 
    FROM Invoices 
    WHERE CustomerName LIKE '%EcoSoftWare%'
)""")
invoice_items = cursor.fetchall()

print("\nInvoice Items:")
for item in invoice_items:
    print(item)

conn.close()
# %%
