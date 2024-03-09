from tkinter import Tk
from lib.data_manager import DataManager
from lib.browser_controller import BrowserController
from lib.video_utils import *
from multiprocessing import Process
from asyncio import sleep


class AutoFilm:
    def __init__(self, root):

        # GUI --------------------------------------------------------------------
        self.root = root
        self.root.title("AutoFilm")

        self.dm = DataManager(root)

        self.dm.create_entry("Executable Path:", "executable_path", isBrowse=True)
        self.dm.create_entry("Profile Path:", "chrome_profile_path", isBrowse=True)

        self.dm.create_entry("Caption Path:", "caption_path", isBrowse=True)
        self.dm.create_entry(
            "Voice Folder Path:", "voice_folder_path", isFolder=True, isBrowse=True
        )
        self.dm.create_entry("Video Path:", "video_path", isBrowse=True)

        self.dm.create_button("Create Caption", self.create_caption, self.load_data)
        self.dm.create_button("Create Video", self.auto_film, self.load_data)

    def load_data(self):
        self.executable_path = self.dm.get_entry_data("executable_path")
        self.chrome_profile_path = self.dm.get_entry_data("chrome_profile_path")
        self.caption_path = self.dm.get_entry_data("caption_path")
        self.voice_folder_path = self.dm.get_entry_data("voice_folder_path")
        self.video_path = self.dm.get_entry_data("video_path")
        self.bc = BrowserController(
            executable_path=self.executable_path,
            chrome_profile_path=self.chrome_profile_path,
            download_path=self.voice_folder_path,
            gl_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTk3OWJkMGViOWU2M2YzNDcwZDU5MjMiLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2NTlkMmQwOTc3NDJjNTdiYTg1ZWJkNzUifQ.gXbYZNg6NqNNTm301zzlg7cjsBedsB7hCadje8jzq8s",
        )

    async def create_caption(self):
        await self.bc.create_gl_profile()
        await self.bc.connect_gl_profile(self.bc.gl_profile_id)
        self.page = self.bc.page
        self.browser = self.bc.browser

        await self.sign_in_vbee()

        await self.bc.gl_stop()
        await self.bc.delete_gl_profile(self.bc.gl_profile_id)

    async def sign_in_vbee(self):
        await self.page.goto("https://studio.vbee.vn/studio/text-to-speech")

        button = await self.page.waitForSelector(
            "#__next > div > div:nth-child(1) > div > div > div.flex.flex-row-reverse.mobile-breakpoint\:flex-row.flex-grow.gap-4 > div.flex.items-start.justify-end.mobile-breakpoint\:justify-center.flex-grow.mobile-breakpoint\:flex-grow-0.gap-2 > div.my-auto.block > div > button"
        )

        await button.click()

        await self.page.waitForSelector("div.absolute#dropdown")

        button = await self.page.waitForSelector(
            "div.absolute#dropdown > div > button:nth-child(2)"
        )

        if button:
            await button.click()
            await sleep(1)

        pages = await self.browser.pages()

        for page in pages:
            if "https://accounts.vbee.ai/" in page.url:
                self.page = page
                break

        return True

    def auto_film(self):
        # merge_audio_with_video(
        #     self.voice_folder_path, self.video_path, self.caption_path
        # )
        return


def main():
    root = Tk()
    app = AutoFilm(root)
    root.mainloop()


if __name__ == "__main__":
    main()
