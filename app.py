import app
import requests
import time
from events.input import Buttons, BUTTON_TYPES
from app_components import clear_background

class SpeedTest(app.App):
    def __init__(self):
        self.button_states = Buttons(self)
        url = "http://ipv4.download.thinkbroadband.com/5GB.zip"
        self.dl_speed = "Downloading..."
        self.dl_speed = download_and_discard(url)

    def update(self, delta):
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            # The button_states do not update while you are in the background.
            # Calling clear() ensures the next time you open the app, it stays open.
            # Without it the app would close again immediately.
            self.button_states.clear()
            self.minimise()

    def draw(self, ctx):
        clear_background(ctx)
        ctx.save()
        ctx.rgb(0.2,0,0).rectangle(-120,-120,240,240).fill()
        ctx.rgb(1,0,0).move_to(-110,0).text(f"{self.dl_speed}")
        ctx.restore()

def download_and_discard(url):
    print("starting download")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_bytes = 0
        start_time = time.time()
        end_time = time.time()
        for chunk in r.iter_content(chunk_size=8192): # Probably about as much memory as we want to buffer
            if chunk:
                total_bytes += len(chunk)
            if total_bytes % 81920 == 0:
                end_time = time.time()
                if end_time - start_time > 5:
                    break
        end_time = time.time()
        duration = end_time - start_time
        speed = total_bytes / duration / 1024  # Speed in KB/s
        print(duration)
        print(speed)
        return "{:,.3f}".format(speed) + " KB/s"

__app_export__ = SpeedTest