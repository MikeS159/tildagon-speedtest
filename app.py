import app
import requests
import time
import usocket as socket
from events.input import Buttons, BUTTON_TYPES
from app_components import clear_background

class SpeedTest(app.App):
    def __init__(self):
        self.button_states = Buttons(self)
        url = "http://ash-speed.hetzner.com/100MB.bin"
        self.dl_speed = "Downloading..."
        self.dl_speed = download_and_discard(url)

    def update(self, delta):
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            # The button_states do not update while you are in the background.
            # Calling clear() ensures the next time you open the app, it stays open.
            # Without it the app would close again immediately.
            self.button_states.clear()
            self.close()

    def draw(self, ctx):
        clear_background(ctx)
        ctx.save()
        ctx.rgb(0.2,0,0).rectangle(-120,-120,240,240).fill()
        ctx.rgb(1,0,0).move_to(-110,0).text(f"{self.dl_speed}")
        ctx.restore()

def download_and_discard(url):
    print("Starting download")
    start_time = time.ticks_ms()
    total_bytes = 0

    try:
        # Parse the URL
        if not url.startswith('http://'):
            raise ValueError("Only HTTP URLs are supported")

        url = url[7:]  # Remove 'http://'
        host, _, path = url.partition('/')
        path = '/' + path

        # Resolve the IP address of the host
        addr_info = socket.getaddrinfo(host, 80)
        if not addr_info:
            raise Exception("Unable to resolve host")
        addr = addr_info[0][-1]

        # Create a socket and connect
        s = socket.socket()
        s.connect(addr)

        # Send the HTTP request
        request = "GET {} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n".format(path, host)
        s.send(request.encode())

        # Read the response headers
        while True:
            line = s.readline()
            print(line)  # Debug: Print header lines
            if line == b"\r\n":
                break

        # Read the response content in chunks
        while True:
            chunk = s.recv(16384)  # Use recv to handle chunks
            if not chunk:
                break
            total_bytes += len(chunk)
            #print("Read chunk of size:", len(chunk))  # Debug: Print chunk size
            end_time = time.ticks_ms()
            if time.ticks_diff(end_time, start_time) > 5000: 
                break

    except Exception as e:
        print("An error occurred:", e)
    
    finally:
        s.close()

    print("Done download")
    end_time = time.time()
    duration = time.ticks_diff(time.ticks_ms(), start_time) / 1000  
    if duration is 0:
        duration = 0.001
    speed = total_bytes / duration / 1000  # Speed in KB/s
    print("Duration:", duration)
    print("Speed:", speed)
    return "{:,.3f}".format(speed) + " KB/s\n""{:,.3f}".format(speed*8) + " Kb/s"

__app_export__ = SpeedTest
