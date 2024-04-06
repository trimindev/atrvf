from tkinter import Tk

import pyppeteer
from lib.data_manager import DataManager
from lib.gologin_controller import GologinController
from lib.auto_pyppeteer_utils import (
    goto_page_with_url_containing,
    pp_copy_paste,
    pp_clear_input_field,
    set_auto_download_behavior,
)
from lib.text_utils import append_text_to_file, is_valid_email
from lib.srt_utils import read_srt_file
from lib.video_utils import *
from asyncio import sleep


class AutoFilm:
    def __init__(self, root):
        self.gc = GologinController(
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTk3OWJkMGViOWU2M2YzNDcwZDU5MjMiLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2NTlkMmQwOTc3NDJjNTdiYTg1ZWJkNzUifQ.gXbYZNg6NqNNTm301zzlg7cjsBedsB7hCadje8jzq8s",
        )

        self.pass_vbee = "1abcdxyz2"
        self.start = None
        self.end = None

        # GUI --------------------------------------------------------------------
        self.root = root
        self.root.title("Atrvf")

        self.dm = DataManager(root)

        self.dm.create_entry("Caption Path:", "caption_path", isBrowse=True)
        self.dm.create_entry(
            "Voice Folder Path:", "voice_folder_path", isFolder=True, isBrowse=True
        )
        self.dm.create_entry("Video Path:", "video_path", isBrowse=True)

        self.start_entry = self.dm.create_entry("Start at:", "start")
        self.dm.create_entry("End at:", "end")

        self.dm.create_button(
            "Create Caption", self.generate_and_download_vbee_captions, self.load_data
        )

    def load_data(self):
        self.caption_path = self.dm.get_entry_data("caption_path")
        self.voice_folder_path = self.dm.get_entry_data("voice_folder_path")
        self.video_path = self.dm.get_entry_data("video_path")
        self.start = int(self.dm.get_entry_data("start"))
        self.end = int(self.dm.get_entry_data("end"))

    async def generate_and_download_vbee_captions(self):
        await self.reset_gologin_and_open_new_profile()

        await self.load_temp_mail_page()

        await self.navigate_to_vbee_sign_in()

        temp_mail = await self.get_temp_mail()

        await self.fill_vbee_sign_in_form(temp_mail, self.pass_vbee)

        vbee_confirm_link = await self.fetch_vbee_confirm_link()

        self.page = await self.browser.newPage()
        await self.page.goto(vbee_confirm_link)

        append_text_to_file("vbee_mail.txt", temp_mail)

        await set_auto_download_behavior(self.page, self.voice_folder_path)

        await self.setup_initial_sign_in()
        await self.setup_voice()

        subtitles = read_srt_file(self.caption_path)
        await self.generate_all_subtitle_voices(subtitles)
        await self.choose_all_voice()
        await self.click_download_voice()
        await self.click_delete_all_voice()

        # await sleep(3000)

        # await self.gc.gl_stop()

    async def reset_gologin_and_open_new_profile(self):
        await self.gc.delete_all()
        await self.gc.create(auto_proxy=False)
        browser = await self.gc.connect(self.gc.gl_profile_id)
        self.browser = browser

    async def load_temp_mail_page(self):
        self.page = await self.browser.newPage()
        await self.page.goto("https://temp-mail.org/vi")

    async def navigate_to_vbee_sign_in(self):
        self.page = await self.browser.newPage()
        await self.page.goto("https://studio.vbee.vn/studio/text-to-speech")
        await sleep(2)

        button = await self.page.waitForSelector(
            "#__next > div > div:nth-child(1) > div > div > div.flex.flex-row-reverse > div.flex.items-start.justify-end > div.my-auto.block > div > button"
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

    async def get_temp_mail(self):
        self.page = await goto_page_with_url_containing(
            self.browser, "https://temp-mail.org"
        )

        email = None
        while email is None or not is_valid_email(email):
            email = await self.page.evaluate('document.getElementById("mail").value')
            if email is None:
                await sleep(1)
        if not email:
            return False

        return email

    async def fill_vbee_sign_in_form(self, email, password):
        self.page = await goto_page_with_url_containing(
            self.browser, "https://accounts.vbee.ai/"
        )

        await self.page.type("#email", email)
        await self.page.type("#password", password)
        await self.page.type("#passwordConfirm", password)

        login_btn = await self.page.waitForSelector('button[name="login"]')
        await login_btn.click()

    async def fetch_vbee_confirm_link(self):
        self.page = await goto_page_with_url_containing(
            self.browser, "https://temp-mail.org"
        )

        confirm_mail = await self.page.waitForSelector(
            "div.inbox-dataList > ul > li:nth-child(2) > div:nth-child(1) > a"
        )
        await confirm_mail.click()

        confirm_btn = await self.page.waitForSelector(
            "div.inbox-data-content > div.inbox-data-content-intro > div > div > div:nth-child(2) > a"
        )
        vbee_confirm_link = await self.page.evaluate(
            '(element) => element.getAttribute("href")', confirm_btn
        )

        return vbee_confirm_link

    async def close_initial_popups_on_sign_in(self):
        readed_checkbox = await self.page.waitForSelector(
            "div.dialog-checkbox > span > input"
        )
        await readed_checkbox.click()

        continue_btn = await self.page.waitForSelector("div.dialog-action > button")
        await continue_btn.click()

        dont_show_again_btn = await self.page.waitForSelector(
            ".not-show-again > label > span > input"
        )
        await dont_show_again_btn.click()
        await sleep(0.5)

        close_ad_btn = await self.page.waitForSelector(
            "div.MuiDialogContent-root > button"
        )
        await close_ad_btn.click()
        await sleep(0.5)

        skip_enter_text_btn = await self.page.waitForSelector(
            "#react-joyride-step-0 > div > div > div > div > button > div > div"
        )
        await skip_enter_text_btn.click()
        await sleep(0.5)

        skip_hightlight_to_listen = await self.page.waitForSelector(
            "p.MuiTypography-root.MuiTypography-body1.ignore-text"
        )
        await skip_hightlight_to_listen.click()
        await sleep(0.5)

    async def setup_initial_sign_in(self):
        await self.close_initial_popups_on_sign_in()

        await self.paste_text_into_editor("demo")
        await self.click_generate_voice()

        await self.close_popup_during_generation()
        await self.expand_download_tab()
        await self.choose_all_voice()
        await self.click_delete_all_voice()

        return

    async def close_popup_during_generation(self):
        close_popup_btn = await self.page.waitForSelector(
            ".dialog-content > h2 > button"
        )
        await close_popup_btn.click()
        await sleep(0.5)

    async def setup_voice(self):
        # Click choose voice
        choose_voice_btn = await self.page.waitForSelector(
            ".group-adjust-voice > button"
        )
        await choose_voice_btn.click()
        await sleep(0.5)

        # Click vn language checkbox
        await self.page.evaluate(
            "document.querySelector(\"input[value='vi-VN']\").click();"
        )
        await sleep(0.5)

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

    async def paste_text_into_title(self, text, number):
        title_input = await self.page.waitForSelector(".input-wrapper")
        await title_input.click()
        await sleep(0.5)

        limited_text = " ".join(text.split()[:5])
        await pp_clear_input_field(self.page)
        await pp_copy_paste(self.page, str(number) + limited_text)

    async def click_generate_voice(self):
        await self.page.evaluate(
            'document.querySelector(".request-info > button").click();'
        )
        await sleep(0.5)

    async def paste_text_into_editor(self, text):
        content_editor = await self.page.waitForSelector(
            ".DraftEditor-editorContainer > div > div"
        )
        await content_editor.click()
        await sleep(0.5)

        await pp_clear_input_field(self.page)
        await pp_copy_paste(self.page, text)

    async def generate_all_subtitle_voices(self, subtitles):
        filtered_subtitles = self.filter_subtitles_by_range(
            subtitles, self.start, self.end
        )
        for subtitle in filtered_subtitles:
            await self.generate_subtitle_voice(subtitle)
            if await self.is_not_enough_characters_popup_displayed():
                break

    async def generate_subtitle_voice(self, subtitle):

        await self.paste_text_into_title(subtitle["text"], subtitle["number"])

        await self.paste_text_into_editor(subtitle["text"])

        await self.click_generate_voice()

    async def is_not_enough_characters_popup_displayed(self):
        try:
            title_element = await self.page.waitForSelector(
                ".dialog-wrapper > .title", timeout=100
            )
            if title_element:
                title_text = await self.page.evaluate(
                    "(element) => element.textContent.trim()", title_element
                )
                return title_text in ["Not Enough Characters", "Không đủ ký tự"]
        except pyppeteer.errors.TimeoutError:
            pass
        return False

    async def filter_subtitles_by_range(self, subtitles, start, end):
        return [
            subtitle for subtitle in subtitles if start <= subtitle["number"] <= end
        ]

    async def click_delete_all_voice(self):
        delete_all_btn = await self.page.waitForSelector(
            ".MuiTableCell-root .delete-button:nth-child(2)"
        )
        await delete_all_btn.click()

        confirm_yes_btn = await self.page.waitForSelector(".content button")
        await confirm_yes_btn.click()

        return

    async def choose_all_voice(self):
        await self.await_voice_generation_completion()

        while True:
            try:
                # Wait for the next button and header checkbox
                next_page_btn = await self.page.waitForSelector(
                    'button[aria-label="Go to next page"]:not([disabled])', timeout=100
                )
                header_checkbox = await self.page.waitForSelector(
                    ".header-checkbox .PrivateSwitchBase-input"
                )

                # Click on the header checkbox and the next button
                await header_checkbox.click()
                await next_page_btn.click()
            except pyppeteer.errors.TimeoutError:
                print("Next page button is disabled.")
                break

            return

    async def expand_download_tab(self):
        expand_icon = await self.page.querySelector(
            'button > [data-testid="KeyboardArrowDownIcon"]'
        )
        if expand_icon:
            await expand_icon.click()
            await sleep(0.5)
        else:
            pass

        return

    async def click_download_voice(self):
        download_btn = await self.page.waitForSelector(
            ".MuiTableCell-root .download-button"
        )
        await download_btn.click()
        return

    async def await_voice_generation_completion(self):
        await self.page.waitForSelector(".request-info > .MuiTypography-body1")
        return


def main():
    root = Tk()
    app = AutoFilm(root)
    root.mainloop()


if __name__ == "__main__":
    main()
