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
    ):
        self.executable_path = executable_path
        self.chrome_profile_path = chrome_profile_path

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


async def main():
    browser_controller = BrowserController(
        executable_path="C:/Program Files/Google/Chrome/Application/chrome.exe",
        chrome_profile_path="C:/Users/xinch/AppData/Local/Google/Chrome/User Data/Profile 1",
    )
    await browser_controller.initialize_browser()


if __name__ == "__main__":
    run(main())
