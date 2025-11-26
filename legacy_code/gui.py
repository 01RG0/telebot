"""
GUI module for admin interface using CustomTkinter
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import logging
import sys
import os

# Add parent directory to path to allow importing from root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import WINDOW_TITLE, WINDOW_SIZE, SEND_DELAY
from database import db
from bot_handler import send_template_to_selected, send_personalized_from_rows

logger = logging.getLogger("telegram_app.gui")

# Set appearance
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class AdminApp(ctk.CTk):
    """Main admin GUI application"""
    
    def __init__(self):
        super().__init__()
        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)
        
        # Initialize data structures
        self.user_vars = {}   # chat_id -> BooleanVar
        self.user_rows = {}   # chat_id -> widget dict
        self.imported_rows = []  # list of {"target":, "message":}
        self.select_all_state = False
        
        # Build UI
        self._create_toolbar()
        self._create_user_list()
        self._create_bottom_panel()
        
        # Initial load
        self.refresh_user_list()
    
    def _create_toolbar(self):
        """Create top toolbar with search and action buttons"""
        toolbar = ctk.CTkFrame(self)
        toolbar.pack(fill="x", padx=8, pady=8)
        
        # Search input
        self.search_var = tk.StringVar()
        self.search_input = ctk.CTkEntry(
            toolbar, 
            width=300, 
            textvariable=self.search_var, 
            placeholder_text="Search by name or id"
        )
        self.search_input.pack(side="left", padx=(4, 8))
        self.search_input.bind("<KeyRelease>", lambda e: self.refresh_user_list())
        
        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            toolbar, 
            text="Refresh", 
            command=self.refresh_user_list
        )
        self.refresh_btn.pack(side="left", padx=4)
        
        # Export button
        self.export_btn = ctk.CTkButton(
            toolbar, 
            text="Export users", 
            command=self.export_users
        )
        self.export_btn.pack(side="left", padx=4)
        
        # Load Excel button
        self.load_excel_btn = ctk.CTkButton(
            toolbar, 
            text="Load Excel (A=target, B=message)", 
            command=self.load_excel
        )
        self.load_excel_btn.pack(side="left", padx=4)
        
        # Select all button
        self.select_all_btn = ctk.CTkButton(
            toolbar, 
            text="Select All", 
            command=self.toggle_select_all
        )
        self.select_all_btn.pack(side="left", padx=4)
    
    def _create_user_list(self):
        """Create scrollable user list frame"""
        self.list_frame = ctk.CTkScrollableFrame(self, width=940, height=380)
        self.list_frame.pack(padx=8, pady=8)
    
    def _create_bottom_panel(self):
        """Create bottom panel with message entry and send buttons"""
        bottom = ctk.CTkFrame(self)
        bottom.pack(fill="x", padx=8, pady=8)
        
        # Template entry
        self.template_entry = ctk.CTkEntry(
            bottom, 
            width=560, 
            placeholder_text="Message template; use {name} or {chat_id}"
        )
        self.template_entry.pack(side="left", padx=6)
        
        # Send to selected button
        self.send_template_btn = ctk.CTkButton(
            bottom, 
            text="Send to Selected", 
            command=self.send_template_selected
        )
        self.send_template_btn.pack(side="left", padx=6)
        
        # Send imported button
        self.send_imported_btn = ctk.CTkButton(
            bottom, 
            text="Send Imported Rows", 
            command=self.send_imported_rows
        )
        self.send_imported_btn.pack(side="left", padx=6)
    
    def refresh_user_list(self):
        """Refresh the user list display"""
        # Clear existing widgets
        for w in self.list_frame.winfo_children():
            w.destroy()
        self.user_vars.clear()
        self.user_rows.clear()
        
        # Get search query
        q = (self.search_var.get() or "").strip().lower()
        
        # Get users from database
        rows = db.get_users()
        
        for chat_id, name in rows:
            # Filter by search query
            combined = f"{chat_id} {name or ''}".lower()
            if q and q not in combined:
                continue
            
            # Create checkbox variable
            var = tk.BooleanVar(value=False)
            self.user_vars[chat_id] = var
            
            # Create row frame
            row = ctk.CTkFrame(self.list_frame)
            row.pack(fill="x", padx=6, pady=4)
            
            # Checkbox
            chk = ctk.CTkCheckBox(row, variable=var, text="")
            chk.pack(side="left", padx=(6, 8))
            
            # User info label
            lbl_text = f"{name}    |    {chat_id}"
            lbl = ctk.CTkLabel(row, text=lbl_text, anchor="w")
            lbl.pack(side="left", padx=6, fill="x", expand=True)
            
            # Delete button
            edit_btn = ctk.CTkButton(
                row, 
                text="Delete", 
                width=80, 
                fg_color="red",
                command=lambda c=chat_id: self.delete_user_confirm(c)
            )
            edit_btn.pack(side="right", padx=6)
            
            self.user_rows[chat_id] = {
                "frame": row, 
                "label": lbl, 
                "delete": edit_btn
            }
    
    def toggle_select_all(self):
        """Toggle select/deselect all users"""
        self.select_all_state = not self.select_all_state
        self.select_all_btn.configure(
            text="Deselect All" if self.select_all_state else "Select All"
        )
        for var in self.user_vars.values():
            var.set(self.select_all_state)
    
    def export_users(self):
        """Export users to CSV or Excel file"""
        rows = db.get_users()
        df = pd.DataFrame(rows, columns=["chat_id", "name"])
        
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
        )
        
        if not path:
            return
        
        try:
            if path.endswith(".csv"):
                df.to_csv(path, index=False)
            else:
                df.to_excel(path, index=False)
            messagebox.showinfo("Export", f"Exported {len(df)} users to:\n{path}")
            logger.info(f"Exported {len(df)} users to {path}")
        except Exception as e:
            logger.exception(f"Export failed: {e}")
            messagebox.showerror("Export error", str(e))
    
    def load_excel(self):
        """Load personalized messages from Excel file"""
        path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx;*.xls")]
        )
        
        if not path:
            return
        
        try:
            df = pd.read_excel(path, engine="openpyxl")
            
            # Expect at least two columns: A=target, B=message
            if df.shape[1] < 2:
                messagebox.showerror(
                    "Format error", 
                    "Excel must contain at least two columns: A=target, B=message"
                )
                return
            
            out = []
            for _, r in df.iterrows():
                a = r.iloc[0]
                b = r.iloc[1]
                if pd.isna(a) or pd.isna(b):
                    continue
                out.append({"target": str(a).strip(), "message": str(b)})
            
            self.imported_rows = out
            messagebox.showinfo("Imported", f"Imported {len(out)} rows from Excel.")
            logger.info(f"Imported {len(out)} rows from {path}")
        except Exception as e:
            logger.exception(f"Import Excel failed: {e}")
            messagebox.showerror("Import error", str(e))
    
    def send_imported_rows(self):
        """Send personalized messages from imported Excel data"""
        if not self.imported_rows:
            messagebox.showinfo(
                "No data", 
                "No imported rows. Use Load Excel first."
            )
            return
        
        # Confirm
        if not messagebox.askyesno(
            "Confirm send", 
            f"Send {len(self.imported_rows)} personalized messages?"
        ):
            return
        
        sent, failed = send_personalized_from_rows(self.imported_rows, delay=SEND_DELAY)
        messagebox.showinfo("Done", f"Sent: {len(sent)} | Failed: {len(failed)}")
        logger.info(f"Imported send done. Sent: {len(sent)} Failed: {len(failed)}")
    
    def send_template_selected(self):
        """Send template message to selected users"""
        # Get selected chat_ids
        selected = [cid for cid, var in self.user_vars.items() if var.get()]
        
        if not selected:
            messagebox.showinfo("No selection", "Select users first.")
            return
        
        template = self.template_entry.get().strip()
        if not template:
            messagebox.showerror(
                "No template", 
                "Enter a message template (use {name} or {chat_id})."
            )
            return
        
        if not messagebox.askyesno(
            "Confirm", 
            f"Send template to {len(selected)} users?"
        ):
            return
        
        sent, failed = send_template_to_selected(selected, template, delay=SEND_DELAY)
        messagebox.showinfo("Done", f"Sent: {len(sent)} | Failed: {len(failed)}")
        logger.info(f"Template send done. Sent: {len(sent)} Failed: {len(failed)}")
    
    def delete_user_confirm(self, chat_id):
        """Confirm and delete a user"""
        if messagebox.askyesno("Delete", f"Delete user {chat_id} from DB?"):
            try:
                db.delete_user(chat_id)
                self.refresh_user_list()
                messagebox.showinfo("Deleted", "User deleted.")
                logger.info(f"User {chat_id} deleted via GUI")
            except Exception as e:
                logger.exception(f"Delete user failed: {e}")
                messagebox.showerror("Error", str(e))
