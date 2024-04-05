from tkinter import Tk
from lib.data_manager import DataManager
from lib.browser_controller import BrowserController
from lib.video_utils import *
from asyncio import sleep
import pyperclip
import re
import pyperclip


def is_valid_email(email):
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    return bool(re.match(pattern, email))


class AutoFilm:
    def __init__(self, root):

        # GUI --------------------------------------------------------------------
        self.root = root
        self.root.title("Atrvf")

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
            gl_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTk3OWJkMGViOWU2M2YzNDcwZDU5MjMiLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2NTlkMmQwOTc3NDJjNTdiYTg1ZWJkNzUifQ.gXbYZNg6NqNNTm301zzlg7cjsBedsB7hCadje8jzq8s",
        )
        self.pass_vbee = "1abcdxyz2"

    async def create_caption(self):
        await self.bc.delete_all_profiles()
        await self.bc.create_gl_profile(auto_proxy=False)
        await self.bc.connect_gl_profile(self.bc.gl_profile_id)
        # await self.bc.connect_gl_profile("65ec8440f4dbc027cfd0a117")

        self.page = self.bc.page
        self.browser = self.bc.browser

        await self.sign_in_vbee()

        # await self.bc.gl_stop()

    async def go_to_sign_in_page(self):
        await self.page.goto(
            "https://temp-mail.org/vi", {"waitUntil": "domcontentloaded"}
        )

        self.page = await self.browser.newPage()

        await self.page.goto("https://studio.vbee.vn/studio/text-to-speech")

        await sleep(2)

        button = await self.page.waitForSelector(
            "#__next > div > div:nth-child(1) > div > div > div.flex.flex-row-reverse.mobile-breakpoint\:flex-row.flex-grow.gap-4 > div.flex.items-start.justify-end.mobile-breakpoint\:justify-center.flex-grow.mobile-breakpoint\:flex-grow-0.gap-2 > div.my-auto.block > div > button"
        )

        while True:
            try:
                await button.click()
                ai_studio = await self.page.waitForSelector(
                    "div.absolute#dropdown > div > button:nth-child(2)", timeout=2000
                )
                await ai_studio.click()
                break
            except:
                pass
        await sleep(1)

    async def fill_sign_in(self):
        self.page = await self.bc.goto_page_with_url_containing("https://temp-mail.org")

        email = None
        while email is None or not is_valid_email(email):
            email = await self.page.evaluate('document.getElementById("mail").value')
            if email is None:
                await sleep(1)

        if not email:
            return False

        self.page = await self.bc.goto_page_with_url_containing(
            "https://accounts.vbee.ai/"
        )

        await self.page.type("#email", email)
        await self.page.type("#password", self.pass_vbee)
        await self.page.type("#passwordConfirm", self.pass_vbee)

        login_btn = await self.page.waitForSelector('button[name="login"]')
        await login_btn.click()

    async def confirm_sign_in(self):
        self.page = await self.bc.goto_page_with_url_containing("https://temp-mail.org")

        link_confirm = await self.page.waitForSelector(
            "div.inbox-dataList > ul > li:nth-child(2) > div:nth-child(1) > a"
        )
        await link_confirm.click()

        confirm_btn = await self.page.waitForSelector(
            "div.inbox-data-content > div.inbox-data-content-intro > div > div > div:nth-child(2) > a"
        )
        confirm_href = await self.page.evaluate(
            '(element) => element.getAttribute("href")', confirm_btn
        )
        self.page = await self.browser.newPage()
        await self.page._client.send(
            "Page.setDownloadBehavior",
            {
                "behavior": "allow",
                "auto_downloads": 1,
                "downloadPath": self.voice_folder_path,
            },
        )
        await self.page.goto(confirm_href)

    async def setup_vbee(self):
        checkbox = await self.page.waitForSelector("div.dialog-checkbox > span > input")
        await checkbox.click()

        continue_btn = await self.page.waitForSelector("div.dialog-action > button")
        await continue_btn.click()

        dont_show_again_btn = await self.page.waitForSelector(
            "div.not-show-again > label > span > input"
        )
        await dont_show_again_btn.click()
        await sleep(0.5)

        close_btn = await self.page.waitForSelector(
            "div.MuiDialogContent-root > button"
        )
        await close_btn.click()
        await sleep(0.5)

        back_btn = await self.page.waitForSelector(
            "#react-joyride-step-0 > div > div > div > div > button > div > div"
        )
        await back_btn.click()
        await sleep(0.5)

        skip_hightlight_to_listen = await self.page.waitForSelector(
            "p.MuiTypography-root.MuiTypography-body1.ignore-text"
        )
        await skip_hightlight_to_listen.click()
        await sleep(0.5)

        # Click choose voice
        choose_voice_btn = await self.page.waitForSelector(
            ".group-adjust-voice > button"
        )
        await choose_voice_btn.click()
        await sleep(1)

        # Click vn language checkbox
        await self.page.evaluate(
            "document.querySelector(\"input[value='vi-VN']\").click();"
        )
        await sleep(1)

        # Click first voice
        first_voice = await self.page.waitForSelector(".voice-list > button ")
        await first_voice.click()
        await sleep(0.5)

        # Adjust speed
        speed_input = await self.page.waitForSelector("[id='mui-8']")
        await speed_input.click()
        await speed_input.type("1.1")
        await self.page.keyboard.press("Enter")
        await sleep(0.5)

        enter_text_here = await self.page.waitForSelector(
            "#enter-text-here > div.editor-wrapper > div > div.DraftEditor-editorContainer > div > div"
        )
        await enter_text_here.click()
        await sleep(0.5)

        pyperclip.copy("Đây là câu thoại mẫu")
        await self.page.keyboard.down("Control")
        await self.page.keyboard.press("KeyV")
        await self.page.keyboard.up("Control")

        generate_btn = await self.page.waitForSelector(".request-info > button")
        await generate_btn.click()
        await sleep(0.5)

        close_ad_button = await self.page.waitForSelector(
            ".dialog-content > h2 > button"
        )
        await close_ad_button.click()
        await sleep(0.5)

        await self.page.waitForSelector(".request-info > .MuiTypography-body1")
        await sleep(0.5)

        # If find expand icon then click
        expand_icon = await self.page.querySelector(
            'button > [data-testid="KeyboardArrowDownIcon"]'
        )
        if expand_icon:
            await expand_icon.click()
            await sleep(0.5)
        else:
            pass

        # Click checkbox of head row to select voices
        head_checkbox = await self.page.querySelector(
            ".MuiCheckbox-root > .PrivateSwitchBase-input"
        )
        await head_checkbox.click()
        await sleep(0.5)

        # Click download selected
        download_button = await self.page.waitForSelector(
            ".MuiTableCell-root .download-button"
        )
        await download_button.click()
        await sleep(0.5)

        # Click delete selected
        delete_selected_btn = await self.page.querySelector(
            ".MuiTableCell-root .delete-button"
        )
        await delete_selected_btn.click()
        await sleep(0.5)

        # Click confirm delete yes
        confirm_delete_yes_btn = await self.page.querySelector(
            ".content > div > button.MuiButton-containedPrimary"
        )
        await confirm_delete_yes_btn.click()
        await sleep(0.5)

    async def sign_up_vbee(self):
        await self.page.goto("https://studio.vbee.vn/studio/text-to-speech")

        sign_up_btn = await self.page.waitForSelector(
            'div.mobile-breakpoint\:flex > div > div[role="button"]'
        )

        await sign_up_btn.click()

        ai_voice_studio = await self.page.waitForSelector(
            "#dropdown.absolute > div > button:nth-child(2)"
        )

        await ai_voice_studio.click()

        self.page = await self.bc.goto_page_with_url_containing(
            "https://accounts.vbee.ai/"
        )

        self.page.type("#username", "vegih76838@comsb.com")
        self.page.type("#password", self.pass_vbee)

    async def sign_in_vbee(self):
        await self.go_to_sign_in_page()
        await self.fill_sign_in()
        await self.confirm_sign_in()
        await self.setup_vbee()

        await sleep(3000)
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
