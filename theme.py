import os
import json
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageColor
import tkinter.font as tkFont
import logging
import glob
from datetime import datetime
import threading
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Modern color palette with pixel aesthetic
class ColorScheme:
    BG_PRIMARY = "#0a0a0a"      # Deep black
    BG_SECONDARY = "#1a1a1a"    # Slightly lighter black
    BG_CARD = "#2a2a2a"         # Card background
    TEXT_PRIMARY = "#ffffff"     # Pure white
    TEXT_SECONDARY = "#b0b0b0"   # Light gray
    ACCENT_BLUE = "#00aaff"      # Bright blue
    ACCENT_GREEN = "#00ff88"     # Success green
    ACCENT_RED = "#ff4444"       # Error red
    ACCENT_YELLOW = "#ffaa00"    # Warning yellow
    BORDER = "#404040"           # Border color
    HOVER = "#333333"            # Hover state

class AssetManager:
    """Manages loading and caching of image assets"""
    
    def __init__(self):
        self.assets = {}
        self.asset_path = "assets"
        
    def load_image(self, filename: str, size: Tuple[int, int] = None) -> Optional[ImageTk.PhotoImage]:
        """Load and cache an image asset"""
        cache_key = f"{filename}_{size}" if size else filename
        
        if cache_key in self.assets:
            return self.assets[cache_key]
            
        file_path = os.path.join(self.asset_path, filename)
        if not os.path.exists(file_path):
            logging.warning(f"Asset not found: {file_path}")
            return None
            
        try:
            img = Image.open(file_path)
            if size:
                img = img.resize(size, Image.NEAREST)
            photo = ImageTk.PhotoImage(img)
            self.assets[cache_key] = photo
            return photo
        except Exception as e:
            logging.error(f"Error loading asset {filename}: {e}")
            return None

class ModernButton(tk.Frame):
    """Custom modern button with pixel styling"""
    
    def __init__(self, parent, text="", command=None, image=None, style="primary", **kwargs):
        super().__init__(parent, bg=ColorScheme.BG_PRIMARY, **kwargs)
        
        self.command = command
        self.style = style
        self.is_hovered = False
        
        # Style configurations
        styles = {
            "primary": {"bg": ColorScheme.ACCENT_BLUE, "hover": "#0088cc"},
            "secondary": {"bg": ColorScheme.BG_CARD, "hover": ColorScheme.HOVER},
            "success": {"bg": ColorScheme.ACCENT_GREEN, "hover": "#00cc66"},
            "danger": {"bg": ColorScheme.ACCENT_RED, "hover": "#cc3333"}
        }
        
        self.colors = styles.get(style, styles["primary"])
        
        # Create button frame
        self.button_frame = tk.Frame(self, bg=self.colors["bg"], relief=tk.FLAT, bd=0)
        self.button_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Add content
        if image:
            self.label = tk.Label(self.button_frame, image=image, bg=self.colors["bg"], 
                                fg=ColorScheme.TEXT_PRIMARY, bd=0)
        else:
            font = tkFont.Font(family="Arial", size=10, weight="bold")
            self.label = tk.Label(self.button_frame, text=text, bg=self.colors["bg"], 
                                fg=ColorScheme.TEXT_PRIMARY, font=font, bd=0)
        
        self.label.pack(expand=True, padx=8, pady=6)
        
        # Bind events
        self.bind_events()
        
    def bind_events(self):
        """Bind mouse events for interactivity"""
        widgets = [self, self.button_frame, self.label]
        for widget in widgets:
            widget.bind("<Button-1>", self.on_click)
            widget.bind("<Enter>", self.on_enter)
            widget.bind("<Leave>", self.on_leave)
            
    def on_click(self, event):
        if self.command:
            self.command()
            
    def on_enter(self, event):
        self.is_hovered = True
        self.button_frame.config(bg=self.colors["hover"])
        self.label.config(bg=self.colors["hover"])
        
    def on_leave(self, event):
        self.is_hovered = False
        self.button_frame.config(bg=self.colors["bg"])
        self.label.config(bg=self.colors["bg"])

