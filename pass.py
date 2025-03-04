import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import getpass
import threading

# Function to get saved Wi-Fi passwords
def get_wifi_passwords(progress_callback=None):
    try:
        output = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('cp850', errors='ignore')
        profiles = [line.split(":")[1].strip() for line in output.split('\n') if "Tous les utilisateurs" in line]

        if not profiles:
            return "No Wi-Fi profiles found."

        wifi_passwords = []
        total_profiles = len(profiles)
        for index, profile in enumerate(profiles):
            try:
                profile_output = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', profile, 'key=clear']).decode('cp850', errors='ignore')
                password = None
                for line in profile_output.split('\n'):
                    if "Contenu de la clé" in line:
                        password = line.split(":")[1].strip()
                        break
                wifi_passwords.append(f"SSID: {profile}, Password: {password if password else '<No Password>'}")
            except subprocess.CalledProcessError:
                wifi_passwords.append(f"SSID: {profile}, Password: <Error Retrieving>")

            # Update progress
            if progress_callback:
                progress = int((index + 1) / total_profiles * 100)
                progress_callback(progress)

        return "\n".join(wifi_passwords)

    except Exception as e:
        return f"Error retrieving Wi-Fi passwords: {e}"

# Function to update progress bar color
def update_progress_color(progress):
    if progress < 33:
        progress_bar.configure(style="red.Horizontal.TProgressbar")
    elif progress < 66:
        progress_bar.configure(style="yellow.Horizontal.TProgressbar")
    else:
        progress_bar.configure(style="green.Horizontal.TProgressbar")

# Function to animate progress bar
def animate_progress_bar(target_value):
    current_value = progress_bar['value']
    if current_value < target_value:
        progress_bar['value'] += 1
        update_progress_color(progress_bar['value'])
        root.after(20, animate_progress_bar, target_value)  # Adjust speed here
    elif current_value == 100:
        # Pulsating effect when progress reaches 100%
        pulsate_progress_bar()

# Function to create a pulsating effect
def pulsate_progress_bar():
    current_color = progress_bar.cget("style")
    if current_color == "green.Horizontal.TProgressbar":
        progress_bar.configure(style="pulse.Horizontal.TProgressbar")
    else:
        progress_bar.configure(style="green.Horizontal.TProgressbar")
    root.after(500, pulsate_progress_bar)  # Adjust pulsation speed here

# Function to display Wi-Fi passwords
def show_wifi_passwords():
    status_label.config(text="Fetching Wi-Fi passwords... ⏳", style="status.TLabel")
    progress_bar['value'] = 0  # Reset progress bar
    progress_bar['maximum'] = 100  # Set maximum value
    root.update_idletasks()  # Force update UI

    def update_progress(progress):
        animate_progress_bar(progress)

    def fetch_passwords():
        try:
            wifi_passwords = get_wifi_passwords(progress_callback=update_progress)
            password_text.delete(1.0, tk.END)
            password_text.insert(tk.INSERT, wifi_passwords)
            status_label.config(text="Wi-Fi Passwords Loaded ✅", style="success.TLabel")
        except Exception as e:
            status_label.config(text=f"Error: {str(e)}", style="error.TLabel")
        finally:
            progress_bar['value'] = 100  # Ensure progress bar reaches 100%

    # Run the password retrieval in a separate thread
    threading.Thread(target=fetch_passwords, daemon=True).start()

# Function to display current user
def show_current_user():
    password_text.delete(1.0, tk.END)
    password_text.insert(tk.INSERT, f"Current User: {getpass.getuser()}")
    status_label.config(text="Current User Displayed ✅", style="success.TLabel")

# Function to toggle theme
def toggle_theme():
    global is_dark_mode
    is_dark_mode = not is_dark_mode

    if is_dark_mode:
        root.configure(bg="#2C3E50")  # Dark Navy background
        style.configure("TFrame", background="#7F8C8D")  # Gray frame
        style.configure("TLabel", foreground="white", background="#2C3E50")  # White text on dark navy
        style.configure("TButton", foreground="white", background="#34495E")  # Navy button color
        style.configure("status.TLabel", foreground="white", background="#2C3E50")  # Status label
        style.configure("success.TLabel", foreground="white", background="#2C3E50")  # Success label
        style.configure("error.TLabel", foreground="red", background="#2C3E50")  # Error label
        status_label.config(text="Current Theme: Dark Navy & Gray", style="status.TLabel")
    else:
        root.configure(bg="#800020")  # Burgundy background
        style.configure("TFrame", background="#800020")  # Burgundy frame
        style.configure("TLabel", foreground="white", background="#34495E")  # White text on Burgundy
        style.configure("TButton", foreground="white", background="#34495E")  # Darker navy button color
        style.configure("status.TLabel", foreground="white", background="#34495E")  # Status label
        style.configure("success.TLabel", foreground="white", background="#34495E")  # Success label
        style.configure("error.TLabel", foreground="red", background="#34495E")  # Error label
        status_label.config(text="Current Theme: Burgundy & Gray", style="status.TLabel")

