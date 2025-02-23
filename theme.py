import os
import json
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import tkinter.font as tkFont
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize main window
root = tk.Tk()
root.title("BBS Theme Tool")
root.geometry("700x600")
root.configure(bg="black")

print("Initializing application...")

# Load custom font
def load_custom_font():
    print("Loading custom font...")
    font_path = "assets/font.ttf"
    if os.path.exists(font_path):
        return tkFont.Font(family="Minecraft", size=16)
    return tkFont.Font(family="Arial", size=12)

custom_font = load_custom_font()

# Load custom icon
def load_custom_icon():
    print("Loading custom icon...")
    icon_path = "assets/myicon.png"
    if os.path.exists(icon_path):
        root.iconphoto(True, tk.PhotoImage(file=icon_path))

load_custom_icon()

# Load checkbox images
print("Loading checkbox images...")
checkbox_checked = ImageTk.PhotoImage(Image.open("assets/checkbox_check.png").resize((16, 16)))
checkbox_unchecked = ImageTk.PhotoImage(Image.open("assets/checkbox_nocheck.png").resize((16, 16)))

# Load reload image
try:
    reload_image = ImageTk.PhotoImage(Image.open("assets/reload.png").resize((20, 20)))
except FileNotFoundError:
    print("Error: reload.png not found in assets folder.  Using a placeholder.")
    reload_image = None  # Or use a default image

# Global variables
import_mode = tk.BooleanVar(value=False)
export_mode = tk.BooleanVar(value=False)

# UI Frames
frame_top = tk.Frame(root, bg="black")
frame_top.pack(pady=10, fill="x")  #  Ensure it fills the width

frame_middle = tk.Frame(root, bg="black")
frame_middle.pack()

frame_bottom = tk.Frame(root, bg="black")
frame_bottom.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

# Path selection
entry_path = tk.Entry(frame_top, font=custom_font, width=40)
entry_path.grid(row=0, column=0, padx=5, sticky="w")  # Stick to the left

def select_config_path():
    print("Selecting config path...")
    path = filedialog.askdirectory(title="Select Config Path")
    if path and "bbs" in os.path.basename(path):
        entry_path.delete(0, tk.END)
        entry_path.insert(0, path)
        update_ui()
    else:
        messagebox.showerror("Error", "Please select a valid /config/bbs directory.")

def update_ui():
    global listbox_theme, entry_export_name

    print("Updating UI...")
    config_path = entry_path.get()

    if not config_path:
        print("No config path selected.")
        if 'listbox_theme' in globals():
            try:
                listbox_theme.destroy()
            except Exception as e:
                print(f"Error deleting listbox: {e}")
        try:
            search_frame.pack_forget()
            entry_export_frame.pack_forget()
        except Exception as e:
            print(f"Error packing frames: {e}")
        return

    theme_path = os.path.join(config_path, "theme")

    if import_mode.get():
        themes = get_available_themes(theme_path)
        search_term = search_entry.get().lower()
        filtered_themes = [theme for theme in themes if search_term in theme.lower()]

        # Check if listbox_theme exists and destroy if it does
        if 'listbox_theme' in globals():
            try:
                listbox_theme.destroy()
            except Exception as e:
                print(f"Error destroying old listbox: {e}")

        # Create a new listbox_theme
        listbox_theme = tk.Listbox(root, font=custom_font, bg="black", fg="white", selectbackground="gray")

        for theme in filtered_themes:
            listbox_theme.insert(tk.END, theme)

        print(f"Loaded themes from {theme_path}: {filtered_themes}")
        listbox_theme.pack(pady=5)
        search_frame.pack(pady=10)
        entry_export_frame.pack_forget()

    elif export_mode.get():
        if 'listbox_theme' in globals():
            try:
                listbox_theme.destroy()
            except Exception as e:
                print(f"Error deleting listbox: {e}")
        search_frame.pack_forget()
        create_export_ui()

    else:
        if 'listbox_theme' in globals():
            try:
                listbox_theme.destroy()
            except Exception as e:
                print(f"Error deleting listbox: {e}")
        search_frame.pack_forget()
        if 'entry_export_frame' in globals():
          entry_export_frame.pack_forget() #Correct pack_forget() and destroy() calls

# Get available themes
def get_available_themes(config_path):
    print(f"Fetching themes from {config_path}...")
    theme_root = config_path
    if not os.path.exists(theme_root):
        print(f"Theme root directory not found: {theme_root}")
        return []

    themes = [f for f in os.listdir(theme_root) if os.path.isdir(os.path.join(theme_root, f))]
    print(f"Found themes: {themes}")
    return themes

