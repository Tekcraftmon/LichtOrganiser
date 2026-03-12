import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import shutil
import threading

# === GLOBALS ===
selected_items = []
target_directory = None
moved_files = []
dark_mode = False

# === FUNCTIONS ===
def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    apply_theme()

def choose_directory():
    global target_directory
    target_directory = filedialog.askdirectory()
    if target_directory:
        load_items_list()
        status_label.config(text=f"Target directory: {target_directory}")

def load_items_list():
    file_listbox.delete(0, tk.END)
    items = os.listdir(target_directory)
    for item in items:
        file_listbox.insert(tk.END, item)

def select_all_items():
    file_listbox.select_set(0, tk.END)

def deselect_all_items():
    file_listbox.select_clear(0, tk.END)

def move_file(file_path, base_directory):
    if not os.path.isfile(file_path):
        return
    filename = os.path.basename(file_path)
    extension = os.path.splitext(filename)[1][1:].upper()
    if extension == "":
        extension = "NO_EXTENSION"
    new_folder = os.path.join(base_directory, extension)
    os.makedirs(new_folder, exist_ok=True)
    new_file_path = os.path.join(new_folder, filename)
    counter = 1
    while os.path.exists(new_file_path):
        name, ext = os.path.splitext(filename)
        new_file_path = os.path.join(new_folder, f"{name}_{counter}{ext}")
        counter += 1
    shutil.move(file_path, new_file_path)
    moved_files.append((file_path, new_file_path))

def organise_worker(items_to_process):
    for idx, item in enumerate(items_to_process):
        item_path = os.path.join(target_directory, item)
        if os.path.isfile(item_path):
            move_file(item_path, target_directory)
        elif os.path.isdir(item_path):
            for root, dirs, files in os.walk(item_path):
                for f in files:
                    move_file(os.path.join(root, f), target_directory)
        window.after(0, lambda i=idx: progress_var.set(int(((i+1)/len(items_to_process))*100)))
    window.after(0, lambda: status_label.config(text="Organisation complete!"))
    window.after(0, lambda: messagebox.showinfo("Done", "Selected files/folders organised successfully!"))

def organise_selected():
    global selected_items
    if not target_directory:
        messagebox.showwarning("No Directory", "Please choose a target directory first.")
        return
    selected_indices = file_listbox.curselection()
    if not selected_indices:
        messagebox.showwarning("No Selection", "No items selected. You can also use 'Organise All'.")
        return
    selected_items = [file_listbox.get(i) for i in selected_indices]
    threading.Thread(target=organise_worker, args=(selected_items,)).start()

def organise_all():
    if not target_directory:
        messagebox.showwarning("No Directory", "Please choose a target directory first.")
        return
    all_items = os.listdir(target_directory)
    threading.Thread(target=organise_worker, args=(all_items,)).start()

def reset_files():
    if not target_directory:
        messagebox.showwarning("No Directory", "Please choose a target directory first.")
        return
    if not moved_files:
        messagebox.showinfo("Nothing to Undo", "No files have been moved yet.")
        return
    try:
        for original_path, moved_path in moved_files:
            if os.path.exists(moved_path):
                os.makedirs(os.path.dirname(original_path), exist_ok=True)
                shutil.move(moved_path, original_path)
        moved_files.clear()
        status_label.config(text="Reset complete!")
        messagebox.showinfo("Reset Complete", "Files moved back successfully!")
    except Exception as e:
        status_label.config(text="Error occurred")
        messagebox.showerror("Error", f"An error occurred during reset:\n{e}")

def apply_theme():
    bg = '#1E1E1E' if dark_mode else '#f5f5f5'
    fg = '#ffffff' if dark_mode else '#333333'
    window.configure(bg=bg)
    logo_label.configure(bg=bg, fg='#1E90FF')
    status_label.configure(bg=bg)
    listbox_frame.configure(bg=bg)
    file_listbox.configure(bg='#2E2E2E' if dark_mode else 'white', fg='white' if dark_mode else 'black', selectbackground='#007ACC')
    btn_frame.configure(bg=bg)
    organise_btn_frame.configure(bg=bg)

# === GUI SETUP ===
window = tk.Tk()
window.title("LichtManager 2.0")
window.geometry("600x650")
window.resizable(True, True)

# Logo
logo_label = tk.Label(window, text="LichtManager 2.0", font=("Arial", 28, "bold"), bg="#f5f5f5", fg="#1E90FF")
logo_label.pack(pady=15)

# Theme toggle
theme_btn = ttk.Button(window, text="Toggle Dark/Light Mode", command=toggle_theme, style='Utility.TButton')
theme_btn.pack(pady=5)

# Choose Directory
choose_btn = ttk.Button(window, text="Choose Target Directory", command=choose_directory, style='Utility.TButton')
choose_btn.pack(pady=5)

# Listbox
listbox_frame = tk.Frame(window, bg="#f5f5f5")
listbox_frame.pack(pady=10)
file_listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, width=75, height=15, font=('Arial', 11))
file_listbox.pack()

# Select/Deselect
btn_frame = tk.Frame(window, bg="#f5f5f5")
btn_frame.pack(pady=5)
select_all_btn = ttk.Button(btn_frame, text="Select All", command=select_all_items, style='Utility.TButton')
select_all_btn.pack(side=tk.LEFT, padx=5)
deselect_all_btn = ttk.Button(btn_frame, text="Deselect All", command=deselect_all_items, style='Utility.TButton')
deselect_all_btn.pack(side=tk.LEFT, padx=5)

# Organise buttons and progress
organise_btn_frame = tk.Frame(window, bg="#f5f5f5")
organise_btn_frame.pack(pady=10)
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(organise_btn_frame, orient='horizontal', length=300, mode='determinate', variable=progress_var)
progress_bar.pack(pady=5)
organise_selected_btn = ttk.Button(organise_btn_frame, text="Organise Selected", command=organise_selected, style='Action.TButton')
organise_selected_btn.pack(side=tk.LEFT, padx=10)
organise_all_btn = ttk.Button(organise_btn_frame, text="Organise All (Auto)", command=organise_all, style='Action.TButton')
organise_all_btn.pack(side=tk.LEFT, padx=10)
reset_btn = ttk.Button(organise_btn_frame, text="Undo / Reset", command=reset_files, style='Reset.TButton')
reset_btn.pack(side=tk.LEFT, padx=10)

# Status
status_label = tk.Label(window, text="", fg="#4CAF50", font=("Arial", 10, "italic"), bg="#f5f5f5")
status_label.pack(pady=5)

# Exit
exit_btn = ttk.Button(window, text="Exit", command=window.quit, style='Exit.TButton')
exit_btn.pack(pady=10)

# Apply theme after widgets
apply_theme()

window.mainloop()

