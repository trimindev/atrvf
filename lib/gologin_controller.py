from pyppeteer import connect
from asyncio import run
from gologin import GoLogin


class GologinController:
    def __init__(
        self,
        token=None,
    ):
        self.token = token
        self.gl = GoLogin({"token": self.token})

    async def open(self, profile_id):
        self.gl.setProfileId(profile_id)
        debugger_address = self.gl.start()
        browser = await connect(
            browserURL="http://" + debugger_address, defaultViewport=None
        )
        # await self.gl.normalizePageView(page)

        return browser

    async def create(self, auto_proxy=False, proxy=False):
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

    async def stop(self):
        await self.browser.close()
        self.gl.stop()

    async def delete_all(self):
        profiles = self.gl.profiles()["profiles"]
        for profile in profiles:
            profile_id = profile["id"]
            self.gl.delete(profile_id)


async def main():
    pass


if __name__ == "__main__":
    run(main())
