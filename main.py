from playwright.sync_api import sync_playwright
from axe_core_python.sync_playwright import Axe
import json
import time
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import Button

websiteToBESCANNED = ""
violations = 0

def testWebsite():
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch()
        page = browser.new_page()
        global websiteToBESCANNED
        page.goto(websiteToBESCANNED)
        results = axe.run(page)
        browser.close()
        global violations
        violations = results["violations"]
        with open("violations.json", "w") as f:
            json.dump(violations, f, indent=4)

def start_progress():
    progress.start()

    for i in range(95):
        time.sleep(0.06)
        progress["value"] = i
        root.update_idletasks()
    testWebsite()
    for i in range(95,101):
        time.sleep(0.03)
        progress["value"] = i
        root.update_idletasks()

    laban.config(text=f"{len(violations)} violations found.")
    progress.stop()


root = tk.Tk()
w = Label(root, text="AAaS!")
w.pack()

progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress.pack(pady=20)

# Button to start progress
start_button = tk.Button(root, text="Start Progress", command=start_progress)
start_button.pack(pady=10)

axe = Axe()
urls = [
    "https://www.google.com/",
    "https://www.berkshirehathaway.com/",
    "https://www.microsoft.com/",
    "https://www.playwright.dev/",
    "https://www.op.europa.eu/en/web/webguide/",
    "https://www.github.com/",
    "https://www.wikipedia.org/",
    "https://www.sdu.dk/en",
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
