from pyppeteer import launch
import cv2
from asyncio import run, sleep
import pyperclip
from time import time


class BrowserController:
    def __init__(
        self,
        executable_path=None,
        chrome_profile_path=None,
        download_path=None,
    ):
        self.executable_path = executable_path
        self.chrome_profile_path = chrome_profile_path
        self.download_path = download_path

    async def initialize_browser(self):
        browser = await launch(
            {
                "executablePath": self.executable_path,
                "userDataDir": self.chrome_profile_path,
                "headless": False,
                "defaultViewport": None,
                "width": 1024,
                "height": 960,
                "autoClose": True,
            }
        )

        return browser

    async def click_img(self, img_path):
        result = await self.find_img(img_path, timeout=10)
        if result:
            center_x, center_y = result
            await self.page.mouse.click(center_x, center_y)
        else:
            print("Image not found within the specified timeout.")

    async def find_img(self, img_path, timeout=10):
        start_time = time.time()

        while True:
            if time() - start_time > timeout:
                return False

            await self.page.screenshot({"path": "screenshot.png"})

            template_image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            screen_image = cv2.imread("screenshot.png", cv2.IMREAD_GRAYSCALE)

            result = cv2.matchTemplate(
                screen_image, template_image, cv2.TM_CCOEFF_NORMED
            )
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            threshold = 0.8

            if max_val >= threshold:
                template_width, template_height = template_image.shape[::-1]
                center_x = max_loc[0] + template_width / 2
                center_y = max_loc[1] + template_height / 2

                return center_x, center_y

            await sleep(0.1)

    async def goto_page_with_url_containing(self, url_part):
        pages = await self.browser.pages()
        for page in pages:
            if url_part in page.url:
                await page.bringToFront()
                return page
        return None

    async def copy_paste(self, page, text):
        pyperclip.copy(text)

        await page.keyboard.down("Control")
        await page.keyboard.press("KeyV")
        await page.keyboard.up("Control")


async def main():
    browser_controller = BrowserController(
        executable_path="C:/Program Files/Google/Chrome/Application/chrome.exe",
        chrome_profile_path="C:/Users/xinch/AppData/Local/Google/Chrome/User Data/Profile 1",
    )
    await browser_controller.initialize_browser()


if __name__ == "__main__":
    run(main())
