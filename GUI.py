import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class LogViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Log Concatenator Pro")
        self.root.geometry("1100x700")
        self.root.minsize(800, 600)
        
        # Configure style
        self.setup_style()
        
        # Main container
        self.main_frame = ttk.Frame(root, padding=(10, 10, 10, 10))
        self.main_frame.pack(fill="both", expand=True)
        
        # Application variables
        self.log_files = []
        
        # Build UI components
        self.create_header()
        self.create_tabs()
        
    def setup_style(self):
        """Configure the visual style of the application"""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Custom colors
        style.configure("TFrame", background="#f8f9fa")
        style.configure("TLabel", background="#f8f9fa", font=("Segoe UI", 9))
        style.configure("TButton", font=("Segoe UI", 9), padding=6)
        style.configure("TEntry", font=("Segoe UI", 9), padding=5)
        style.configure("TNotebook", background="#f8f9fa")
        style.configure("TNotebook.Tab", font=("Segoe UI", 9, "bold"), padding=(10, 5))
        
        # Custom button colors
        style.map("Accent.TButton",
                  foreground=[("pressed", "white"), ("active", "white")],
                  background=[("pressed", "#0056b3"), ("active", "#0069d9")])
        style.configure("Accent.TButton", foreground="white", background="#007bff")
        
    def create_header(self):
        """Create the top control panel"""
        header_frame = ttk.Frame(self.main_frame, padding=(0, 0, 0, 10))
        header_frame.pack(fill="x")
        
        # Project folder selection
        folder_label = ttk.Label(header_frame, text="Project Folder:")
        folder_label.pack(side="left", padx=(0, 5))
        
        self.path_var = tk.StringVar()
        folder_entry = ttk.Entry(
            header_frame, 
            textvariable=self.path_var, 
            width=60,
            font=("Segoe UI", 9)
        )
        folder_entry.pack(side="left", expand=True, fill="x", padx=5)
        
        # Buttons with icons (text emoji as placeholder)
        browse_btn = ttk.Button(
            header_frame, 
            text="📁 Browse", 
            command=self.browse_folder,
            style="Accent.TButton"
        )
        browse_btn.pack(side="left", padx=(5, 5))
        
        execute_btn = ttk.Button(
            header_frame, 
            text="🟢 Execute", 
            command=self.load_logs,
            style="Accent.TButton"
        )
        execute_btn.pack(side="left")
        
    def create_tabs(self):
        #Create the notebook with tabs
        self.tabs = ttk.Notebook(self.main_frame)
        self.tabs.pack(fill="both", expand=True)
        
        # Tab 1: Log Files
        self.create_log_tab()
        
        # Tab 2: Output Viewer
        self.create_output_tab()
        
    def create_log_tab(self):
        #Create the log files viewer tab
        self.log_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.log_tab, text="Log Files")
        
        # Split view with listbox and text area
        log_split = ttk.PanedWindow(self.log_tab, orient="horizontal")
        log_split.pack(fill="both", expand=True)
        
        # Log list container
        list_frame = ttk.Frame(log_split, padding=(0, 0, 5, 0))
        log_split.add(list_frame, weight=1)
        
        list_label = ttk.Label(list_frame, text="Available Log Files:")
        list_label.pack(anchor="w", pady=(0, 5))
        
        # Listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill="both", expand=True)
        
        y_scroll = ttk.Scrollbar(list_container, orient="vertical")
        y_scroll.pack(side="right", fill="y")
        
        self.log_listbox = tk.Listbox(
            list_container,
            yscrollcommand=y_scroll.set,
            selectbackground="#e7f3ff",
            selectforeground="black",
            activestyle="none",
            font=("Consolas", 10),
            borderwidth=1,
            relief="solid",
            highlightthickness=0
        )
        self.log_listbox.pack(fill="both", expand=True)
        y_scroll.config(command=self.log_listbox.yview)
        
        # Log content viewer
        text_frame = ttk.Frame(log_split)
        log_split.add(text_frame, weight=3)
        
        text_label = ttk.Label(text_frame, text="Log Content:")
        text_label.pack(anchor="w", pady=(0, 5))
        
        text_container = ttk.Frame(text_frame)
        text_container.pack(fill="both", expand=True)
        
        self.log_text = tk.Text(
            text_container,
            wrap="none",
            font=("Consolas", 10),
            bg="white",
            padx=5,
            pady=5,
            borderwidth=1,
            relief="solid",
            highlightthickness=0
        )
        
        y_scroll_text = ttk.Scrollbar(text_container, orient="vertical")
        x_scroll_text = ttk.Scrollbar(text_container, orient="horizontal")
        
        y_scroll_text.pack(side="right", fill="y")
        x_scroll_text.pack(side="bottom", fill="x")
        
        self.log_text.pack(fill="both", expand=True)
        
        self.log_text.config(
            yscrollcommand=y_scroll_text.set,
            xscrollcommand=x_scroll_text.set
        )
        y_scroll_text.config(command=self.log_text.yview)
        x_scroll_text.config(command=self.log_text.xview)
        
        # Bind selection event
        self.log_listbox.bind("<<ListboxSelect>>", self.show_log_content)
        
    def create_output_tab(self):
        #Create the output.txt viewer tab
        self.output_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.output_tab, text="Output Viewer")
        
        # Output text container
        text_frame = ttk.Frame(self.output_tab)
        text_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.output_text = tk.Text(
            text_frame,
            wrap="none",
            font=("Consolas", 10),
            bg="white",
            padx=5,
            pady=5,
            borderwidth=1,
            relief="solid",
            highlightthickness=0
        )
        
        y_scroll = ttk.Scrollbar(text_frame, orient="vertical")
        x_scroll = ttk.Scrollbar(text_frame, orient="horizontal")
        
        y_scroll.pack(side="right", fill="y")
        x_scroll.pack(side="bottom", fill="x")
        
        self.output_text.pack(fill="both", expand=True)
        
        self.output_text.config(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )
        y_scroll.config(command=self.output_text.yview)
        x_scroll.config(command=self.output_text.xview)
        
    def browse_folder(self):
      #Open folder dialog and set path
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)
            self.root.focus()  # Return focus to main window
            
    def load_logs(self):
        #Load log files from selected folder
        folder = self.path_var.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Error", "Please select a valid folder.")
            return

        # Clear existing data
        self.log_files.clear()
        self.log_listbox.delete(0, tk.END)
        self.log_text.delete(1.0, tk.END)
        self.output_text.delete(1.0, tk.END)

        # Load all .log files
        found_logs = False
        for dirpath, _, filenames in os.walk(folder):
            for filename in filenames:
                if filename.endswith(".log"):
                    full_path = os.path.join(dirpath, filename)
                    self.log_files.append(full_path)
                    rel_name = os.path.relpath(full_path, folder)
                    self.log_listbox.insert(tk.END, rel_name)
                    found_logs = True

        # Load output.txt if exists
        output_path = os.path.join(folder, "output.txt")
        if os.path.isfile(output_path):
            try:
                with open(output_path, "r", encoding="utf-8") as f:
                    self.output_text.insert(tk.END, f.read())
            except Exception as e:
                self.output_text.insert(tk.END, f"Error reading output.txt:\n{str(e)}")
        else:
            self.output_text.insert(tk.END, "No output.txt found in the selected folder.")

        if not found_logs:
            messagebox.showinfo("No Logs", "No .log files found in the selected folder.")
            
    def show_log_content(self, event):
        #Display selected log file content
        selection = self.log_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        log_file = self.log_files[index]

        try:
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(tk.END, content)
                self.log_text.see("1.0")  # Scroll to top
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LogViewerApp(root)
    
    try:
        root.iconbitmap(default="icon.ico")  
    except:
        pass  
        
    root.mainloop()