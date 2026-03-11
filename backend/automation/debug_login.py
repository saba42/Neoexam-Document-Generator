import asyncio
from playwright.async_api import async_playwright

async def debug_login(url, email, password):
    if not url.startswith("http"):
        url = "https://" + url
        
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print(f"Navigating to {url}")
        await page.goto(url, wait_until="networkidle")
        
        # Save HTML for analysis
        htmlContent = await page.content()
        with open("login_page.html", "w") as f:
            f.write(htmlContent)
        print("Saved HTML to backend/login_page.html")
        
        await page.screenshot(path="login_debug.png")
        print("Saved screenshot to backend/login_debug.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_login("admin.nirmalacollege305.examly.io", "test@test.com", "password"))
