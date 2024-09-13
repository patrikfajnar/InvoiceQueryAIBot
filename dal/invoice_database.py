from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, DeclarativeBase

class Base(DeclarativeBase):
    pass

class Invoice(Base):
    __tablename__ = 'Invoices'
    InvoiceId = Column(String, primary_key=True)
    VendorName = Column(String)
    VendorTaxId = Column(String)
    CustomerName = Column(String)
    CustomerTaxId = Column(String)
    PaymentTerm = Column(String)
    InvoiceDate = Column(String)
    DueDate = Column(String)
    SubTotal = Column(String)
    TotalTax = Column(String)
    InvoiceTotal = Column(String)
    Currency = Column(String)
    items = relationship("InvoiceItem", back_populates="invoice")

class InvoiceItem(Base):
    __tablename__ = 'InvoiceItems'
    ItemId = Column(Integer, primary_key=True, autoincrement=True)
    InvoiceId = Column(String, ForeignKey('Invoices.InvoiceId'))
    Description = Column(String)
    Quantity = Column(Float)
    Unit = Column(String)
    UnitPrice = Column(String)
    TaxRate = Column(String)
    Tax = Column(String)
    Amount = Column(String)
    invoice = relationship("Invoice", back_populates="items")

engine = create_engine('sqlite:///c:\\Data\\Pr\\AI\\InvoiceQueryAIBot\\InvoiceQueryAIBot\\data\\invoices.db')
Session = sessionmaker(bind=engine)

def get_new_session():
    return Session()