# Function to search for a specific SSID
def search_ssid():
    search_query = search_entry.get().strip().lower()
    if not search_query:
        return

    # Get all Wi-Fi passwords
    wifi_passwords = get_wifi_passwords()

    # Filter SSID matches
    filtered_wifi = [line for line in wifi_passwords.split('\n') if search_query in line.lower()]

    # Display filtered results
    password_text.delete(1.0, tk.END)
    if filtered_wifi:
        password_text.insert(tk.INSERT, "\n".join(filtered_wifi))
    else:
        password_text.insert(tk.INSERT, "No matching SSID found.")

# Create main window
root = tk.Tk()
root.title("Wi-Fi Password Viewer 🔐")
root.geometry("1700x700")  # Increased window size
root.minsize(600, 400)  # Prevents window from being too small
root.configure(bg="#2C3E50")  # Set dark navy background

# Style
style = ttk.Style()
style.theme_use("clam")  # Use a modern theme
style.configure("TButton", font=("Segoe UI", 12), padding=5)
style.configure("TLabel", font=("Segoe UI", 12), background="#7F8C8D", foreground="white")  # Gray background for labels
style.configure("TFrame", background="#7F8C8D")  # Gray frame

# Custom progress bar styles
style.configure("red.Horizontal.TProgressbar", background="red")
style.configure("yellow.Horizontal.TProgressbar", background="yellow")
style.configure("green.Horizontal.TProgressbar", background="green")
style.configure("pulse.Horizontal.TProgressbar", background="lime")  # Pulsating effect color

# Additional styles for status messages
style.configure("status.TLabel", foreground="white", background="#2C3E50")
style.configure("success.TLabel", foreground="white", background="#2C3E50")
style.configure("error.TLabel", foreground="red", background="#2C3E50")

# Grid Configuration (Ensures Full Fit)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Frame for Layout
frame = ttk.Frame(root, padding=10)
frame.grid(row=0, column=0, sticky="nsew")

# Make frame expandable
frame.grid_rowconfigure(0, weight=0)
frame.grid_rowconfigure(1, weight=0)
frame.grid_rowconfigure(2, weight=0)
frame.grid_rowconfigure(3, weight=0)
frame.grid_rowconfigure(4, weight=1)  # Allow content area to expand
frame.grid_columnconfigure(0, weight=1)

# Search Entry and Button
search_label = ttk.Label(frame, text="Search SSID:", style="TLabel")
search_label.grid(row=0, column=0, pady=10, padx=10, sticky="w")

search_entry = ttk.Entry(frame, font=("Segoe UI", 12))
search_entry.grid(row=0, column=1, pady=10, padx=10, sticky="ew")

search_button = ttk.Button(frame, text="🔍 Search", command=search_ssid)
search_button.grid(row=0, column=2, pady=10, padx=10, sticky="ew")

# Scrollable Text Area (Expands with Window)
password_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Consolas", 11))
password_text.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

# Progress Bar
progress_bar = ttk.Progressbar(frame, mode="determinate", style="red.Horizontal.TProgressbar")
progress_bar.grid(row=2, column=0, columnspan=3, pady=5, sticky="ew")

# Buttons (Expands Horizontally)
wifi_button = ttk.Button(frame, text="🔍 Show Wi-Fi Passwords", command=show_wifi_passwords)
wifi_button.grid(row=3, column=0, pady=5, padx=5, sticky="ew")

user_button = ttk.Button(frame, text="👤 Show Current User", command=show_current_user)
user_button.grid(row=3, column=1, pady=5, padx=5, sticky="ew")

theme_button = ttk.Button(frame, text="🌙 Toggle Theme", command=toggle_theme)
theme_button.grid(row=3, column=2, pady=5, padx=5, sticky="ew")

# Status Label (Stays at Bottom)
status_label = ttk.Label(frame, text="Ready...", anchor="center", style="status.TLabel")
status_label.grid(row=4, column=0, columnspan=3, pady=5, sticky="ew")

# Dark Mode Flag
is_dark_mode = True

# Run the application
root.mainloop()