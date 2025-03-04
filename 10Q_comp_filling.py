import pdfplumber
import re
import json
from datetime import datetime

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
    
    # Get the quarter number
    quarter = get_quarter_from_date(filing_date) if filing_date != "Not Found" else "Not Found"

    return {"company_name": company_name, "filing_date": filing_date, "quarter": quarter}

def get_quarter_from_date(date_str):
    """Returns the quarter (Q1, Q2, Q3, Q4) based on the filing date."""
    try:
        date_obj = datetime.strptime(date_str, "%B %d, %Y")  # Convert to datetime object
        month = date_obj.month
        
        if 1 <= month <= 3:
            return "Q1"
        elif 4 <= month <= 6:
            return "Q2"
        elif 7 <= month <= 9:
            return "Q3"
        else:
            return "Q4"
    
    except ValueError:
        return "Invalid Date"

# Example usage
pdf_path = "SandPGlobal-2Q-2024-10-Q.pdf"
data = extract_company_info(pdf_path)

# Save to JSON file
with open("company_info.json", "w") as json_file:
    json.dump(data, json_file, indent=4)

print(f"Company Name: {data['company_name']}")
print(f"Filing Date: {data['filing_date']}")
print(f"Quarter: {data['quarter']}")