def create_export_ui():
    global entry_export_frame, entry_export_name

    if 'entry_export_frame' in globals():
        try:
            entry_export_frame.destroy()
        except Exception as e:
            print(f"Error destroying old export frame: {e}")

    entry_export_frame = tk.Frame(root, bg="black")
    tk.Label(entry_export_frame, text="Name:", fg="white", bg="black", font=custom_font).pack(side=tk.LEFT)
    entry_export_name = tk.Entry(entry_export_frame, width=30, font=custom_font, fg="white", bg="black", highlightbackground="white", highlightthickness=2)
    entry_export_name.pack(side=tk.LEFT)
    entry_export_frame.pack(pady=5)

# Apply a theme
def update_bbs_config():
    print("Updating BBS configuration...")
    config_path = entry_path.get()

    if not config_path:
        messagebox.showerror("Error", "Please select a config path.")
        return

    if import_mode.get():
        if 'listbox_theme' not in globals() or not listbox_theme.winfo_exists():
            messagebox.showerror("Error", "Listbox is not initialized. Please select import mode and load a config path.")
            return

        try:
            selected_theme = listbox_theme.get(tk.ACTIVE)
        except Exception as e:
            messagebox.showerror("Error", f"Error getting selected theme: {e}")
            return

        if not selected_theme:
            messagebox.showerror("Error", "Please select a theme to apply.")
            return

        print(f"Applying theme: {selected_theme}")
        theme_path = os.path.join(config_path, "theme", selected_theme)
        bbs_config_path = os.path.join(config_path, "settings", "bbs.json")
        textures_path = os.path.join(config_path, "assets", "textures")

        os.makedirs(textures_path, exist_ok=True)

        theme_config_file = os.path.join(theme_path, "config.txt")
        background_img = os.path.join(theme_path, "background.png")
        icons_img = os.path.join(theme_path, "icons.png")

        if not os.path.exists(theme_config_file):
            messagebox.showerror("Error", "config.txt not found in selected theme folder!")
            return

        theme_data = {}
        try:
            with open(theme_config_file, "r") as file:
                for line in file:
                    if ":" in line:
                        key, value = line.strip().split(":")
                        theme_data[key.strip('"')] = int(value.strip().strip(','))
        except Exception as e:
            messagebox.showerror("Error", f"Error reading config.txt: {e}")
            return

        if not os.path.exists(bbs_config_path):
            messagebox.showerror("Error", "bbs.json not found!")
            return

        try:
            with open(bbs_config_path, "r") as file:
                config = json.load(file)

            if "appearance" in config and "primary_color" in theme_data:
                config["appearance"]["primary_color"] = theme_data["primary_color"]

            if "background" in config and "background_color" in theme_data:
                config["background"]["color"] = theme_data["background_color"]

            print("Saving updated config...")
            with open(bbs_config_path, "w") as file:
                json.dump(config, file, indent=4)

            for img, dest_name in [(background_img, "background.png"), (icons_img, "icons.png")]:
                if os.path.exists(img):
                    print(f"Copying {img} to {textures_path}")
                    shutil.copy(img, os.path.join(textures_path, dest_name))

            messagebox.showinfo("Success", "Theme applied successfully!")

        except FileNotFoundError as e:
            messagebox.showerror("Error", f"File not found: {e}")
        except OSError as e:
            messagebox.showerror("Error", f"OS Error: {e}")
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"JSON Decode Error: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error updating bbs.json: {e}")

    elif export_mode.get():
        if 'entry_export_name' not in globals() or not entry_export_name.get():
            messagebox.showerror("Error", "Please enter a name for the export.")
            return

        export_name = entry_export_name.get()
        src_config = entry_path.get()
        dest_theme = os.path.join(src_config, "theme", export_name)

        try:
            os.makedirs(dest_theme, exist_ok=True)

            src_settings = os.path.join(src_config, "settings", "bbs.json")
            dest_config_file = os.path.join(dest_theme, "config.txt")

            with open(src_settings, "r") as read_file:
                try:
                    get_json = json.load(read_file)
                    primary_color = get_json["appearance"]["primary_color"]
                    bg_color = get_json["background"]["color"]

                    with open(dest_config_file, "w") as create_file:
                        create_file.write('{\n')
                        create_file.write(f'\t"primary_color": {primary_color},\n') #Added quotes
                        create_file.write(f'\t"background_color": {bg_color}\n')  #Added quotes
                        create_file.write('}')


                    print("Copied colors to config.txt")
                except KeyError as e:
                    messagebox.showerror("Error", f"Error reading values from bbs.json: {e}. Check if keys exist")

            asset_background = os.path.join(src_config, "assets", "textures", "background.png")
            asset_icons = os.path.join(src_config, "assets", "textures", "icons.png")

            if os.path.exists(asset_background):
                shutil.copy(asset_background, dest_theme)
            if os.path.exists(asset_icons):
                shutil.copy(asset_icons, dest_theme)

            messagebox.showinfo("Success", f"Theme exported successfully to {dest_theme}!")

        except FileNotFoundError as e:
            messagebox.showerror("Error", f"File not found: {e}")
        except OSError as e:
            messagebox.showerror("Error", f"OS Error: {e}")
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"JSON Decode Error: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting theme: {e}")


