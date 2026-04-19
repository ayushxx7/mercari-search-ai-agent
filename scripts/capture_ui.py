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
        # Launch browser
        browser = await p.chromium.launch()
        
        # Initial wait for server to be ready - without recording
        print("Pre-loading app to handle hydration...")
        temp_context = await browser.new_context()
        temp_page = await temp_context.new_page()
        try:
            await temp_page.goto("http://localhost:8502", timeout=60000)
            await temp_page.wait_for_selector("h1", timeout=60000)
            # Wait for Streamlit's "Running..." to stop
            await asyncio.sleep(10) 
        except Exception as e:
            print(f"Warning during pre-load: {e}")
        await temp_context.close()

        # Now start recording for the actual demo
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            record_video_dir=video_dir,
            record_video_size={'width': 1280, 'height': 800}
        )
        page = await context.new_page()
        
        try:
            print("Navigating for recording...")
            await page.goto("http://localhost:8502")
            await page.wait_for_selector("h1")
            await asyncio.sleep(2) # Short pause for visuals
            
            # 1. Landing screenshot
            await page.screenshot(path="showcase/landing.png")
            print("Landing screenshot saved.")

            # 2. Perform Default Search for "bag"
            print("Performing default search for 'bag' in the main search box...")
            
            # Use label-based selector for the actual search box
            search_box = page.get_by_label("🔎 Search for products")
            await search_box.fill("bag")
            await page.keyboard.press("Enter")
            
            print("Waiting for default search results...")
            await asyncio.sleep(5) 
            await page.screenshot(path="showcase/default_search_bag.png")

            # 3. Enable AI Assistant
            print("Enabling AI Assistant...")
            await page.get_by_text("AI Assistant (LLM-powered search & recommendations)").click()
            
            print("Waiting for AI recommendations (this takes a moment)...")
            # Wait for the recommendations section or just enough time for the LLM
            await asyncio.sleep(15) 
            
            await page.screenshot(path="showcase/ai_search_bag.png")
            print("AI search screenshot saved.")
            
            print("Demo sequence complete.")
            
        except Exception as e:
            print(f"Error during capture: {e}")
            await page.screenshot(path="showcase/debug_error.png")
        
        await context.close()
        await browser.close()

        # Process the video
        videos = os.listdir(video_dir)
        if videos:
            video_path = os.path.join(video_dir, videos[0])
            raw_video = "showcase/raw_demo.webm"
            shutil.move(video_path, raw_video)
            
            final_gif = "showcase/demo_ai_search.gif"
            
            # Convert to GIF with trimming and optimization
            # We trim the first 2 seconds of the recorded session which might still be loading
            print("Converting video to optimized GIF...")
            # -ss 2 trims the first 2 seconds
            os.system(f"ffmpeg -y -i {raw_video} -ss 2 -vf \"fps=10,scale=800:-1:flags=lanczos\" {final_gif}")
            print(f"Optimized GIF saved to {final_gif}")
            
    # Cleanup
    if os.path.exists(video_dir):
        shutil.rmtree(video_dir)
    if os.path.exists("showcase/raw_demo.webm"):
        os.remove("showcase/raw_demo.webm")

if __name__ == "__main__":
    if not os.path.exists("showcase"):
        os.makedirs("showcase")
    asyncio.run(capture())
