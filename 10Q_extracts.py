import pdfplumber
import re
import json

def get_index_sections(pdf_path):
    """Extract all sections and their page numbers from the index, adding Item 1 manually."""
    with pdfplumber.open(pdf_path) as pdf:
        index_page = pdf.pages[1]  # Assuming index is on page 2
        index_text = index_page.extract_text()

        # Find all sections and their page numbers from index
        matches = re.findall(r"(Item\s+\d+\..*?)\s+(\d+)", index_text, re.IGNORECASE)
        sections = [{"section_name": match[0], "page": int(match[1])} for match in matches]

        # Find the page where "Item 1. Financial Statements" appears
        item1_page = None
        for i, page in enumerate(pdf.pages[2:], start=3):  # Start from page 3 (index 2)
            text = page.extract_text()
            if text and re.search(r"Item 1\. Financial Statements", text, re.IGNORECASE):
                item1_page = i
                break

        # Add Item 1 at the top with its found page number
        if item1_page:
            sections.insert(0, {"section_name": "Item 1. Financial Statements", "page": item1_page})
        else:
            print("Warning: 'Item 1. Financial Statements' not found in the document.")

        # Save sections to a separate JSON file
        with open("index_sections.json", "w") as json_file:
            json.dump(sections, json_file, indent=4)
        
        print("\nSections found in index:")
        for section in sections:
            print(f"{section['section_name']} - Page {section['page']}")
        
        return sections

def extract_item1_financial_statements(pdf_path):
    """Extract 'Item 1. Financial Statements' from page 3 until 'Item 2' appears."""
    with pdfplumber.open(pdf_path) as pdf:
        extracted_text = []
        found_item1 = False
        start_page = None
        end_page = None

        for i, page in enumerate(pdf.pages[2:], start=3):  # Start from page 3
            text = page.extract_text()
            if text:
                if not found_item1:
                    if re.search(r"Item 1\. Financial Statements", text, re.IGNORECASE):
                        found_item1 = True
                        start_page = i
                        match = re.search(r"Item 1\. Financial Statements", text, re.IGNORECASE)
                        extracted_text.append(text[match.start():])
                else:
                    # Check for Item 2 to stop extraction
                    if re.search(r"Item 2\. Management’s Discussion and Analysis of Financial Condition and Results of Operations", text, re.IGNORECASE):
                        end_page = i
                        match = re.search(r"Item 2\. Management’s Discussion and Analysis of Financial Condition and Results of Operations", text, re.IGNORECASE)
                        extracted_text.append(text[:match.start()])
                        break
                    extracted_text.append(text)

        if extracted_text:
            section_content = "\n".join(extracted_text)
            print(f"\nExtracted Section 'Item 1. Financial Statements':\n{section_content}")

            # Store extracted section text in a JSON file
            section_data = {
                "section_name": "Item 1. Financial Statements",
                "start_page": start_page,
                "end_page": end_page,
                "content": section_content
            }
            with open("section_data.json", "w") as json_file:
                json.dump(section_data, json_file, indent=4)

            return section_data
        
        return {"error": "'Item 1. Financial Statements' not found in the document."}

def find_section_pages(pdf_path, section_name, sections):
    """Find the start and next section's page number from the provided sections list."""
    for i, section in enumerate(sections):
        if section_name.lower() in section["section_name"].lower():
            next_section = sections[i + 1] if i + 1 < len(sections) else None
            next_section_name = next_section["section_name"] if next_section else None
            next_section_page = next_section["page"] if next_section else None
            
            print(f"\nSection '{section['section_name']}' starts on page {section['page']}.")
            if next_section:
                print(f"Next section '{next_section_name}' starts on page {next_section_page}.")
            
            return section["page"], next_section_name, next_section_page
    
    print(f"Section '{section_name}' not found in the index.")
    return None, None, None

def extract_section_by_name(pdf_path, section_name):
    """Extract only the relevant section text from its start page until the next section starts."""
    # Get all sections from index
    sections = get_index_sections(pdf_path)
    
    start_page, next_section_name, next_section_page = find_section_pages(pdf_path, section_name, sections)
    if start_page is None:
        return {"error": f"Section '{section_name}' not found in the index."}

    with pdfplumber.open(pdf_path) as pdf:
        extracted_text = []
        found_section = False

        for i in range(start_page - 2, len(pdf.pages)):  # Adjust for 0-based index
            page = pdf.pages[i]
            text = page.extract_text()

            if text:
                if found_section:
                    if next_section_name and re.search(fr"({next_section_name})", text, re.IGNORECASE):
                        extracted_text.append(text[:re.search(fr"({next_section_name})", text, re.IGNORECASE).start()])
                        break
                    
                    extracted_text.append(text)
                    if next_section_page and i + 1 == next_section_page - 1:
                        break
                else:
                    match = re.search(fr"({section_name})", text, re.IGNORECASE)
                    if match:
                        found_section = True
                        section_text = text[match.start():]
                        if next_section_name:
                            next_match = re.search(fr"({next_section_name})", section_text, re.IGNORECASE)
                            if next_match:
                                section_text = section_text[:next_match.start()]
                                found_section = False
                        extracted_text.append(section_text)

        if extracted_text:
            section_content = "\n".join(extracted_text)
            print(f"\nExtracted Section '{section_name}':\n{section_content}")

            # Store extracted section text in a JSON file
            section_data = {
                "section_name": section_name,
                "start_page": start_page,
                "end_page": next_section_page,
                "content": section_content
            }
            with open("section_data.json", "w") as json_file:
                json.dump(section_data, json_file, indent=4)

            return section_data

    return {"error": f"Section '{section_name}' not found on the expected pages."}

# User input and conditional execution
def main():
    pdf_path = input("Enter the PDF file path: ")
    section_name = input("Enter the section name to extract: ")
    
    if section_name.lower() == "item 1. financial statements":
        result = extract_item1_financial_statements(pdf_path)
    else:
        result = extract_section_by_name(pdf_path, section_name)
    
    if "error" in result:
        print(result["error"])
    else:
        print(f"\nSection data saved to 'section_data.json'")

if __name__ == "__main__":
    main()