def toggle_checkbox(var, label):
    config_path = entry_path.get()

    if not config_path:
        messagebox.showerror("Error", "Please provide the config path first.")
        return

    if var == import_mode:
        export_mode.set(False)
        export_label.config(image=checkbox_unchecked)
    elif var == export_mode:
        import_mode.set(False)
        import_label.config(image=checkbox_unchecked)

    var.set(not var.get())
    label.config(image=checkbox_checked if var.get() else checkbox_unchecked)
    update_ui()
    search_themes() # Call search_themes after toggling to update list based on new mode

def search_themes(event=None): # Accept event argument
    search_term = search_entry.get().lower()
    update_ui()

# Import and Export Checkboxes
import_frame = tk.Frame(root, bg="black")
import_frame.pack()

import_label = tk.Label(import_frame, image=checkbox_unchecked, bg="black")
import_label.pack(side=tk.LEFT)
import_text = tk.Label(import_frame, text="Import", fg="white", bg="black", font=custom_font)
import_text.pack(side=tk.LEFT, padx=5)
import_label.bind("<Button-1>", lambda e: toggle_checkbox(import_mode, import_label))

export_frame = tk.Frame(root, bg="black")
export_frame.pack()

export_label = tk.Label(export_frame, image=checkbox_unchecked, bg="black")
export_label.pack(side=tk.LEFT)
export_text = tk.Label(export_frame, text="Export", fg="white", bg="black", font=custom_font)
export_text.pack(side=tk.LEFT, padx=5)
export_label.bind("<Button-1>", lambda e: toggle_checkbox(export_mode, export_label))

#entry_export_frame = tk.Frame(root, bg="black")  # Create frame early
#tk.Label(entry_export_frame, text="Name:", fg="white", bg="black", font=custom_font).pack(side=tk.LEFT)
#entry_export_name = tk.Entry(entry_export_frame, width=30, font=custom_font, fg="white", bg="black", highlightbackground="white", highlightthickness=2)
#entry_export_name.pack(side=tk.LEFT)

listbox_theme = tk.Listbox(root, font=custom_font, bg="black", fg="white", selectbackground="gray")

# Execute Button
execute_button = tk.Button(frame_bottom, text="Execute", command=update_bbs_config, font=custom_font)
execute_button.pack(side=tk.RIGHT, padx=10)

# Reload and Browse Button
browse_button = tk.Button(frame_top, text="Browse", command=select_config_path, font=custom_font)
browse_button.grid(row=0, column=1, padx=5, sticky="w")

# Configuration for the top-right reload button
if reload_image:
    reload_button = tk.Button(frame_top, image=reload_image, command=update_ui, bd=0, highlightthickness=0, relief="flat", bg="black", activebackground="black")  # Set background to black
    reload_button.grid(row=0, column=3, sticky="e")  # Position top-right

else:
    tk.Label(frame_top, text="Reload Image Not Found", fg="white", bg="black").grid(row=0, column=3, sticky="e")

# Add search functionality
search_frame = tk.Frame(root, bg="black")
search_label = tk.Label(search_frame, text="Search Themes:", fg="white", bg="black", font=custom_font)
search_label.pack(side=tk.LEFT)
search_entry = tk.Entry(search_frame, font=custom_font, width=30)
search_entry.pack(side=tk.LEFT)
def search_themes(event=None): # Accept event argument
    search_term = search_entry.get().lower()
    update_ui()

search_entry.bind("<KeyRelease>", search_themes)  # Auto-update on key release

print("Application started.")

# Initially hide listbox, search frame, and entry_export_frame
if 'listbox_theme' in globals():
    listbox_theme.pack_forget()
search_frame.pack_forget()
if 'entry_export_frame' in globals():

   entry_export_frame.pack_forget()

root.mainloop()
