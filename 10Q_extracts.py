import pdfplumber
import re
import json

def find_section_pages(pdf_path, section_name):
    """Find the start and next section's page number from the index."""
    with pdfplumber.open(pdf_path) as pdf:
        index_page = pdf.pages[1]  # Assuming index is on page 2
        index_text = index_page.extract_text()

        # Find all sections and their page numbers
        matches = re.findall(r"(Item\s+\d+\..*?)\s+(\d+)", index_text, re.IGNORECASE)
        sections = [(match[0], int(match[1])) for match in matches]

        # Locate the requested section and the next section
        for i, (sec, page) in enumerate(sections):
            if section_name.lower() in sec.lower():
                next_section = sections[i + 1] if i + 1 < len(sections) else None
                next_section_name = next_section[0] if next_section else None
                next_section_page = next_section[1] if next_section else None
                
                print(f"Section '{sec}' starts on page {page}.")
                if next_section:
                    print(f"Next section '{next_section_name}' starts on page {next_section_page}.")

                return page, next_section_name, next_section_page

        print(f"Section '{section_name}' not found in the index.")
        return None, None, None

def extract_section_by_name(pdf_path, section_name):
    """Extract only the relevant section text from its start page until the next section starts."""
    start_page, next_section_name, next_section_page = find_section_pages(pdf_path, section_name)
    if start_page is None:
        return {"error": f"Section '{section_name}' not found in the index."}

    with pdfplumber.open(pdf_path) as pdf:
        extracted_text = []
        found_section = False  # Flag to track when the section starts

        for i in range(start_page - 1, len(pdf.pages)):  # Adjust for 0-based index
            page = pdf.pages[i]
            text = page.extract_text()

            if text:
                if found_section:
                    # If the next section is on the same page, stop at its heading
                    if next_section_name and re.search(fr"({next_section_name})", text, re.IGNORECASE):
                        extracted_text.append(text[:re.search(fr"({next_section_name})", text, re.IGNORECASE).start()])
                        break  # Stop extracting when the next section is found
                    
                    # If the next section starts on a different page, extract everything from this page
                    extracted_text.append(text)

                    # Stop when we reach the next section's page number
                    if next_section_page and i + 1 == next_section_page - 1:
                        break
                else:
                    # Search for the section heading on the start page
                    match = re.search(fr"({section_name})", text, re.IGNORECASE)
                    if match:
                        found_section = True
                        section_text = text[match.start():]  # Extract from section heading onward
                        
                        # If the next section is on the same page, stop at its heading
                        if next_section_name:
                            next_match = re.search(fr"({next_section_name})", section_text, re.IGNORECASE)
                            if next_match:
                                section_text = section_text[:next_match.start()]
                                found_section = False  # Stop searching
                        
                        extracted_text.append(section_text)

        if extracted_text:
            section_content = "\n".join(extracted_text)
            print(f"\nExtracted Section '{section_name}':\n{section_content}")

            # Store extracted section text in a JSON file
            section_data = {"section_name": section_name, "start_page": start_page, "end_page": next_section_page, "content": section_content}
            with open("section_data.json", "w") as json_file:
                json.dump(section_data, json_file, indent=4)

            return section_data

    return {"error": f"Section '{section_name}' not found on the expected pages."}

# Example usage
pdf_path = "CISCO-2Q-2024-10-Q.pdf"
section_name = "Item 3. Quantitative and Qualitative Disclosures About Market Risk"
section_text = extract_section_by_name(pdf_path, section_name)
