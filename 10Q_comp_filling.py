import pdfplumber
import re
import json

def extract_company_info(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()
    
    # Extract company name (Assuming it's near 'Exact name of registrant')
    company_name_match = re.search(r"(\n|^)\s*(.*?)\n\(Exact name of registrant", text, re.IGNORECASE)
    company_name = company_name_match.group(2).strip() if company_name_match else "Not Found"
    
    # Extract filing date (Assuming it's near 'For the quarterly period ended')
    filing_date_match = re.search(r"For the quarterly period ended\s+([A-Za-z]+ \d{1,2}, \d{4})", text)
    filing_date = filing_date_match.group(1).strip() if filing_date_match else "Not Found"
    
    return {"company_name": company_name, "filing_date": filing_date}

# Example usage
pdf_path = "SandPGlobal-2Q-2024-10-Q.pdf"
data = extract_company_info(pdf_path)

# Save to JSON file
with open("company_info.json", "w") as json_file:
    json.dump(data, json_file, indent=4)

print(f"Company Name: {data['company_name']}")
print(f"Filing Date: {data['filing_date']}")