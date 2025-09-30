from playwright.sync_api import sync_playwright
from axe_core_python.sync_playwright import Axe
import json
import time
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import Button
import logging
from stopwatch import Stopwatch
import sitemap

logger = logging.getLogger("main")
logging.basicConfig(filename='myapp.log', level=logging.DEBUG)

stopwatch = Stopwatch()
websiteToBESCANNED = ""
violations = 0
vioCount = 0

def testWebsite(url):
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch()
        page = browser.new_page()
        page.goto(url)
        results = axe.run(page)
        browser.close()
        global violations
        violations = results["violations"]
        with open("violations.json", "w") as f:
            json.dump(violations, f, indent=4)
        return len(violations)



def start_progress():
    logger.debug("progress bar started")
    progress.start()
    global vioCount
    vioCount = 0
    data = sitemap.sitemapsFromUrl(websiteToBESCANNED)
    data = data[-100:]

    for i, url in enumerate(data):
        logger.debug(url)

        stopwatch.start()
        vioCount = vioCount + testWebsite(url)
        stopwatch.stop()
        percentage = (i + 1) * 100 / len(data)
        # Update GUI elements
        progress["value"] = percentage
        laban.config(text=f"estimated time:{int(((len(data)*stopwatch.elapsed-(i*stopwatch.elapsed)))/60)} min ")
        stopwatch.reset()
        root.update_idletasks()  # Ensures GUI updates are drawn

    laban.config(text=f"{vioCount} violations found.")
    progress.stop()


root = tk.Tk()
w = Label(root, text="AaaS!")
w.pack()

progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress.pack(pady=20)

# Button to start progress
start_button = tk.Button(root, text="Start Progress", command=start_progress)
start_button.pack(pady=10)

axe = Axe()
urls = [
    "https://www.google.com",
    "https://www.berkshirehathaway.com",
    "https://www.microsoft.com",
    "https://www.playwright.dev",
    "https://www.op.europa.eu/en/web/webguide",
    "https://www.github.com",
    "https://www.wikipedia.org",
    "https://www.sdu.dk",
]
label = tk.Label(root, text="Selected Item: ")
label.pack(pady=10)
combo_box = ttk.Combobox(root, values=urls, state="readonly")
combo_box.pack(pady=5)
combo_box.set("Please Select website")


def select(event):
    selected_item = combo_box.get()
    global websiteToBESCANNED
    websiteToBESCANNED = selected_item
    label.config(text="Selected Item: " + selected_item)


combo_box.bind("<<ComboboxSelected>>", select)
# Create a label
laban = tk.Label(root, text="")
laban.pack(pady=10)


# for i in range(len(urls)):
#    testWebsite(i)

# print(f"{len(violations)} violations found.")

root.mainloop()
