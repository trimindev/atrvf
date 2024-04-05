from pyppeteer import launch, connect
import cv2
from asyncio import run, sleep
import pyperclip
from pyautogui import hotkey, press
from time import time
from gologin import GoLogin


def copy_paste(text, sleep=0.2):
    hotkey("ctrl", "a")
    pyperclip.copy(text)
    hotkey("ctrl", "v", interval=sleep)


def copy_paste_enter(text, isTab=False, sleep=1):
    hotkey("ctrl", "a")
    pyperclip.copy(text)
    hotkey("ctrl", "v", interval=0.2)

    if isTab:
        press("tab")

    press("enter", interval=sleep)
    return True


class BrowserController:
    def __init__(
        self,
        executable_path=None,
        chrome_profile_path=None,
        download_path=None,
        gl_token=None,
        gl_profile_id=None,
    ):
        self.executable_path = executable_path
        self.chrome_profile_path = chrome_profile_path
        self.download_path = download_path
        self.gl_token = gl_token
        self.gl_profile_id = gl_profile_id
        self.browser = None
        self.page = None
        self.gl = GoLogin({"token": self.gl_token})

    async def initialize_browser(self):
        self.browser = await launch(
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

        self.page = await self.browser.newPage()

    async def connect_gl_profile(self, profile_id):
        self.gl.setProfileId(profile_id)
        debugger_address = self.gl.start()
        self.browser = await connect(
            browserURL="http://" + debugger_address, defaultViewport=None
        )
        self.page = await self.browser.newPage()
        await self.gl.normalizePageView(self.page)

    async def create_gl_profile(self, auto_proxy=False, proxy=False):

        if auto_proxy and not proxy:
            proxy_config = {
                "mode": "gologin",
                "autoProxyRegion": "us",
            }

        if not auto_proxy:
            proxy_config = {
                "mode": "none",
            }

        if proxy:
            proxy_config = {
                "host": proxy.host,
                "port": proxy.port,
                "username": proxy.username,
                "password": proxy.password,
            }

        self.gl_profile_id = self.gl.create(
            {
                "name": "demo",
                "os": "mac",
                "navigator": {
                    "language": "en-US",
                    "userAgent": "random",
                    "resolution": "1024x960",
                    "platform": "mac",
                },
                "proxy": proxy_config,
                "webRTC": {
                    "mode": "alerted",
                    "enabled": True,
                },
                "storage": {
                    "local": True,  # Local Storage is special browser caches that websites may use for user tracking in a way similar to cookies.
                    # Having them enabled is generally advised but may increase browser profile loading times.
                    "extensions": True,  # Extension storage is a special cotainer where a browser stores extensions and their parameter.
                    # Enable it if you need to install extensions from a browser interface.
                    "bookmarks": True,  # This option enables saving bookmarks in a browser interface.
                    "history": True,  # Warning! Enabling this option may increase the amount of data required
                    # to open/save a browser profile significantly.
                    # In the interests of security, you may wish to disable this feature,
                    # but it may make using GoLogin less convenient.
                    "passwords": True,  # This option will save passwords stored in browsers.
                    # It is used for pre-filling login forms on websites.
                    # All passwords are securely encrypted alongside all your data.
                    "session": True,  # This option will save browser session. It is used to save last open tabs.
                    "indexedDb": False,  # IndexedDB is special browser caches that websites may use for user tracking in a way similar to cookies.
                    # Having them enabled is generally advised but may increase browser profile loading times.
                },
            }
        )

        print("profile id=", self.gl_profile_id)

    async def gl_stop(self):
        await self.browser.close()
        self.gl.stop()

    async def delete_gl_profile(self, profile_id):
        self.gl.delete(profile_id)

    async def set_download_location(self):
        await self.page.goto("chrome://settings/downloads")

        await self.page.keyboard.press("Tab")
        await self.page.keyboard.press("Tab")
        await self.page.keyboard.press("Enter")
        await sleep(0.5)
        copy_paste_enter(self.download_path.replace("/", "\\"), isTab=True)
        await self.page.close()

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
        download_path="C:/Users/xinch/Desktop/demo/demo_voices",
    )
    await browser_controller.initialize_browser()


if __name__ == "__main__":
    run(main())
