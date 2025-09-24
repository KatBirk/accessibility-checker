import tkinter as tk
from tkinter import ttk, messagebox

def show_login():
    def login():
        username = username_entry.get()
        password = password_entry.get()
        
        if username and password:
            login_window.destroy()
            import main
            main.show_main_window(version="paid")
        else:
            messagebox.showerror("Error", "Please enter both username and password")
    
    def free_login():
        login_window.destroy()
        import main
        main.show_main_window(version="free")

    def on_enter(event):
        login()

    login_window = tk.Tk()
    login_window.title("Login - AAaS")
    login_window.geometry("300x350")
    login_window.resizable(False, False)

    login_window.eval('tk::PlaceWindow . center')

    title_label = tk.Label(login_window, text="AAaS Login", font=("Arial", 16, "bold"))
    title_label.pack(pady=15)

    username_label = tk.Label(login_window, text="Username:")
    username_label.pack()
    username_entry = tk.Entry(login_window, width=20)
    username_entry.pack(pady=8)

    password_label = tk.Label(login_window, text="Password:")
    password_label.pack()
    password_entry = tk.Entry(login_window, show="*", width=20)
    password_entry.pack(pady=8)

    login_button = tk.Button(
        login_window, 
        text="Login (Paid Version)", 
        command=login, 
        width=20, 
        height=2,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 10, "bold")
    )
    login_button.pack(pady=15)
    
    free_button = tk.Button(
        login_window, 
        text="Login as Free User", 
        command=free_login, 
        width=20, 
        height=2,
        bg="#2196F3",
        fg="white",
        font=("Arial", 10, "bold")
    )
    free_button.pack(pady=10)

    username_entry.bind('<Return>', on_enter)
    password_entry.bind('<Return>', on_enter)

    username_entry.focus()

    login_window.mainloop()

if __name__ == "__main__":
    show_login()