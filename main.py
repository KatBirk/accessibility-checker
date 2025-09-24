from playwright.sync_api import sync_playwright
from axe_core_python.sync_playwright import Axe
import json
import time
import tkinter as tk
from tkinter import *
from tkinter import ttk
import webbrowser
import threading
import http.server
import socketserver
from tkinter import Button, messagebox


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

        html_url = f"http://localhost:8000/report.html"
        webbrowser.open(html_url)



def start_server(port=8000):
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd

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

    server = start_server(port=8000)  # serves current folder

    login.show_login()
