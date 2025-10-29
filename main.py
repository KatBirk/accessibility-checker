from playwright.sync_api import sync_playwright
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from axe_core_python.sync_playwright import Axe
import json
import time
import tkinter as tk
from tkinter import *
from tkinter import ttk
import os, sys, logging
from stopwatch import Stopwatch
import sitemap
from tkinter import Button, messagebox
import webbrowser
import threading
import http.server
import socketserver

# Set up myapp.log
if getattr(sys, "frozen", False):  # place log in the same folder as the exe
    base_dir = (
        sys._MEIPASS if hasattr(sys, "_MEIPASS") else os.path.dirname(sys.executable)
    )
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

log_file = os.path.join(base_dir, "myapp.log")

logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("main")


# Used for time estimation
stopwatch = Stopwatch()


websiteToBESCANNED = ""
violations = 0
vioCount = 0


def testWebsite(url):
    logger.debug(url)
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
        html_url = f"http://localhost:8000/report.html"
        webbrowser.open(html_url)


def start_server(port=8000):
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


def start_progress():
    logger.debug("progress bar started")
    progress.start()
    global vioCount
    vioCount = 0
    data = sitemap.sitemapsFromUrl(websiteToBESCANNED)
    data = data[:200]  # limit the amount of stuff to scan
    total_urls = len(data)
    if total_urls == 0:
        logger.debug("No URLs to process.")
        laban.config(text="No URLs found.")
        progress.stop()
        return

    urls_processed = 0
    total_time_elapsed = 0.0
    # Note that too many worker threads will make your computer freeze or google flags you
    # Not talking from experince
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(testWebsite, url): url for url in data}

        # Iterate over completed futures
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]

            try:
                stopwatch.start()  # Start timing for the current result processing block
                violation_count_for_url = future.result()
                vioCount += violation_count_for_url
                stopwatch.stop()

                urls_processed += 1

                percentage = (urls_processed * 100) / total_urls
                progress["value"] = percentage

                if urls_processed == 1:
                    start_time = time.time()  # Record start time of the first result

                current_wall_time = time.time()
                elapsed_wall_time = (
                    current_wall_time - start_time if "start_time" in locals() else 0
                )

                avg_time_per_url = (
                    elapsed_wall_time / urls_processed if urls_processed > 0 else 0
                )

                if avg_time_per_url > 0:
                    remaining_urls = total_urls - urls_processed
                    estimated_remaining_seconds = remaining_urls * avg_time_per_url
                    estimated_remaining_minutes = int(estimated_remaining_seconds / 60)

                    laban.config(
                        text=f"estimated time: {estimated_remaining_minutes} min "
                    )
                else:
                    laban.config(
                        text=f"Progressing... {urls_processed}/{total_urls} URLs"
                    )

                root.update_idletasks()  # Ensures GUI updates are drawn

            except Exception as exc:
                logger.error(f"{url} generated an exception: {exc}")

        root.update_idletasks()  # Ensures GUI updates are drawn
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
        about_text = (
            "Accessibility as a Service\n\n"
            + "A tool for checking website accessibility\n"
            + "using Playwright and axe-core.\n\n"
            + f"Current Version: {version.upper()}"
        )
        tk.messagebox.showinfo("About AAaS", about_text)

    help_menu.add_command(label="About", command=show_about)

    if version == "paid":
        version_label = tk.Label(
            root,
            text="🌟 PAID VERSION 🌟",
            font=("Arial", 12, "bold"),
            fg="gold",
            bg="darkgreen",
            padx=10,
            pady=5,
        )
    else:
        version_label = tk.Label(
            root,
            text="📝 FREE VERSION",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="blue",
            padx=10,
            pady=5,
        )

    version_label.pack(pady=(5, 10))

    w = Label(root, text="AAaS!")
    w.pack()

    progress = ttk.Progressbar(
        root, orient="horizontal", length=300, mode="determinate"
    )
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

    server = start_server(port=8000)  # serves current folder

    login.show_login()
