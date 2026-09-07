from playwright.sync_api import sync_playwright
import json
import os

def scrape_agriculture_schemes():
    # Ensure the data directory exists
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    
    with sync_playwright() as p:
        # Launch browser (set headless=False if you want to watch the navigation steps)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.newPage() if hasattr(context, 'newPage') else context.new_page()
        
        # Navigate to the main Tamil Nadu Government portal or direct schemes section
        base_url = 'https://www.tn.gov.in/scheme_list.php?dep_id=Mg=='
        print(f"Connecting to {base_url}...")
        page.goto(base_url, wait_until="networkidle")

        try:
            # Step 1 & 2: Click through Schemes -> Schemes menu path if present on homepage,
            # or directly navigate to the schemes portal page.
            #print("Navigating through Schemes -> Schemes...")
            
            # Attempt to click the main 'Schemes' navigation/menu item
            # Adjust selectors based on live DOM text matching
            #page.get_by_text("Schemes", exact=False).first.click()
            
            # Wait for navigation or submenu option to appear and click 'Agriculture - Farmers Welfare Department'
            # Alternatively, if direct dropdown/link exists:
            page.wait_for_timeout(2000) # brief wait for menu transition
            
            # If a direct link or option for Agriculture - Farmers Welfare Department is available:
            agriculture_link = page.get_by_text("Agriculture - Farmers Welfare Department", exact=False)
            if agriculture_link.count() > 0:
                agriculture_link.first.click()
            else:
                # Fallback to direct URL if menu interaction varies
                print("Menu item not immediately clicked; navigating via direct department filter...")
                page.goto('https://www.tn.gov.in/scheme_list.php?dep_id=Mg==', wait_until="networkidle")

            page.wait_for_load_state("networkidle")

            # Extract scheme details from the target page table or list
            schemes = page.evaluate("""() => {
                const schemeData = [];
                const rows = document.querySelectorAll('table tr');

                if (rows.length > 0) {
                    rows.forEach((row, index) => {
                        const cells = row.querySelectorAll('td, th');
                        if (cells.length > 0) {
                            const rowText = Array.from(cells).map(cell => cell.innerText.trim()).join(' | ');
                            const linkElement = row.querySelector('a');
                            
                            schemeData.push({
                                'index': index,
                                'details': rowText,
                                'link': linkElement ? linkElement.href : null
                            });
                        }
                    });
                } else {
                    const listItems = document.querySelectorAll('ul li, ol li');
                    listItems.forEach((li, index) => {
                        const linkElement = li.querySelector('a');
                        schemeData.push({
                            'index': index + 1,
                            'details': li.innerText.trim(),
                            'link': linkElement ? linkElement.href : null
                        });
                    });
                }

                return schemeData;
            }""")

            # Filter out empty entries
            cleaned_schemes = [item for item in schemes if item.get('details')]

            # Save to JSON file inside the 'data' directory
            output_filename = os.path.join(data_dir, 'tn_schemes.json')
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(cleaned_schemes, f, ensure_ascii=False, indent=2)
                
            print(f"Successfully extracted {len(cleaned_schemes)} records and saved to {output_filename}")
            print(json.dumps(cleaned_schemes, ensure_ascii=False, indent=2))

        except Exception as e:
            print(f"An error occurred during scraping navigation: {e}")
        finally:
            browser.close()

if __name__ == '__main__':
    scrape_agriculture_schemes()