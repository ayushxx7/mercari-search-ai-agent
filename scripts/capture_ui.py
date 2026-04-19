import asyncio
from playwright.async_api import async_playwright
import time
import os
import shutil

async def capture():
    video_dir = "showcase/temp_video"
    if os.path.exists(video_dir):
        shutil.rmtree(video_dir)
    os.makedirs(video_dir)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        # 1. Pre-load for stability
        print("Pre-loading app...")
        temp_context = await browser.new_context()
        temp_page = await temp_context.new_page()
        try:
            await temp_page.goto("http://localhost:8502", timeout=60000)
            await temp_page.wait_for_selector("h1", timeout=60000)
            await asyncio.sleep(8) 
        except Exception as e:
            print(f"Pre-load warning: {e}")
        await temp_context.close()

        # 2. Record snappy demo
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            record_video_dir=video_dir,
            record_video_size={'width': 1280, 'height': 720}
        )
        page = await context.new_page()
        
        try:
            print("Recording ultra-snappy demo...")
            await page.goto("http://localhost:8502")
            await page.wait_for_selector("h1")
            
            await asyncio.sleep(1)
            await page.screenshot(path="showcase/landing.png")

            # Rapid search
            search_box = page.get_by_label("🔎 Search for products")
            await search_box.fill("bag")
            await page.keyboard.press("Enter")
            
            await asyncio.sleep(3) 
            await page.screenshot(path="showcase/default_search_bag.png")

            # Toggle AI
            print("Toggling AI Assistant...")
            await page.get_by_text("AI Assistant (LLM-powered search & recommendations)").click()
            
            # Wait just enough for AI recommendations to appear
            await asyncio.sleep(7) 
            
            await page.screenshot(path="showcase/ai_search_bag.png")
            
            # No final pause - cut immediately
            print("Demo sequence complete.")
            
        except Exception as e:
            print(f"Error: {e}")
        
        await context.close()
        await browser.close()

        # 3. Trim and Convert
        videos = os.listdir(video_dir)
        if videos:
            video_path = os.path.join(video_dir, videos[0])
            raw_video = "showcase/raw_demo.webm"
            shutil.move(video_path, raw_video)
            
            final_gif = "showcase/demo_ai_search.gif"
            
            print("Trimming and converting to ultra-snappy GIF...")
            # -ss 1: Start 1 second in
            # -t 11: Limit duration to 11 seconds total
            os.system(f"ffmpeg -y -i {raw_video} -ss 1 -t 11 -vf \"fps=10,scale=800:-1:flags=lanczos\" {final_gif}")
            print(f"Ultra-snappy GIF saved to {final_gif}")
            
    if os.path.exists(video_dir):
        shutil.rmtree(video_dir)
    if os.path.exists("showcase/raw_demo.webm"):
        os.remove("showcase/raw_demo.webm")

if __name__ == "__main__":
    asyncio.run(capture())
