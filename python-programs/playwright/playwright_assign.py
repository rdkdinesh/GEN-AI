import asyncio
from pathlib import Path

import pandas as pd  # type: ignore[reportMissingModuleSource]
from playwright.async_api import async_playwright

EXCEL_PATH = Path(r"C:\Users\Manimala DineshKumar\Downloads\contact.xlsx")


def load_contacts(file_path: Path):
    if not file_path.exists():
        raise FileNotFoundError(f"Excel file not found: {file_path}")

    df = pd.read_excel(file_path)
    required_columns = {"Name", "Phone", "Message"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Excel file is missing required columns: {sorted(missing)}")

    return df["Name"].tolist(), df["Phone"].tolist(), df["Message"].tolist()


async def send_message(page, contact_name: str, phone: int, message: str):
    search_box = page.locator('input[placeholder="Search or start a new chat"]')
    await search_box.wait_for(state="visible", timeout=20000)
    await search_box.fill(contact_name)
    await page.keyboard.press("Enter")

    message_box = page.locator('div[contenteditable="true"]').last
    await message_box.wait_for(state="visible", timeout=20000)
    await message_box.fill(message)
    await page.keyboard.press("Enter")

    print(f"Message sent to {contact_name}")
    await page.screenshot(path=f"{contact_name}_message_sent.png")

    # --- Close chat (go back to chat list) ---
    # WhatsApp doesn’t have a “close” button, but you can clear the search box
    page.fill("._2_1wd", "")
    #page.keyboard.press("Escape")

# Read the last 3 messages from whatsapp by name and phone number
async def read_last_3_messages(page, contact_name: str):
    search_box = page.locator('input[placeholder="Search or start a new chat"]')
    await search_box.wait_for(state="visible", timeout=20000)
    await search_box.fill(contact_name)
    await page.keyboard.press("Enter")

    # Wait for chat messages to load
    page.wait_for_selector("div.message-in, div.message-out")

    # Extract the last 5 messages
    messages = page.query_selector_all("div.message-in, div.message-out")
    for msg in messages[-5:]:
        text = msg.inner_text()
        print(text)

    last_messages = await page.locator('div.message-in').all()
    last_messages_text = []
    for msg in last_messages[-3:]:
        text = await msg.inner_text()
        last_messages_text.append(text)
    print(f"Last 3 messages received from {contact_name}:")
    for msg in last_messages_text:
        print(msg)
    return last_messages_text

async def main():
    contact_names, phones, messages = load_contacts(EXCEL_PATH)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://web.whatsapp.com/")
        print("Please scan the QR code to log in.")

        

        for contact_name, phone, message in zip(contact_names, phones, messages):
            await page.wait_for_selector('input[placeholder="Search or start a new chat"]', timeout=60000)
            await send_message(page, contact_name, phone, message)
            await page.wait_for_timeout(50000)

        # Screenshot after sending all messages
        await page.screenshot(path="all_messages_sent.png")

        # Extract last 3 messages sent by using last_3_messages function
        last_messages_text = []
        for contact_name in contact_names:
            last_3_msgs = await read_last_3_messages(page, contact_name)
            last_messages_text.extend(last_3_msgs)
            print(f"Last 3 messages for {contact_name}: {last_3_msgs}")
            # Wait for a short duration before moving to the next contact
            await page.wait_for_timeout(50000)
            # Prepare the json and excel file for the last 3 messages
            last_messages_df = pd.DataFrame({
                "Contact Name": [contact_name] * len(last_3_msgs),
                "Last 3 Messages": last_3_msgs
            })
            last_messages_df.to_excel(f"{contact_name}_last_3_messages.xlsx", index=False)


        await browser.close()
        print("All messages sent successfully.")


if __name__ == "__main__":
    asyncio.run(main())
