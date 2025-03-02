import os
import json
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageColor
import tkinter.font as tkFont
import logging
import glob
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Color palette
COLOR_BG = "#000000"  # Pure Black background
COLOR_TEXT = "#FFFFFF"  # White text
COLOR_BUTTON = "#333333"  # Darker button
COLOR_ACCENT = "#0088FF"  # Blue accent

class BBSThemeTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BBS Theme Tool")
        self.root.geometry("700x600")
        self.root.configure(bg=COLOR_BG)
        self.import_mode = tk.BooleanVar(value=False)
        self.export_mode = tk.BooleanVar(value=False)
        self.export_type = tk.StringVar(value="zip")  # Default to "Export as Zip"
        
        # Load assets
        self.custom_font = self.load_custom_font()
        self.load_custom_icon()
        self.checkbox_size = 32
        self.reload_size = 32
        self.checkbox_checked, self.checkbox_unchecked = self.load_checkbox_images()
        self.reload_image = self.load_reload_image()

        self.setup_ui()
        logging.info("Application started.")

    def load_custom_font(self):
        logging.info("Loading custom font...")
        font_path = "assets/font.ttf"
        if os.path.exists(font_path):
            try:
                return tkFont.Font(family="Minecraft", size=16)
            except Exception as e:
                logging.error(f"Error loading custom font: {e}. Using Arial instead.")
                return tkFont.Font(family="Arial", size=12)
        logging.warning("Custom font file not found. Using Arial instead.")
        return tkFont.Font(family="Arial", size=12)

    def load_custom_icon(self):
        logging.info("Loading custom icon...")
        icon_path = "assets/myicon.png"
        if os.path.exists(icon_path):
            try:
                img = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, img)
                logging.info("Custom icon loaded successfully.")
            except Exception as e:
                logging.error(f"Error loading custom icon: {e}")

    def load_checkbox_images(self):
        logging.info("Loading checkbox images...")
        try:
            img_check = Image.open("assets/checkbox_check.png").resize((self.checkbox_size, self.checkbox_size), Image.NEAREST)
            img_uncheck = Image.open("assets/checkbox_nocheck.png").resize((self.checkbox_size, self.checkbox_size), Image.NEAREST)
            return ImageTk.PhotoImage(img_check), ImageTk.PhotoImage(img_uncheck)
        except FileNotFoundError:
            logging.error("Error: Checkbox images not found.")
            return None, None

    def load_reload_image(self):
        try:
            img_reload = Image.open("assets/reload.png").resize((self.reload_size, self.reload_size), Image.NEAREST)
            return ImageTk.PhotoImage(img_reload)
        except FileNotFoundError:
            logging.error("Error: reload.png not found in assets folder. Using placeholder.")
            return None

    def setup_ui(self):
        # Frames
        self.frame_top = tk.Frame(self.root, bg=COLOR_BG)
        self.frame_top.pack(pady=10, fill="x")
        self.frame_middle = tk.Frame(self.root, bg=COLOR_BG)
        self.frame_middle.pack()
        self.frame_bottom = tk.Frame(self.root, bg=COLOR_BG)
        self.frame_bottom.pack(side=tk.BOTTOM, fill="x", padx=10, pady=10)

        # Path selection
        self.entry_path = tk.Entry(self.frame_top, font=self.custom_font, width=40, bg=COLOR_BUTTON, fg=COLOR_TEXT, relief=tk.FLAT)
        self.entry_path.grid(row=0, column=0, padx=5, sticky="w")
        browse_button = tk.Button(self.frame_top, text="Browse", command=self.select_config_path, font=self.custom_font, relief=tk.FLAT, bg=COLOR_BUTTON, fg=COLOR_TEXT, activebackground=COLOR_ACCENT, highlightthickness=0, bd=0)
        browse_button.grid(row=0, column=1, padx=5, sticky="w")
        if self.reload_image:
            reload_button = tk.Button(self.frame_top, image=self.reload_image, command=self.update_ui, bd=0, highlightthickness=0, relief=tk.FLAT, bg=COLOR_BG, activebackground=COLOR_ACCENT)
            reload_button.grid(row=0, column=3, sticky="e")
        else:
            tk.Label(self.frame_top, text="Reload Image Not Found", fg=COLOR_TEXT, bg=COLOR_BG).grid(row=0, column=3, sticky="e")

        # Checkboxes for Import/Export
        import_frame = tk.Frame(self.root, bg=COLOR_BG)
        import_frame.pack(pady=5, anchor='center')
        self.import_label = tk.Label(import_frame, image=self.checkbox_unchecked if self.checkbox_unchecked else "", bg=COLOR_BG)
        self.import_label.pack(side=tk.LEFT, padx=5)
        tk.Label(import_frame, text="Import", fg=COLOR_TEXT, bg=COLOR_BG, font=self.custom_font).pack(side=tk.LEFT, padx=5)
        self.import_label.bind("<Button-1>", lambda e: self.toggle_checkbox(self.import_mode, self.import_label, "import"))

        export_frame = tk.Frame(self.root, bg=COLOR_BG)
        export_frame.pack(pady=5, anchor='center')
        self.export_label = tk.Label(export_frame, image=self.checkbox_unchecked if self.checkbox_unchecked else "", bg=COLOR_BG)
        self.export_label.pack(side=tk.LEFT, padx=5)
        tk.Label(export_frame, text="Export", fg=COLOR_TEXT, bg=COLOR_BG, font=self.custom_font).pack(side=tk.LEFT, padx=5)
        self.export_label.bind("<Button-1>", lambda e: self.toggle_checkbox(self.export_mode, self.export_label, "export"))

        # Search frame
        self.search_frame = tk.Frame(self.root, bg=COLOR_BG)
        tk.Label(self.search_frame, text="Search Themes:", fg=COLOR_TEXT, bg=COLOR_BG, font=self.custom_font).pack(side=tk.LEFT)
        self.search_entry = tk.Entry(self.search_frame, font=self.custom_font, width=30, relief=tk.FLAT, bg=COLOR_BUTTON, fg=COLOR_TEXT)
        self.search_entry.pack(side=tk.LEFT)
        self.search_entry.bind("<KeyRelease>", self.search_themes)

        # Export entry frame with options below name
        self.entry_export_frame = tk.Frame(self.root, bg=COLOR_BG)
        name_frame = tk.Frame(self.entry_export_frame, bg=COLOR_BG)
        name_frame.pack(pady=5)
        tk.Label(name_frame, text="Name:", fg=COLOR_TEXT, bg=COLOR_BG, font=self.custom_font).pack(side=tk.LEFT, padx=5)
        self.entry_export_name = tk.Entry(name_frame, width=30, font=self.custom_font, fg=COLOR_TEXT, bg=COLOR_BUTTON, highlightbackground="white", highlightthickness=2, relief=tk.FLAT)
        self.entry_export_name.pack(side=tk.LEFT, padx=5)

        export_options_frame = tk.Frame(self.entry_export_frame, bg=COLOR_BG)
        export_options_frame.pack(pady=5)
        tk.Label(export_options_frame, text="Export as:", fg=COLOR_TEXT, bg=COLOR_BG, font=self.custom_font).pack(side=tk.LEFT, padx=5)
        
        self.export_zip_label = tk.Label(export_options_frame, image=self.checkbox_checked if self.checkbox_checked else "", bg=COLOR_BG)
        self.export_zip_label.pack(side=tk.LEFT, padx=5)
        tk.Label(export_options_frame, text="Zip", fg=COLOR_TEXT, bg=COLOR_BG, font=self.custom_font).pack(side=tk.LEFT, padx=5)
        self.export_zip_label.bind("<Button-1>", lambda e: self.toggle_export_type("zip"))

        self.export_folder_label = tk.Label(export_options_frame, image=self.checkbox_unchecked if self.checkbox_unchecked else "", bg=COLOR_BG)
        self.export_folder_label.pack(side=tk.LEFT, padx=5)
        tk.Label(export_options_frame, text="Folder", fg=COLOR_TEXT, bg=COLOR_BG, font=self.custom_font).pack(side=tk.LEFT, padx=5)
        self.export_folder_label.bind("<Button-1>", lambda e: self.toggle_export_type("folder"))

        # Buttons
        self.execute_button = tk.Button(self.frame_bottom, text="Execute", command=self.update_bbs_config, font=self.custom_font, relief=tk.FLAT, bg=COLOR_BUTTON, fg=COLOR_TEXT, activebackground=COLOR_ACCENT, highlightthickness=0, bd=0)
        self.execute_button.pack(side=tk.RIGHT, padx=10)
        self.preview_button = tk.Button(self.frame_bottom, text="Preview", command=self.preview_theme, font=self.custom_font, relief=tk.FLAT, bg=COLOR_BUTTON, fg=COLOR_TEXT, activebackground=COLOR_ACCENT, highlightthickness=0, bd=0)
        self.preview_button.pack(side=tk.RIGHT, padx=10)

        # Initially hide dynamic elements
        self.search_frame.pack_forget()
        self.entry_export_frame.pack_forget()

    def select_config_path(self):
        logging.info("Selecting config path...")
        path = filedialog.askdirectory(title="Select Config Path")
        if path and "bbs" in os.path.basename(path):
            if os.path.exists(os.path.join(path, "settings", "bbs.json")):
                self.entry_path.delete(0, tk.END)
                self.entry_path.insert(0, path)
                self.update_ui()
            else:
                messagebox.showerror("Error", "Selected directory lacks settings/bbs.json.")
        else:
            messagebox.showerror("Error", "Please select a valid /config/bbs directory.")

    def toggle_checkbox(self, var, label, mode):
        config_path = self.entry_path.get()
        if not config_path:
            messagebox.showerror("Error", "Please provide the config path first.")
            return
        if var == self.import_mode:
            self.export_mode.set(False)
            self.export_label.config(image=self.checkbox_unchecked)
        elif var == self.export_mode:
            self.import_mode.set(False)
            self.import_label.config(image=self.checkbox_unchecked)
        var.set(not var.get())
        label.config(image=self.checkbox_checked if var.get() else self.checkbox_unchecked)
        self.update_ui()

    def toggle_export_type(self, selected_type):
        if self.export_type.get() != selected_type:
            self.export_type.set(selected_type)
            if selected_type == "zip":
                self.export_zip_label.config(image=self.checkbox_checked)
                self.export_folder_label.config(image=self.checkbox_unchecked)
            else:  # folder
                self.export_zip_label.config(image=self.checkbox_unchecked)
                self.export_folder_label.config(image=self.checkbox_checked)

    def update_ui(self):
        logging.info("Updating UI...")
        config_path = self.entry_path.get()
        if not config_path:
            logging.info("No config path selected.")
            if hasattr(self, "listbox_theme"):
                self.listbox_theme.pack_forget()
            self.search_frame.pack_forget()
            self.entry_export_frame.pack_forget()
            return

        if not hasattr(self, "listbox_theme"):
            self.listbox_theme = tk.Listbox(self.root, font=self.custom_font, bg=COLOR_BUTTON, fg=COLOR_TEXT, selectbackground=COLOR_ACCENT, relief=tk.FLAT, highlightthickness=0)
            self.listbox_theme.pack(pady=5)

        self.listbox_theme.delete(0, tk.END)
        if self.import_mode.get():
            themes = self.get_available_themes(os.path.join(config_path, "theme"))
            search_term = self.search_entry.get().lower()
            filtered_themes = [theme for theme in themes if search_term in theme.lower()]
            for theme in filtered_themes:
                self.listbox_theme.insert(tk.END, theme)
            logging.info(f"Loaded themes: {filtered_themes}")
            self.listbox_theme.pack(pady=5)
            self.search_frame.pack(pady=10)
            self.entry_export_frame.pack_forget()
        elif self.export_mode.get():
            self.listbox_theme.pack_forget()
            self.search_frame.pack_forget()
            self.entry_export_frame.pack(pady=5)
        else:
            self.listbox_theme.pack_forget()
            self.search_frame.pack_forget()
            self.entry_export_frame.pack_forget()

    def get_available_themes(self, theme_path):
        logging.info(f"Fetching themes from {theme_path}...")
        if not os.path.exists(theme_path):
            logging.warning(f"Theme root directory not found: {theme_path}")
            return []
        themes = [f for f in os.listdir(theme_path) if os.path.isdir(os.path.join(theme_path, f)) or f.endswith(".zip")]
        logging.info(f"Found themes: {themes}")
        return themes

    def search_themes(self, event=None):
        self.update_ui()

    def preview_theme(self):
        config_path = self.entry_path.get()
        if not config_path:
            messagebox.showerror("Error", "Please select a config path.")
            return

        if self.import_mode.get():
            if not hasattr(self, "listbox_theme") or not self.listbox_theme.winfo_exists():
                messagebox.showerror("Error", "Please select a theme first.")
                return
            selected_theme = self.listbox_theme.get(tk.ACTIVE)
            if not selected_theme:
                messagebox.showerror("Error", "Please select a theme to preview.")
                return
            theme_path = os.path.join(config_path, "theme")
            if selected_theme.endswith(".zip"):
                temp_dir = os.path.join(theme_path, "temp")
                os.makedirs(temp_dir, exist_ok=True)
                shutil.unpack_archive(os.path.join(theme_path, selected_theme), temp_dir)
                config_file = glob.glob(os.path.join(temp_dir, '**', 'config.txt'), recursive=True)[0]
                background_img_path = os.path.join(os.path.dirname(config_file), "background.png")
            else:
                config_file = os.path.join(theme_path, selected_theme, "config.txt")
                background_img_path = os.path.join(theme_path, selected_theme, "background.png")
            theme_data = {}
            with open(config_file, "r") as file:
                for line in file:
                    if ":" in line:
                        key, value = line.strip().split(":")
                        theme_data[key.strip('"')] = int(value.strip().strip(','))
            primary_color = theme_data.get("primary_color", 0)
            background_color = theme_data.get("background_color", 0)
        elif self.export_mode.get():
            bbs_config_path = os.path.join(config_path, "settings", "bbs.json")
            if not os.path.exists(bbs_config_path):
                messagebox.showerror("Error", "bbs.json not found!")
                return
            with open(bbs_config_path, "r") as file:
                config = json.load(file)
            primary_color = config["appearance"].get("primary_color", 0)
            background_color = config["background"].get("color", 0)
            background_img_path = os.path.join(config_path, "assets", "textures", "background.png")
        else:
            messagebox.showerror("Error", "Please select Import or Export mode.")
            return

        # Color conversion
        def color_to_hex_and_alpha(color_int):
            alpha = (color_int >> 24) & 0xFF
            rgb = color_int & 0xFFFFFF
            hex_color = f"#{rgb:06x}"
            return hex_color, alpha / 255.0

        primary_hex, primary_alpha = color_to_hex_and_alpha(primary_color)
        background_hex, background_alpha = color_to_hex_and_alpha(background_color)
        logging.info(f"Primary Color: {primary_hex} (Alpha: {primary_alpha}), Background Color: {background_hex} (Alpha: {background_alpha}), Image Path: {background_img_path}")

        # Preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Theme Preview")
        preview_window.geometry("400x400")
        preview_window.configure(bg=COLOR_BG)

        tk.Label(preview_window, text=f"Primary Color (Alpha: {primary_alpha:.2f}):", fg=COLOR_TEXT, bg=COLOR_BG, font=self.custom_font).pack(pady=5)
        primary_canvas = tk.Canvas(preview_window, width=100, height=50, bg=primary_hex, relief=tk.FLAT)
        primary_canvas.pack()

        tk.Label(preview_window, text=f"Background Color (Alpha: {background_alpha:.2f}):", fg=COLOR_TEXT, bg=COLOR_BG, font=self.custom_font).pack(pady=5)
        background_canvas = tk.Canvas(preview_window, width=100, height=50, bg=background_hex, relief=tk.FLAT)
        background_canvas.pack()

        tk.Label(preview_window, text="Background Preview:", fg=COLOR_TEXT, bg=COLOR_BG, font=self.custom_font).pack(pady=5)
        preview_canvas = tk.Canvas(preview_window, width=200, height=200, bg=COLOR_BG, relief=tk.FLAT)
        preview_canvas.pack()

        rgb_tuple = ImageColor.getrgb(background_hex)
        bg_image = Image.new("RGBA", (200, 200), rgb_tuple + (int(background_alpha * 255),))
        if os.path.exists(background_img_path):
            try:
                img = Image.open(background_img_path).convert("RGBA").resize((200, 200), Image.NEAREST)
                combined = Image.blend(bg_image, img, 0.5)
                photo = ImageTk.PhotoImage(combined)
                preview_canvas.create_image(100, 100, image=photo)
                preview_canvas.image = photo
                logging.info(f"Loaded and blended background image from: {background_img_path}")
            except Exception as e:
                logging.error(f"Error loading background image: {e}")
                preview_canvas.create_rectangle(0, 0, 200, 200, fill=background_hex)
                tk.Label(preview_window, text="Error Loading Image", fg=COLOR_TEXT, bg=COLOR_BG, font=self.custom_font).pack(pady=5)
        else:
            logging.warning(f"Background image not found at: {background_img_path}")
            preview_canvas.create_rectangle(0, 0, 200, 200, fill=background_hex)
            tk.Label(preview_window, text="Image Not Found", fg=COLOR_TEXT, bg=COLOR_BG, font=self.custom_font).pack(pady=5)

        if self.import_mode.get() and os.path.exists(os.path.join(theme_path, "temp")):
            shutil.rmtree(os.path.join(theme_path, "temp"))

    def update_bbs_config(self):
        logging.info("Updating BBS configuration...")
        config_path = self.entry_path.get()
        if not config_path:
            messagebox.showerror("Error", "Please select a config path.")
            return

        if self.import_mode.get():
            if not hasattr(self, "listbox_theme") or not self.listbox_theme.winfo_exists():
                messagebox.showerror("Error", "Please select import mode and load a config path.")
                return
            selected_theme = self.listbox_theme.get(tk.ACTIVE)
            if not selected_theme:
                messagebox.showerror("Error", "Please select a theme to apply.")
                return
            logging.info(f"Applying theme: {selected_theme}")
            theme_path = os.path.join(config_path, "theme")
            bbs_config_path = os.path.join(config_path, "settings", "bbs.json")
            textures_path = os.path.join(config_path, "assets", "textures")
            os.makedirs(textures_path, exist_ok=True)

            if selected_theme.endswith(".zip"):
                temp_dir = os.path.join(theme_path, "temp")
                os.makedirs(temp_dir, exist_ok=True)
                zip_file_path = os.path.join(theme_path, selected_theme)
                try:
                    shutil.unpack_archive(zip_file_path, temp_dir)
                    config_files = glob.glob(os.path.join(temp_dir, '**', 'config.txt'), recursive=True)
                    if not config_files:
                        messagebox.showerror("Error", "config.txt not found in the extracted zip file!")
                        return
                    theme_config_file = config_files[0]
                    theme_dir = os.path.dirname(theme_config_file)
                    background_img = os.path.join(theme_dir, "background.png")
                    icons_img = os.path.join(theme_dir, "icons.png")
                except Exception as e:
                    messagebox.showerror("Error", f"Error extracting zip file: {e}")
                    return
            else:
                theme_config_file = os.path.join(theme_path, selected_theme, "config.txt")
                background_img = os.path.join(theme_path, selected_theme, "background.png")
                icons_img = os.path.join(theme_path, selected_theme, "icons.png")

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
                with open(bbs_config_path, "w") as file:
                    json.dump(config, file, indent=4)
                for img, dest_name in [(background_img, "background.png"), (icons_img, "icons.png")]:
                    if os.path.exists(img):
                        logging.info(f"Copying {img} to {textures_path}")
                        shutil.copy(img, os.path.join(textures_path, dest_name))
                messagebox.showinfo("Success", "Theme applied successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error updating bbs.json: {e}")
            finally:
                if os.path.exists(os.path.join(theme_path, "temp")):
                    shutil.rmtree(os.path.join(theme_path, "temp"))

        elif self.export_mode.get():
            if not self.entry_export_name.winfo_exists() or not self.entry_export_name.get():
                messagebox.showerror("Error", "Please enter a name for the export.")
                return
            export_name = self.entry_export_name.get()
            dest_theme = os.path.join(config_path, "theme", export_name)
            zip_file_path = os.path.join(config_path, "theme", f"{export_name}.zip")
            
            # Check for overwrite
            if (self.export_type.get() == "zip" and os.path.exists(zip_file_path)) or \
               (self.export_type.get() == "folder" and os.path.exists(dest_theme)):
                if not messagebox.askyesno("Warning", f"Theme '{export_name}' already exists as {self.export_type.get()}. Overwrite?"):
                    return

            try:
                # Always create the folder first
                if os.path.exists(dest_theme):
                    shutil.rmtree(dest_theme)  # Clear existing folder if it exists
                os.makedirs(dest_theme, exist_ok=True)
                
                src_settings = os.path.join(config_path, "settings", "bbs.json")
                dest_config_file = os.path.join(dest_theme, "config.txt")
                with open(src_settings, "r") as read_file:
                    try:
                        config = json.load(read_file)
                        primary_color = config["appearance"]["primary_color"]
                        bg_color = config["background"]["color"]
                        with open(dest_config_file, "w") as create_file:
                            create_file.write('{\n')
                            create_file.write(f'\t"primary_color": {primary_color},\n')
                            create_file.write(f'\t"background_color": {bg_color}\n')
                            create_file.write('}')
                        logging.info("Copied colors to config.txt")
                    except KeyError as e:
                        messagebox.showerror("Error", f"Error reading values from bbs.json: {e}")
                        return
                
                # Copy texture files
                for src, dest in [(os.path.join(config_path, "assets", "textures", "background.png"), "background.png"),
                                  (os.path.join(config_path, "assets", "textures", "icons.png"), "icons.png")]:
                    if os.path.exists(src):
                        shutil.copy(src, os.path.join(dest_theme, dest))

                # Handle export type
                if self.export_type.get() == "zip":
                    if os.path.exists(zip_file_path):
                        os.remove(zip_file_path)  # Remove existing ZIP if it exists
                    shutil.make_archive(os.path.join(config_path, "theme", export_name), 'zip', dest_theme)
                    shutil.rmtree(dest_theme)  # Clean up temporary folder
                    logging.info(f"Zip file generated to {zip_file_path}")
                    messagebox.showinfo("Success", f"Theme exported successfully as ZIP to {zip_file_path}!")
                else:  # Export as folder
                    logging.info(f"Folder exported to {dest_theme}")
                    messagebox.showinfo("Success", f"Theme exported successfully as folder to {dest_theme}!")
            except Exception as e:
                messagebox.showerror("Error", f"Error exporting theme: {e}")
                if os.path.exists(dest_theme):
                    shutil.rmtree(dest_theme)  # Clean up on failure

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = BBSThemeTool()
    app.run()
