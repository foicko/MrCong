from playwright.async_api import Playwright, async_playwright
import asyncio
import aiofiles


async def run(url):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url)
        await page.get_by_role("button", name="I'm a human").click()
        await page.get_by_role("button", name="Get Link").click()
        await page.get_by_role("button", name="Consent").click()
        await page.get_by_role("link", name="I Accept").click()
        print(page.url)
        async with aiofiles.open('Page_Need_To_Get_DownloadUrl.txts', 'a+', encoding='utf-8') as f:
            f.write(page.url+'\n')
        #  ---------------------
        await context.close()
        await browser.close()


# asyncio.run(run("https://ouo.io/z0Gc1S7"))
