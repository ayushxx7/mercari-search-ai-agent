import asyncio
from playwright.async_api import async_playwright
import time
import os
import shutil

async def capture():
    # Setup directory for video
    video_dir = "showcase/temp_video"
    if os.path.exists(video_dir):
        shutil.rmtree(video_dir)
    os.makedirs(video_dir)

    async with async_playwright() as p:
        # Launch browser with video recording enabled
        browser = await p.chromium.launch()
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            record_video_dir=video_dir,
            record_video_size={'width': 1280, 'height': 800}
        )
        page = await context.new_page()
        
        print("Waiting for Streamlit to load (20s delay for full hydration)...")
        await asyncio.sleep(20)
        
        try:
            await page.goto("http://localhost:8502")
            # Wait for the main title to appear
            await page.wait_for_selector("h1", timeout=60000)
            print("Page loaded.")
            
            # 1. Take landing page screenshot after delay
            await asyncio.sleep(5)
            await page.screenshot(path="showcase/landing.png")
            print("Landing screenshot saved.")

            # 2. Perform Default Search for "bag"
            print("Performing default search for 'bag'...")
            search_input = page.get_by_placeholder("Search for products")
            if await search_input.count() == 0:
                 # Fallback to general text input if placeholder doesn't match
                 search_input = page.locator("input").first
            
            await search_input.fill("bag")
            await page.keyboard.press("Enter")
            await asyncio.sleep(8) # Wait for search results
            
            await page.screenshot(path="showcase/default_search_bag.png")
            print("Default search screenshot saved.")

            # 3. Enable AI Assistant
            print("Enabling AI Assistant...")
            # Streamlit checkboxes are often labels
            await page.get_by_text("AI Assistant (LLM-powered search & recommendations)").click()
            await asyncio.sleep(15) # Wait for AI to process and recommend
            
            await page.screenshot(path="showcase/ai_search_bag.png")
            print("AI search screenshot saved.")
            
            print("Demo sequence complete.")
            
        except Exception as e:
            print(f"Error during capture: {e}")
            await page.screenshot(path="showcase/debug_error.png")
        
        await context.close()
        await browser.close()

        # Find the recorded video file and rename it
        videos = os.listdir(video_dir)
        if videos:
            video_path = os.path.join(video_dir, videos[0])
            final_video = "showcase/demo_ai_search.webm"
            shutil.move(video_path, final_video)
            print(f"Video saved to {final_video}")
            
            # Convert to GIF using ffmpeg for README compatibility
            print("Converting video to GIF...")
            os.system(f"ffmpeg -y -i {final_video} -vf \"fps=10,scale=800:-1:flags=lanczos\" showcase/demo_ai_search.gif")
            print("GIF saved to showcase/demo_ai_search.gif")
            
    # Cleanup temp video dir
    if os.path.exists(video_dir):
        shutil.rmtree(video_dir)

if __name__ == "__main__":
    if not os.path.exists("showcase"):
        os.makedirs("showcase")
    asyncio.run(capture())
