from playwright.sync_api import sync_playwright
from axe_core_python.sync_playwright import Axe
import json
import time
import tkinter as tk
from tkinter import *
from tkinter import ttk
import logging
from stopwatch import Stopwatch
import sitemap
from tkinter import Button, messagebox

logger = logging.getLogger("main")
logging.basicConfig(filename="myapp.log", level=logging.DEBUG)

# Used for time estimation
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
        laban.config(
            text=f"estimated time:{int(((len(data)*stopwatch.elapsed-(i*stopwatch.elapsed)))/60)} min "
        )
        stopwatch.reset()
        root.update_idletasks()  # Ensures GUI updates are drawn

    laban.config(text=f"{vioCount} violations found.")
    progress.stop()

def show_main_window(version="free"):
    global root, progress, start_button, axe, urls, label, combo_box, laban

    root = tk.Tk()

    if version == "paid":
        root.title("AAaS - Accessibility as a Service (Paid Version)")
    else:
        root.title("AAaS - Accessibility as a Service (Free Version)")

    menubar = tk.Menu(root)
    root.config(menu=menubar)

    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)

    def logout():
        root.quit()
        root.destroy()
        import login
        login.show_login()

    def exit_app():
        root.quit()
        root.destroy()

    file_menu.add_command(label="Logout", command=logout)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=exit_app)

    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)

    def show_about():
        about_text = "Accessibility as a Service\n\n" + \
                    "A tool for checking website accessibility\n" + \
                    "using Playwright and axe-core.\n\n" + \
                    f"Current Version: {version.upper()}"
        tk.messagebox.showinfo("About AAaS", about_text)

    help_menu.add_command(label="About", command=show_about)

    if version == "paid":
        version_label = tk.Label(root, text="🌟 PAID VERSION 🌟",
                               font=("Arial", 12, "bold"),
                               fg="gold", bg="darkgreen", padx=10, pady=5)
    else:
        version_label = tk.Label(root, text="📝 FREE VERSION",
                               font=("Arial", 12, "bold"),
                               fg="white", bg="blue", padx=10, pady=5)

    version_label.pack(pady=(5,10))

    w = Label(root, text="AAaS!")
    w.pack()

    progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=20)

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
    laban = tk.Label(root, text="")
    laban.pack(pady=10)

    def on_closing():
        root.quit()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    import login
    login.show_login()