class ModernCheckbox(tk.Frame):
    """Custom modern checkbox with pixel styling"""
    
    def __init__(self, parent, text="", variable=None, command=None, **kwargs):
        super().__init__(parent, bg=ColorScheme.BG_PRIMARY, **kwargs)
        
        self.variable = variable or tk.BooleanVar()
        self.command = command
        self.text = text
        
        # Create checkbox elements
        self.checkbox_frame = tk.Frame(self, bg=ColorScheme.BG_CARD, width=20, height=20, relief=tk.FLAT, bd=1)
        self.checkbox_frame.pack(side=tk.LEFT, padx=(0, 8))
        self.checkbox_frame.pack_propagate(False)
        
        self.check_label = tk.Label(self.checkbox_frame, bg=ColorScheme.BG_CARD, fg=ColorScheme.ACCENT_BLUE, 
                                  text="", font=("Arial", 12, "bold"))
        self.check_label.pack(expand=True)
        
        if text:
            self.text_label = tk.Label(self, text=text, bg=ColorScheme.BG_PRIMARY, 
                                     fg=ColorScheme.TEXT_PRIMARY, font=("Arial", 10))
            self.text_label.pack(side=tk.LEFT)
        
        # Bind events
        self.bind_events()
        self.update_display()
        
    def bind_events(self):
        """Bind mouse events"""
        widgets = [self, self.checkbox_frame, self.check_label]
        if hasattr(self, 'text_label'):
            widgets.append(self.text_label)
            
        for widget in widgets:
            widget.bind("<Button-1>", self.toggle)
            
    def toggle(self, event=None):
        """Toggle checkbox state"""
        self.variable.set(not self.variable.get())
        self.update_display()
        if self.command:
            self.command()
            
    def update_display(self):
        """Update visual state"""
        if self.variable.get():
            self.check_label.config(text="✓", fg=ColorScheme.ACCENT_BLUE)
            self.checkbox_frame.config(bg=ColorScheme.BG_SECONDARY, highlightbackground=ColorScheme.ACCENT_BLUE)
        else:
            self.check_label.config(text="", fg=ColorScheme.TEXT_SECONDARY)
            self.checkbox_frame.config(bg=ColorScheme.BG_CARD, highlightbackground=ColorScheme.BORDER)

class ModernEntry(tk.Frame):
    """Custom modern entry with pixel styling"""
    
    def __init__(self, parent, placeholder="", **kwargs):
        super().__init__(parent, bg=ColorScheme.BG_PRIMARY, **kwargs)
        
        self.placeholder = placeholder
        self.has_focus = False
        
        # Create entry frame
        self.entry_frame = tk.Frame(self, bg=ColorScheme.BG_CARD, relief=tk.FLAT, bd=1)
        self.entry_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Create entry widget
        self.entry = tk.Entry(self.entry_frame, bg=ColorScheme.BG_CARD, fg=ColorScheme.TEXT_PRIMARY,
                            relief=tk.FLAT, bd=0, font=("Arial", 10), insertbackground=ColorScheme.TEXT_PRIMARY)
        self.entry.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        
        # Bind events
        self.entry.bind("<FocusIn>", self.on_focus_in)
        self.entry.bind("<FocusOut>", self.on_focus_out)
        
        # Set placeholder
        if placeholder:
            self.set_placeholder()
            
    def set_placeholder(self):
        """Set placeholder text"""
        self.entry.insert(0, self.placeholder)
        self.entry.config(fg=ColorScheme.TEXT_SECONDARY)
        
    def on_focus_in(self, event):
        """Handle focus in event"""
        self.has_focus = True
        self.entry_frame.config(highlightbackground=ColorScheme.ACCENT_BLUE, highlightthickness=1)
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=ColorScheme.TEXT_PRIMARY)
            
    def on_focus_out(self, event):
        """Handle focus out event"""
        self.has_focus = False
        self.entry_frame.config(highlightthickness=0)
        if not self.entry.get() and self.placeholder:
            self.set_placeholder()
            
    def get(self):
        """Get entry value"""
        value = self.entry.get()
        return "" if value == self.placeholder else value
        
    def delete(self, first, last=None):
        """Delete entry content"""
        self.entry.delete(first, last)
        
    def insert(self, index, string):
        """Insert text into entry"""
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=ColorScheme.TEXT_PRIMARY)
        self.entry.insert(index, string)

