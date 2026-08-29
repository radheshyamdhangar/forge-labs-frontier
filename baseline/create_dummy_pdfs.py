"""Create dummy SOP PDFs for testing."""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from pathlib import Path

# Create /idea folder if it doesn't exist
idea_folder = Path(__file__).parent.parent / "idea"
idea_folder.mkdir(exist_ok=True)

# Define styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=16,
    textColor='#003366',
    spaceAfter=12,
    alignment=1  # Center
)
body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['BodyText'],
    fontSize=11,
    spaceAfter=10
)

# 1. KYC SOP
kyc_doc = SimpleDocTemplate(str(idea_folder / "KYC_SOP.pdf"), pagesize=letter)
kyc_content = [
    Paragraph("KYC (Know Your Customer) Standard Operating Procedure", title_style),
    Spacer(1, 0.2*inch),
    
    Paragraph("<b>1. Identity Verification</b>", styles['Heading2']),
    Paragraph("All customers must provide government-issued photo ID. Accepted documents include: Passport, Driver's License, National ID. Verification must be completed within 24 hours of account opening.", body_style),
    
    Paragraph("<b>2. Address Verification</b>", styles['Heading2']),
    Paragraph("Customers must provide proof of current address. Accepted documents include utility bills, bank statements, or official government correspondence dated within last 3 months.", body_style),
    
    Paragraph("<b>3. Income Verification</b>", styles['Heading2']),
    Paragraph("Income verification is required for customers with annual transactions exceeding $50,000. Acceptable documents: Tax returns (last 2 years), salary slips (last 3 months), or bank statements showing regular deposits.", body_style),
    
    Paragraph("<b>4. PEP and Sanctions Screening</b>", styles['Heading2']),
    Paragraph("All customers must be screened against international PEP (Politically Exposed Person) lists and OFAC sanctions lists. Screening must be completed before account approval.", body_style),
    
    Paragraph("<b>5. Risk Assessment</b>", styles['Heading2']),
    Paragraph("Assign risk rating: Low, Medium, High. High-risk customers require additional monitoring and approval from compliance officer.", body_style),
]
kyc_doc.build(kyc_content)
print("✓ Created KYC_SOP.pdf")

# 2. Insurance Claim SOP
insurance_doc = SimpleDocTemplate(str(idea_folder / "Insurance_Claim_SOP.pdf"), pagesize=letter)
insurance_content = [
    Paragraph("Insurance Claim Processing Standard Operating Procedure", title_style),
    Spacer(1, 0.2*inch),
    
    Paragraph("<b>1. Claim Submission</b>", styles['Heading2']),
    Paragraph("Claims must be submitted within 30 days of incident occurrence. Required documents: Claim form (completed), incident report, photos of damage. Exceptions require manager approval.", body_style),
    
    Paragraph("<b>2. Initial Assessment</b>", styles['Heading2']),
    Paragraph("Upon receipt, claims are logged and assigned claim number. Initial assessment completed within 2 business days. If claim appears straightforward, approval issued within 5 business days.", body_style),
    
    Paragraph("<b>3. Document Review</b>", styles['Heading2']),
    Paragraph("All submitted documents verified for authenticity. Medical claims require doctor's certificate. Property damage claims require third-party assessment. Incomplete documentation requires customer follow-up.", body_style),
    
    Paragraph("<b>4. Claim Limits</b>", styles['Heading2']),
    Paragraph("Standard coverage limit is $100,000 per incident. Maximum 3 claims per policy year. Claims exceeding limit require policy review and potential denial.", body_style),
    
    Paragraph("<b>5. Payment Processing</b>", styles['Heading2']),
    Paragraph("Approved claims processed within 10 business days via bank transfer or check. Emergency claims (hospitalization) processed within 24 hours. All payments require 2-signature authorization.", body_style),
]
insurance_doc.build(insurance_content)
print("✓ Created Insurance_Claim_SOP.pdf")

# 3. Loan SOP
loan_doc = SimpleDocTemplate(str(idea_folder / "Loan_SOP.pdf"), pagesize=letter)
loan_content = [
    Paragraph("Loan Processing Standard Operating Procedure", title_style),
    Spacer(1, 0.2*inch),
    
    Paragraph("<b>1. Loan Application</b>", styles['Heading2']),
    Paragraph("Customers submit completed loan application with personal and financial information. Required documents: Income proof (last 6 months), bank statements (last 12 months), employment letter, identification documents.", body_style),
    
    Paragraph("<b>2. Credit Check</b>", styles['Heading2']),
    Paragraph("Credit score minimum 650 for unsecured loans. Minimum credit score 500 for secured loans. Customers with credit score below 500 are automatically rejected.", body_style),
    
    Paragraph("<b>3. Loan Limits</b>", styles['Heading2']),
    Paragraph("Maximum loan amount is 5x annual verified income. Minimum loan amount $5,000. Maximum loan term is 10 years. Interest rates range from 5% to 15% based on credit score and collateral.", body_style),
    
    Paragraph("<b>4. Approval Decision</b>", styles['Heading2']),
    Paragraph("Loans under $50,000 approved by loan officer. Loans between $50,000-$250,000 require manager approval. Loans exceeding $250,000 require director and board approval. Decision issued within 5 business days.", body_style),
    
    Paragraph("<b>5. Disbursement</b>", styles['Heading2']),
    Paragraph("Upon approval, funds disbursed within 2 business days. First payment due 30 days after disbursement. Missed payment incurs 5% penalty. Default after 90 days triggers recovery process.", body_style),
]
loan_doc.build(loan_content)
print("✓ Created Loan_SOP.pdf")

print(f"\n✅ All dummy PDFs created in: {idea_folder}")
