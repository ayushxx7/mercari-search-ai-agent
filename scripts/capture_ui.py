import asyncio
from playwright.async_api import async_playwright
import time

async def capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1440, 'height': 900})
        
        print("Waiting for Streamlit to load...")
        # Give it some time to start and render
        await asyncio.sleep(10)
        
        try:
            await page.goto("http://localhost:8502")
            # Wait for the main title to appear
            await page.wait_for_selector("h1", timeout=30000)
            print("Page loaded.")
            
            # Take a full page screenshot
            await page.screenshot(path="showcase/landing.png", full_page=False)
            print("Screenshot saved to showcase/landing.png")
            
            # Let's try to interact a bit - type in search
            await page.fill("input[aria-label='🔎 Search for products']", "iPhone")
            await page.keyboard.press("Enter")
            await asyncio.sleep(5) # Wait for results
            
            await page.screenshot(path="showcase/search_results.png")
            print("Screenshot saved to showcase/search_results.png")
            
        except Exception as e:
            print(f"Error during capture: {e}")
            # Take a debug screenshot if it fails
            await page.screenshot(path="showcase/debug_error.png")
        
        await browser.close()

if __name__ == "__main__":
    import os
    if not os.path.exists("showcase"):
        os.makedirs("showcase")
    asyncio.run(capture())