class ModernListbox(tk.Frame):
    """Custom modern listbox with pixel styling"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=ColorScheme.BG_PRIMARY, **kwargs)
        
        # Create scrollable frame
        self.canvas = tk.Canvas(self, bg=ColorScheme.BG_CARD, highlightthickness=0, height=200)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=ColorScheme.BG_CARD)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.items = []
        self.selected_index = -1
        
    def insert(self, index, text):
        """Insert item into listbox"""
        item_frame = tk.Frame(self.scrollable_frame, bg=ColorScheme.BG_CARD, relief=tk.FLAT)
        item_frame.pack(fill="x", padx=2, pady=1)
        
        item_label = tk.Label(item_frame, text=text, bg=ColorScheme.BG_CARD, fg=ColorScheme.TEXT_PRIMARY,
                            font=("Arial", 10), anchor="w", padx=8, pady=4)
        item_label.pack(fill="x")
        
        # Bind selection events
        def on_click(event, idx=len(self.items)):
            self.select_item(idx)
            
        item_frame.bind("<Button-1>", on_click)
        item_label.bind("<Button-1>", on_click)
        
        self.items.append({"frame": item_frame, "label": item_label, "text": text})
        
    def delete(self, first, last=None):
        """Delete items from listbox"""
        if last is None:
            last = first
            
        for i in range(last, first - 1, -1):
            if 0 <= i < len(self.items):
                self.items[i]["frame"].destroy()
                del self.items[i]
                
        self.selected_index = -1
        
    def select_item(self, index):
        """Select an item"""
        # Deselect previous
        if 0 <= self.selected_index < len(self.items):
            item = self.items[self.selected_index]
            item["frame"].config(bg=ColorScheme.BG_CARD)
            item["label"].config(bg=ColorScheme.BG_CARD)
            
        # Select new
        if 0 <= index < len(self.items):
            self.selected_index = index
            item = self.items[index]
            item["frame"].config(bg=ColorScheme.ACCENT_BLUE)
            item["label"].config(bg=ColorScheme.ACCENT_BLUE)
            
    def get(self, index):
        """Get item text"""
        if index == tk.ACTIVE:
            index = self.selected_index
        if 0 <= index < len(self.items):
            return self.items[index]["text"]
        return ""

class BBSThemeTool:
    """Main application class with modern UI and optimized code"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # Initialize managers
        self.asset_manager = AssetManager()
        
        # State variables
        self.import_mode = tk.BooleanVar(value=False)
        self.export_mode = tk.BooleanVar(value=False)
        self.export_type = tk.StringVar(value="zip")
        
        # UI components
        self.widgets = {}
        
        self.setup_ui()
        self.setup_styles()
        
        logging.info("Modern BBS Theme Tool initialized")
        
    def setup_window(self):
        """Configure main window"""
        self.root.title("BBS Theme Tool - Modern Edition")
        self.root.geometry("800x700")
        self.root.configure(bg=ColorScheme.BG_PRIMARY)
        self.root.resizable(True, True)
        
        # Load custom icon
        icon = self.asset_manager.load_image("myicon.png")
        if icon:
            self.root.iconphoto(True, icon)
            
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure scrollbar
        style.configure("Vertical.TScrollbar",
                       background=ColorScheme.BG_CARD,
                       troughcolor=ColorScheme.BG_SECONDARY,
                       bordercolor=ColorScheme.BORDER,
                       arrowcolor=ColorScheme.TEXT_SECONDARY,
                       darkcolor=ColorScheme.BG_CARD,
                       lightcolor=ColorScheme.BG_CARD)
        
    def create_header(self, parent):
        """Create modern header section"""
        header_frame = tk.Frame(parent, bg=ColorScheme.BG_SECONDARY, height=60)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(header_frame, text="BBS Theme Tool", 
                             bg=ColorScheme.BG_SECONDARY, fg=ColorScheme.TEXT_PRIMARY,
                             font=("Arial", 16, "bold"))
        title_label.pack(side="left", padx=20, pady=15)
        
        # Version info
        version_label = tk.Label(header_frame, text="v2.0 Modern Edition", 
                               bg=ColorScheme.BG_SECONDARY, fg=ColorScheme.TEXT_SECONDARY,
                               font=("Arial", 9))
        version_label.pack(side="right", padx=20, pady=15)
        
        return header_frame
        
    def create_path_section(self, parent):
        """Create path selection section"""
        section_frame = tk.Frame(parent, bg=ColorScheme.BG_PRIMARY)
        section_frame.pack(fill="x", padx=20, pady=15)
        
        # Section title
        title_label = tk.Label(section_frame, text="Configuration Path", 
                             bg=ColorScheme.BG_PRIMARY, fg=ColorScheme.TEXT_PRIMARY,
                             font=("Arial", 12, "bold"))
        title_label.pack(anchor="w", pady=(0, 8))
        
        # Path input frame
        path_frame = tk.Frame(section_frame, bg=ColorScheme.BG_PRIMARY)
        path_frame.pack(fill="x")
        
        # Path entry
        self.widgets["path_entry"] = ModernEntry(path_frame, placeholder="Select BBS config directory...")
        self.widgets["path_entry"].pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Browse button
        browse_btn = ModernButton(path_frame, text="Browse", command=self.select_config_path, style="secondary")
        browse_btn.pack(side="right", ipadx=10)
        
        # Reload button
        reload_icon = self.asset_manager.load_image("reload.png", (24, 24))
        reload_btn = ModernButton(path_frame, image=reload_icon, command=self.update_ui, style="secondary")
        reload_btn.pack(side="right", padx=(0, 10))
        
        return section_frame
        
    def create_mode_section(self, parent):
        """Create mode selection section"""
        section_frame = tk.Frame(parent, bg=ColorScheme.BG_PRIMARY)
        section_frame.pack(fill="x", padx=20, pady=15)
        
        # Section title
        title_label = tk.Label(section_frame, text="Operation Mode", 
                             bg=ColorScheme.BG_PRIMARY, fg=ColorScheme.TEXT_PRIMARY,
                             font=("Arial", 12, "bold"))
        title_label.pack(anchor="w", pady=(0, 8))
        
        # Mode selection frame
        mode_frame = tk.Frame(section_frame, bg=ColorScheme.BG_CARD, relief=tk.FLAT)
        mode_frame.pack(fill="x", pady=5)
        
        # Import checkbox
        import_frame = tk.Frame(mode_frame, bg=ColorScheme.BG_CARD)
        import_frame.pack(side="left", padx=20, pady=15)
        
        self.widgets["import_checkbox"] = ModernCheckbox(import_frame, text="Import Theme", 
                                                       variable=self.import_mode, 
                                                       command=self.on_mode_change)
        self.widgets["import_checkbox"].pack()
        
        # Export checkbox
        export_frame = tk.Frame(mode_frame, bg=ColorScheme.BG_CARD)
        export_frame.pack(side="right", padx=20, pady=15)
        
        self.widgets["export_checkbox"] = ModernCheckbox(export_frame, text="Export Theme", 
                                                        variable=self.export_mode, 
                                                        command=self.on_mode_change)
        self.widgets["export_checkbox"].pack()
        
        return section_frame
        
    def create_content_section(self, parent):
        """Create dynamic content section"""
        self.content_frame = tk.Frame(parent, bg=ColorScheme.BG_PRIMARY)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        return self.content_frame
        
    def create_import_content(self):
        """Create import mode content"""
        self.clear_content()
        
        # Search section
        search_frame = tk.Frame(self.content_frame, bg=ColorScheme.BG_PRIMARY)
        search_frame.pack(fill="x", pady=(0, 15))
        
        search_label = tk.Label(search_frame, text="Search Themes", 
                              bg=ColorScheme.BG_PRIMARY, fg=ColorScheme.TEXT_PRIMARY,
                              font=("Arial", 11, "bold"))
        search_label.pack(anchor="w", pady=(0, 5))
        
        self.widgets["search_entry"] = ModernEntry(search_frame, placeholder="Type to search themes...")
        self.widgets["search_entry"].pack(fill="x")
        self.widgets["search_entry"].entry.bind("<KeyRelease>", self.search_themes)
        
        # Theme list section
        list_frame = tk.Frame(self.content_frame, bg=ColorScheme.BG_PRIMARY)
        list_frame.pack(fill="both", expand=True, pady=(15, 0))
        
        list_label = tk.Label(list_frame, text="Available Themes", 
                            bg=ColorScheme.BG_PRIMARY, fg=ColorScheme.TEXT_PRIMARY,
                            font=("Arial", 11, "bold"))
        list_label.pack(anchor="w", pady=(0, 5))
        
        self.widgets["theme_listbox"] = ModernListbox(list_frame)
        self.widgets["theme_listbox"].pack(fill="both", expand=True)
        
        self.load_themes()
        
    def create_export_content(self):
        """Create export mode content"""
        self.clear_content()
        
        # Export name section
        name_frame = tk.Frame(self.content_frame, bg=ColorScheme.BG_PRIMARY)
        name_frame.pack(fill="x", pady=(0, 20))
        
        name_label = tk.Label(name_frame, text="Theme Name", 
                            bg=ColorScheme.BG_PRIMARY, fg=ColorScheme.TEXT_PRIMARY,
                            font=("Arial", 11, "bold"))
        name_label.pack(anchor="w", pady=(0, 5))
        
        self.widgets["export_name_entry"] = ModernEntry(name_frame, placeholder="Enter theme name...")
        self.widgets["export_name_entry"].pack(fill="x")
        
        # Export type section
        type_frame = tk.Frame(self.content_frame, bg=ColorScheme.BG_PRIMARY)
        type_frame.pack(fill="x", pady=(20, 0))
        
        type_label = tk.Label(type_frame, text="Export Format", 
                            bg=ColorScheme.BG_PRIMARY, fg=ColorScheme.TEXT_PRIMARY,
                            font=("Arial", 11, "bold"))
        type_label.pack(anchor="w", pady=(0, 10))
        
        # Export options
        options_frame = tk.Frame(type_frame, bg=ColorScheme.BG_CARD, relief=tk.FLAT)
        options_frame.pack(fill="x", pady=5)
        
        zip_frame = tk.Frame(options_frame, bg=ColorScheme.BG_CARD)
        zip_frame.pack(side="left", padx=20, pady=15)
        
        self.zip_var = tk.BooleanVar(value=True)
        self.widgets["zip_checkbox"] = ModernCheckbox(zip_frame, text="Export as ZIP", 
                                                    variable=self.zip_var, 
                                                    command=lambda: self.set_export_type("zip"))
        self.widgets["zip_checkbox"].pack()
        
        folder_frame = tk.Frame(options_frame, bg=ColorScheme.BG_CARD)
        folder_frame.pack(side="right", padx=20, pady=15)
        
        self.folder_var = tk.BooleanVar(value=False)
        self.widgets["folder_checkbox"] = ModernCheckbox(folder_frame, text="Export as Folder", 
                                                       variable=self.folder_var, 
                                                       command=lambda: self.set_export_type("folder"))
        self.widgets["folder_checkbox"].pack()
        
    def create_action_section(self, parent):
        """Create action buttons section"""
        action_frame = tk.Frame(parent, bg=ColorScheme.BG_SECONDARY, height=70)
        action_frame.pack(fill="x", side="bottom")
        action_frame.pack_propagate(False)
        
        button_frame = tk.Frame(action_frame, bg=ColorScheme.BG_SECONDARY)
        button_frame.pack(side="right", padx=20, pady=15)
        
        # Preview button
        preview_btn = ModernButton(button_frame, text="Preview", command=self.preview_theme, style="secondary")
        preview_btn.pack(side="left", padx=(0, 10), ipadx=15)
        
        # Execute button
        execute_btn = ModernButton(button_frame, text="Execute", command=self.execute_operation, style="primary")
        execute_btn.pack(side="left", ipadx=15)
        
        return action_frame
        
    def setup_ui(self):
        """Setup the complete UI"""
        # Create main sections
        self.create_header(self.root)
        self.create_path_section(self.root)
        self.create_mode_section(self.root)
        self.create_content_section(self.root)
        self.create_action_section(self.root)
        
    def clear_content(self):
        """Clear dynamic content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def on_mode_change(self):
        """Handle mode selection change"""
        config_path = self.widgets["path_entry"].get()
        if not config_path:
            messagebox.showerror("Error", "Please select a config path first.")
            self.import_mode.set(False)
            self.export_mode.set(False)
            self.widgets["import_checkbox"].update_display()
            self.widgets["export_checkbox"].update_display()
            return
            
        # Ensure only one mode is selected
        if self.import_mode.get() and self.export_mode.get():
            if hasattr(self, '_last_mode') and self._last_mode == 'import':
                self.import_mode.set(False)
            else:
                self.export_mode.set(False)
                
        self._last_mode = 'import' if self.import_mode.get() else 'export'
        
        # Update UI based on mode
        if self.import_mode.get():
            self.create_import_content()
        elif self.export_mode.get():
            self.create_export_content()
        else:
            self.clear_content()
            
        # Update checkbox displays
        self.widgets["import_checkbox"].update_display()
        self.widgets["export_checkbox"].update_display()
        
    def set_export_type(self, export_type):
        """Set export type and update UI"""
        self.export_type.set(export_type)
        self.zip_var.set(export_type == "zip")
        self.folder_var.set(export_type == "folder")
        self.widgets["zip_checkbox"].update_display()
        self.widgets["folder_checkbox"].update_display()
        
    def select_config_path(self):
        """Select configuration path with validation"""
        path = filedialog.askdirectory(title="Select BBS Config Directory")
        if not path:
            return
            
        if "bbs" not in os.path.basename(path):
            messagebox.showerror("Error", "Please select a valid BBS config directory.")
            return
            
        bbs_json_path = os.path.join(path, "settings", "bbs.json")
        if not os.path.exists(bbs_json_path):
            messagebox.showerror("Error", "Selected directory lacks settings/bbs.json.")
            return
            
        self.widgets["path_entry"].delete(0, tk.END)
        self.widgets["path_entry"].insert(0, path)
        self.update_ui()
        
    def update_ui(self):
        """Update UI state"""
        self.on_mode_change()
        
    def load_themes(self):
        """Load available themes"""
        config_path = self.widgets["path_entry"].get()
        if not config_path:
            return
            
        theme_path = os.path.join(config_path, "theme")
        if not os.path.exists(theme_path):
            logging.warning(f"Theme directory not found: {theme_path}")
            return
            
        themes = [f for f in os.listdir(theme_path) 
                 if os.path.isdir(os.path.join(theme_path, f)) or f.endswith(".zip")]
        
        if "theme_listbox" in self.widgets:
            self.widgets["theme_listbox"].delete(0, tk.END)
            for theme in sorted(themes):
                self.widgets["theme_listbox"].insert(tk.END, theme)
                
    def search_themes(self, event=None):
        """Filter themes based on search"""
        if "search_entry" not in self.widgets or "theme_listbox" not in self.widgets:
            return
            
        search_term = self.widgets["search_entry"].get().lower()
        config_path = self.widgets["path_entry"].get()
        
        if not config_path:
            return
            
        theme_path = os.path.join(config_path, "theme")
        if not os.path.exists(theme_path):
            return
            
        all_themes = [f for f in os.listdir(theme_path) 
                     if os.path.isdir(os.path.join(theme_path, f)) or f.endswith(".zip")]
        
        filtered_themes = [theme for theme in all_themes if search_term in theme.lower()]
        
        self.widgets["theme_listbox"].delete(0, tk.END)
        for theme in sorted(filtered_themes):
            self.widgets["theme_listbox"].insert(tk.END, theme)
            
    def preview_theme(self):
        """Preview selected theme with modern UI"""
        config_path = self.widgets["path_entry"].get()
        if not config_path:
            messagebox.showerror("Error", "Please select a config path.")
            return
            
        try:
            if self.import_mode.get():
                theme_data = self.get_import_theme_data()
            elif self.export_mode.get():
                theme_data = self.get_export_theme_data()
            else:
                messagebox.showerror("Error", "Please select Import or Export mode.")
                return
                
            if not theme_data:
                return
                
            self.show_preview_window(theme_data)
            
        except Exception as e:
            logging.error(f"Error in preview: {e}")
            messagebox.showerror("Error", f"Preview failed: {e}")
            
    def get_import_theme_data(self):
        """Get theme data for import preview"""
        if "theme_listbox" not in self.widgets:
            messagebox.showerror("Error", "No themes loaded.")
            return None
            
        selected_theme = self.widgets["theme_listbox"].get(tk.ACTIVE)
        if not selected_theme:
            messagebox.showerror("Error", "Please select a theme to preview.")
            return None
            
        config_path = self.widgets["path_entry"].get()
        theme_path = os.path.join(config_path, "theme")
        
        # Handle ZIP files
        if selected_theme.endswith(".zip"):
            temp_dir = os.path.join(theme_path, "temp_preview")
            os.makedirs(temp_dir, exist_ok=True)
            
            try:
                shutil.unpack_archive(os.path.join(theme_path, selected_theme), temp_dir)
                config_files = glob.glob(os.path.join(temp_dir, '**', 'config.txt'), recursive=True)
                if not config_files:
                    messagebox.showerror("Error", "config.txt not found in ZIP file!")
                    return None
                    
                config_file = config_files[0]
                theme_dir = os.path.dirname(config_file)
            finally:
                # Cleanup will happen in calling function
                pass
        else:
            config_file = os.path.join(theme_path, selected_theme, "config.txt")
            theme_dir = os.path.join(theme_path, selected_theme)
            
        if not os.path.exists(config_file):
            messagebox.showerror("Error", "config.txt not found!")
            return None
            
        # Parse theme data
        theme_data = {}
        with open(config_file, "r") as file:
            for line in file:
                if ":" in line:
                    key, value = line.strip().split(":")
                    theme_data[key.strip('"')] = int(value.strip().strip(','))
                    
        return {
            "primary_color": theme_data.get("primary_color", 0),
            "background_color": theme_data.get("background_color", 0),
            "background_image": os.path.join(theme_dir, "background.png"),
            "cleanup_path": os.path.join(theme_path, "temp_preview") if selected_theme.endswith(".zip") else None
        }
        
    def get_export_theme_data(self):
        """Get theme data for export preview"""
        config_path = self.widgets["path_entry"].get()
        bbs_config_path = os.path.join(config_path, "settings", "bbs.json")
        
        if not os.path.exists(bbs_config_path):
            messagebox.showerror("Error", "bbs.json not found!")
            return None
            
        with open(bbs_config_path, "r") as file:
            config = json.load(file)
            
        return {
            "primary_color": config["appearance"].get("primary_color", 0),
            "background_color": config["background"].get("color", 0),
            "background_image": os.path.join(config_path, "assets", "textures", "background.png"),
            "cleanup_path": None
        }
        
    def show_preview_window(self, theme_data):
        """Show modern preview window"""
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Theme Preview")
        preview_window.geometry("500x600")
        preview_window.configure(bg=ColorScheme.BG_PRIMARY)
        preview_window.resizable(False, False)
        
        # Header
        header_frame = tk.Frame(preview_window, bg=ColorScheme.BG_SECONDARY, height=50)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="Theme Preview", 
                             bg=ColorScheme.BG_SECONDARY, fg=ColorScheme.TEXT_PRIMARY,
                             font=("Arial", 14, "bold"))
        title_label.pack(pady=15)
        
        # Content frame
        content_frame = tk.Frame(preview_window, bg=ColorScheme.BG_PRIMARY)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Color previews
        self.create_color_preview(content_frame, "Primary Color", theme_data["primary_color"])
        self.create_color_preview(content_frame, "Background Color", theme_data["background_color"])
        
        # Background image preview
        self.create_image_preview(content_frame, theme_data["background_image"], theme_data["background_color"])
        
        # Cleanup
        def on_close():
            if theme_data["cleanup_path"] and os.path.exists(theme_data["cleanup_path"]):
                shutil.rmtree(theme_data["cleanup_path"])
            preview_window.destroy()
            
        preview_window.protocol("WM_DELETE_WINDOW", on_close)
        
    def create_color_preview(self, parent, label_text, color_int):
        """Create color preview section"""
        section_frame = tk.Frame(parent, bg=ColorScheme.BG_PRIMARY)
        section_frame.pack(fill="x", pady=10)
        
        # Convert color
        alpha = (color_int >> 24) & 0xFF
        rgb = color_int & 0xFFFFFF
        hex_color = f"#{rgb:06x}"
        alpha_percent = alpha / 255.0
        
        # Label
        label = tk.Label(section_frame, text=f"{label_text} (Alpha: {alpha_percent:.2f})", 
                        bg=ColorScheme.BG_PRIMARY, fg=ColorScheme.TEXT_PRIMARY,
                        font=("Arial", 11, "bold"))
        label.pack(anchor="w", pady=(0, 5))
        
        # Color display
        color_frame = tk.Frame(section_frame, bg=ColorScheme.BG_CARD, relief=tk.FLAT, height=40)
        color_frame.pack(fill="x", pady=5)
        color_frame.pack_propagate(False)
        
        color_canvas = tk.Canvas(color_frame, bg=hex_color, highlightthickness=0, height=40)
        color_canvas.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Hex value
        hex_label = tk.Label(section_frame, text=hex_color.upper(), 
                           bg=ColorScheme.BG_PRIMARY, fg=ColorScheme.TEXT_SECONDARY,
                           font=("Arial", 9))
        hex_label.pack(anchor="w")
        
    def create_image_preview(self, parent, image_path, bg_color_int):
        """Create image preview section"""
        section_frame = tk.Frame(parent, bg=ColorScheme.BG_PRIMARY)
        section_frame.pack(fill="x", pady=20)
        
        # Label
        label = tk.Label(section_frame, text="Background Preview", 
                        bg=ColorScheme.BG_PRIMARY, fg=ColorScheme.TEXT_PRIMARY,
                        font=("Arial", 11, "bold"))
        label.pack(anchor="w", pady=(0, 10))
        
        # Preview canvas
        canvas_frame = tk.Frame(section_frame, bg=ColorScheme.BG_CARD, relief=tk.FLAT)
        canvas_frame.pack(fill="x", pady=5)
        
        preview_canvas = tk.Canvas(canvas_frame, width=400, height=200, highlightthickness=0)
        preview_canvas.pack(padx=10, pady=10)
        
        # Convert background color
        alpha = (bg_color_int >> 24) & 0xFF
        rgb = bg_color_int & 0xFFFFFF
        hex_color = f"#{rgb:06x}"
        alpha_percent = alpha / 255.0
        
        try:
            if os.path.exists(image_path):
                # Load and blend image
                rgb_tuple = ImageColor.getrgb(hex_color)
                bg_image = Image.new("RGBA", (400, 200), rgb_tuple + (int(alpha_percent * 255),))
                
                img = Image.open(image_path).convert("RGBA").resize((400, 200), Image.NEAREST)
                combined = Image.blend(bg_image, img, 0.6)
                
                photo = ImageTk.PhotoImage(combined)
                preview_canvas.create_image(200, 100, image=photo)
                preview_canvas.image = photo  # Keep reference
            else:
                # Show color only
                preview_canvas.configure(bg=hex_color)
                preview_canvas.create_text(200, 100, text="Image Not Found", 
                                         fill=ColorScheme.TEXT_PRIMARY, font=("Arial", 12))
        except Exception as e:
            logging.error(f"Error creating image preview: {e}")
            preview_canvas.configure(bg=hex_color)
            preview_canvas.create_text(200, 100, text="Error Loading Image", 
                                     fill=ColorScheme.TEXT_PRIMARY, font=("Arial", 12))
            
    def execute_operation(self):
        """Execute the selected operation"""
        if self.import_mode.get():
            self.execute_import()
        elif self.export_mode.get():
            self.execute_export()
        else:
            messagebox.showerror("Error", "Please select an operation mode.")
            
    def execute_import(self):
        """Execute theme import operation"""
        config_path = self.widgets["path_entry"].get()
        if not config_path:
            messagebox.showerror("Error", "Please select a config path.")
            return
            
        if "theme_listbox" not in self.widgets:
            messagebox.showerror("Error", "No themes loaded.")
            return
            
        selected_theme = self.widgets["theme_listbox"].get(tk.ACTIVE)
        if not selected_theme:
            messagebox.showerror("Error", "Please select a theme to import.")
            return
            
        try:
            self.import_theme(config_path, selected_theme)
            messagebox.showinfo("Success", "Theme imported successfully!")
        except Exception as e:
            logging.error(f"Import error: {e}")
            messagebox.showerror("Error", f"Import failed: {e}")
            
    def execute_export(self):
        """Execute theme export operation"""
        config_path = self.widgets["path_entry"].get()
        if not config_path:
            messagebox.showerror("Error", "Please select a config path.")
            return
            
        if "export_name_entry" not in self.widgets:
            messagebox.showerror("Error", "Export interface not loaded.")
            return
            
        export_name = self.widgets["export_name_entry"].get()
        if not export_name:
            messagebox.showerror("Error", "Please enter a theme name.")
            return
            
        try:
            self.export_theme(config_path, export_name)
            export_type = "ZIP file" if self.export_type.get() == "zip" else "folder"
            messagebox.showinfo("Success", f"Theme exported successfully as {export_type}!")
        except Exception as e:
            logging.error(f"Export error: {e}")
            messagebox.showerror("Error", f"Export failed: {e}")
            
    def import_theme(self, config_path: str, theme_name: str):
        """Import theme implementation"""
        theme_path = os.path.join(config_path, "theme")
        bbs_config_path = os.path.join(config_path, "settings", "bbs.json")
        textures_path = os.path.join(config_path, "assets", "textures")
        
        os.makedirs(textures_path, exist_ok=True)
        
        # Handle ZIP extraction
        if theme_name.endswith(".zip"):
            temp_dir = os.path.join(theme_path, "temp_import")
            os.makedirs(temp_dir, exist_ok=True)
            
            try:
                shutil.unpack_archive(os.path.join(theme_path, theme_name), temp_dir)
                config_files = glob.glob(os.path.join(temp_dir, '**', 'config.txt'), recursive=True)
                if not config_files:
                    raise Exception("config.txt not found in ZIP file!")
                    
                theme_config_file = config_files[0]
                theme_dir = os.path.dirname(theme_config_file)
            except Exception as e:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                raise e
        else:
            theme_config_file = os.path.join(theme_path, theme_name, "config.txt")
            theme_dir = os.path.join(theme_path, theme_name)
            
        if not os.path.exists(theme_config_file):
            raise Exception("config.txt not found in theme!")
            
        # Parse theme configuration
        theme_data = {}
        with open(theme_config_file, "r") as file:
            for line in file:
                if ":" in line:
                    key, value = line.strip().split(":")
                    theme_data[key.strip('"')] = int(value.strip().strip(','))
                    
        # Update BBS configuration
        with open(bbs_config_path, "r") as file:
            config = json.load(file)
            
        if "appearance" in config and "primary_color" in theme_data:
            config["appearance"]["primary_color"] = theme_data["primary_color"]
        if "background" in config and "background_color" in theme_data:
            config["background"]["color"] = theme_data["background_color"]
            
        with open(bbs_config_path, "w") as file:
            json.dump(config, file, indent=4)
            
        # Copy assets
        for asset_name in ["background.png", "icons.png"]:
            src_path = os.path.join(theme_dir, asset_name)
            if os.path.exists(src_path):
                shutil.copy(src_path, os.path.join(textures_path, asset_name))
                
        # Cleanup
        if theme_name.endswith(".zip") and os.path.exists(os.path.join(theme_path, "temp_import")):
            shutil.rmtree(os.path.join(theme_path, "temp_import"))
            
    def export_theme(self, config_path: str, theme_name: str):
        """Export theme implementation"""
        theme_dir = os.path.join(config_path, "theme", theme_name)
        zip_path = os.path.join(config_path, "theme", f"{theme_name}.zip")
        
        # Check for overwrite
        target_path = zip_path if self.export_type.get() == "zip" else theme_dir
        if os.path.exists(target_path):
            if not messagebox.askyesno("Confirm Overwrite", 
                                     f"'{theme_name}' already exists. Overwrite?"):
                return
                
        # Create theme directory
        if os.path.exists(theme_dir):
            shutil.rmtree(theme_dir)
        os.makedirs(theme_dir, exist_ok=True)
        
        try:
            # Read BBS configuration
            bbs_config_path = os.path.join(config_path, "settings", "bbs.json")
            with open(bbs_config_path, "r") as file:
                config = json.load(file)
                
            # Create config.txt
            config_file_path = os.path.join(theme_dir, "config.txt")
            with open(config_file_path, "w") as file:
                file.write('{\n')
                file.write(f'\t"primary_color": {config["appearance"]["primary_color"]},\n')
                file.write(f'\t"background_color": {config["background"]["color"]}\n')
                file.write('}')
                
            # Copy assets
            textures_path = os.path.join(config_path, "assets", "textures")
            for asset_name in ["background.png", "icons.png"]:
                src_path = os.path.join(textures_path, asset_name)
                if os.path.exists(src_path):
                    shutil.copy(src_path, os.path.join(theme_dir, asset_name))
                    
            # Handle export type
            if self.export_type.get() == "zip":
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                shutil.make_archive(os.path.join(config_path, "theme", theme_name), 'zip', theme_dir)
                shutil.rmtree(theme_dir)  # Remove temporary folder
                
        except Exception as e:
            if os.path.exists(theme_dir):
                shutil.rmtree(theme_dir)
            raise e
            
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = BBSThemeTool()
    app.run()