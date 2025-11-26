# app.py  — All-in-one Telegram bot + admin GUI + Excel sender
import os
import threading
import time
import logging
import sqlite3
from pathlib import Path
import telebot
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import pandas as pd

# -----------------------------
# CONFIG
# -----------------------------
TOKEN = "8334074221:AAE8pGbyawYLnZmDlQd4fRXoW0p0hvO7koY"   # <<-- put your bot token here
DB_PATH = "users.db"
LOGFILE = "app.log"
SEND_DELAY = 0.5                # seconds between sends (safe pace)
WELCOME_MSG = "اهلا بيك في نظام المتابعة لمستر شادي الشرقاوي شكرا على ثقتك بنتمنى نكون عند حسن ظنك"

# -----------------------------
# Logging
# -----------------------------
logging.basicConfig(filename=LOGFILE,
                    level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("telegram_app")

# -----------------------------
# DATABASE (simple SQLite)
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        chat_id INTEGER PRIMARY KEY,
        name TEXT,
        joined_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def add_or_update_user(chat_id: int, name: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Insert or update name if already exists
    c.execute("INSERT OR IGNORE INTO users (chat_id, name, joined_at) VALUES (?, ?, datetime('now'))",
              (chat_id, name))
    c.execute("UPDATE users SET name=? WHERE chat_id=?", (name, chat_id))
    conn.commit()
    conn.close()

def get_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT chat_id, name FROM users ORDER BY name")
    rows = c.fetchall()
    conn.close()
    return rows

def get_user_by_chat(chat_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT chat_id, name FROM users WHERE chat_id=?", (chat_id,))
    r = c.fetchone()
    conn.close()
    return r

def find_users_by_name(name):
    # case-insensitive contains search
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    pattern = f"%{name}%"
    c.execute("SELECT chat_id, name FROM users WHERE lower(name) LIKE lower(?)", (pattern,))
    rows = c.fetchall()
    conn.close()
    return rows

def delete_user(chat_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE chat_id=?", (chat_id,))
    conn.commit()
    conn.close()

# -----------------------------
# TELEGRAM BOT
# -----------------------------
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

@bot.message_handler(commands=["start"])
def on_start(message):
    try:
        chat_id = message.chat.id
        name = message.from_user.first_name or ""
        add_or_update_user(chat_id, name)
        bot.send_message(chat_id, WELCOME_MSG)
        logger.info(f"New/updated user: {chat_id} | {name}")
    except Exception as e:
        logger.exception("Error in /start handler: %s", e)

@bot.message_handler(func=lambda m: True)
def on_message(message):
    """
    We only store chat_id + name on any message (no asking for phone/ID).
    If new user messages, we add them with available name.
    We respond politely that they are registered.
    """
    try:
        chat_id = message.chat.id
        name = message.from_user.first_name or ""
        add_or_update_user(chat_id, name)
        # Optional quick reply — keep simple
        # We do not collect phone or ID per your instruction
        bot.send_message(chat_id, WELCOME_MSG)
    except Exception as e:
        logger.exception("Error in message handler: %s", e)

def run_bot_forever():
    # resilient polling loop
    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=60)
        except Exception as e:
            logger.exception("Bot polling crashed, restarting: %s", e)
            time.sleep(5)

# -----------------------------
# SENDING UTILITIES
# -----------------------------
def safe_send_message(chat_id, text):
    try:
        bot.send_message(chat_id, text)
        logger.info("Sent to %s", chat_id)
        return True, None
    except Exception as e:
        logger.exception("Failed to send to %s: %s", chat_id, e)
        return False, str(e)

def send_bulk_by_chatids(chat_ids, message, delay=SEND_DELAY):
    sent, failed = [], []
    for cid in chat_ids:
        ok, err = safe_send_message(cid, message)
        if ok:
            sent.append(cid)
        else:
            failed.append((cid, err))
        time.sleep(delay)
    return sent, failed

def send_template_to_selected(chat_ids, template, delay=SEND_DELAY):
    sent, failed = [], []
    for cid in chat_ids:
        user = get_user_by_chat(cid)
        name = user[1] if user else ""
        try:
            msg = template.format(name=name or "", chat_id=cid)
        except Exception:
            msg = template
        ok, err = safe_send_message(cid, msg)
        if ok:
            sent.append(cid)
        else:
            failed.append((cid, err))
        time.sleep(delay)
    return sent, failed

def send_personalized_from_rows(rows, delay=SEND_DELAY):
    # rows: list of dicts {"target": <chat_id or name>, "message": <text>}
    sent, failed = [], []
    for r in rows:
        target = r.get("target")
        message = r.get("message", "")
        # if target numeric → chat_id
        if isinstance(target, (int,)) or (isinstance(target, str) and target.isdigit()):
            cid = int(target)
            ok, err = safe_send_message(cid, message)
            if ok: sent.append(cid)
            else: failed.append((cid, err))
        else:
            # treat as name search (take first match)
            matches = find_users_by_name(str(target))
            if not matches:
                failed.append((target, "no matching user by name"))
            else:
                # send to all matches (or you might choose first one)
                for cid, name in matches:
                    ok, err = safe_send_message(cid, message)
                    if ok: sent.append(cid)
                    else: failed.append((cid, err))
        time.sleep(delay)
    return sent, failed

# -----------------------------
# GUI (CustomTkinter)
# -----------------------------
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AdminApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Telegram Admin - Mr Shady")
        self.geometry("980x660")

        # Top toolbar
        toolbar = ctk.CTkFrame(self)
        toolbar.pack(fill="x", padx=8, pady=8)

        self.search_var = tk.StringVar()
        self.search_input = ctk.CTkEntry(toolbar, width=300, textvariable=self.search_var, placeholder_text="Search by name or id")
        self.search_input.pack(side="left", padx=(4,8))
        self.search_input.bind("<KeyRelease>", lambda e: self.refresh_user_list())

        self.refresh_btn = ctk.CTkButton(toolbar, text="Refresh", command=self.refresh_user_list)
        self.refresh_btn.pack(side="left", padx=4)

        self.export_btn = ctk.CTkButton(toolbar, text="Export users", command=self.export_users)
        self.export_btn.pack(side="left", padx=4)

        self.load_excel_btn = ctk.CTkButton(toolbar, text="Load Excel (A=target, B=message)", command=self.load_excel)
        self.load_excel_btn.pack(side="left", padx=4)

        self.select_all_state = False
        self.select_all_btn = ctk.CTkButton(toolbar, text="Select All", command=self.toggle_select_all)
        self.select_all_btn.pack(side="left", padx=4)

        # Middle user list
        self.list_frame = ctk.CTkScrollableFrame(self, width=940, height=380)
        self.list_frame.pack(padx=8, pady=8)

        # bottom: message entry and sending
        bottom = ctk.CTkFrame(self)
        bottom.pack(fill="x", padx=8, pady=8)

        self.template_entry = ctk.CTkEntry(bottom, width=560, placeholder_text="Message template; use {name} or {chat_id}")
        self.template_entry.pack(side="left", padx=6)
        self.send_template_btn = ctk.CTkButton(bottom, text="Send to Selected", command=self.send_template_selected)
        self.send_template_btn.pack(side="left", padx=6)

        self.send_imported_btn = ctk.CTkButton(bottom, text="Send Imported Rows", command=self.send_imported_rows)
        self.send_imported_btn.pack(side="left", padx=6)

        # data
        self.user_vars = {}   # chat_id -> BooleanVar
        self.user_rows = {}   # chat_id -> widget dict
        self.imported_rows = []  # list of {"target":, "message":}

        # initial load
        self.refresh_user_list()

    def refresh_user_list(self):
        # clear
        for w in self.list_frame.winfo_children():
            w.destroy()
        self.user_vars.clear()
        self.user_rows.clear()

        q = (self.search_var.get() or "").strip().lower()
        rows = get_users()
        for chat_id, name in rows:
            combined = f"{chat_id} {name or ''}".lower()
            if q and q not in combined:
                continue
            var = tk.BooleanVar(value=False)
            self.user_vars[chat_id] = var

            row = ctk.CTkFrame(self.list_frame)
            row.pack(fill="x", padx=6, pady=4)

            chk = ctk.CTkCheckBox(row, variable=var, text="")
            chk.pack(side="left", padx=(6,8))

            lbl_text = f"{name}    |    {chat_id}"
            lbl = ctk.CTkLabel(row, text=lbl_text, anchor="w")
            lbl.pack(side="left", padx=6, fill="x", expand=True)

            edit_btn = ctk.CTkButton(row, text="Delete", width=80, fg_color="red", command=lambda c=chat_id: self.delete_user_confirm(c))
            edit_btn.pack(side="right", padx=6)

            self.user_rows[chat_id] = {"frame": row, "label": lbl, "delete": edit_btn}

    def toggle_select_all(self):
        self.select_all_state = not self.select_all_state
        self.select_all_btn.configure(text="Deselect All" if self.select_all_state else "Select All")
        for var in self.user_vars.values():
            var.set(self.select_all_state)

    def export_users(self):
        rows = get_users()
        df = pd.DataFrame(rows, columns=["chat_id", "name"])
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV files","*.csv"),("Excel files","*.xlsx")])
        if not path:
            return
        try:
            if path.endswith(".csv"):
                df.to_csv(path, index=False)
            else:
                df.to_excel(path, index=False)
            messagebox.showinfo("Export", f"Exported {len(df)} users to:\n{path}")
        except Exception as e:
            logger.exception("Export failed: %s", e)
            messagebox.showerror("Export error", str(e))

    def load_excel(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files","*.xlsx;*.xls")])
        if not path:
            return
        try:
            df = pd.read_excel(path, engine="openpyxl")
            # Expect at least two columns: A target, B message
            if df.shape[1] < 2:
                messagebox.showerror("Format error", "Excel must contain at least two columns: A=target, B=message")
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
        except Exception as e:
            logger.exception("Import Excel failed: %s", e)
            messagebox.showerror("Import error", str(e))

    def send_imported_rows(self):
        if not self.imported_rows:
            messagebox.showinfo("No data", "No imported rows. Use Load Excel first.")
            return
        # Confirm
        if not messagebox.askyesno("Confirm send", f"Send {len(self.imported_rows)} personalized messages?"):
            return
        sent, failed = send_personalized_from_rows(self.imported_rows, delay=SEND_DELAY)
        messagebox.showinfo("Done", f"Sent: {len(sent)} | Failed: {len(failed)}")
        logger.info("Imported send done. Sent: %s Failed: %s", len(sent), len(failed))

    def send_template_selected(self):
        # get selected chat_ids
        selected = [cid for cid, var in self.user_vars.items() if var.get()]
        if not selected:
            messagebox.showinfo("No selection", "Select users first.")
            return
        template = self.template_entry.get().strip()
        if not template:
            messagebox.showerror("No template", "Enter a message template (use {name} or {chat_id}).")
            return
        if not messagebox.askyesno("Confirm", f"Send template to {len(selected)} users?"):
            return
        sent, failed = send_template_to_selected(selected, template, delay=SEND_DELAY)
        messagebox.showinfo("Done", f"Sent: {len(sent)} | Failed: {len(failed)}")
        logger.info("Template send done. Sent: %s Failed: %s", len(sent), len(failed))

    def delete_user_confirm(self, chat_id):
        if messagebox.askyesno("Delete", f"Delete user {chat_id} from DB?"):
            try:
                delete_user(chat_id)
                self.refresh_user_list()
                messagebox.showinfo("Deleted", "User deleted.")
            except Exception as e:
                logger.exception("Delete user failed: %s", e)
                messagebox.showerror("Error", str(e))

# -----------------------------
# START EVERYTHING
# -----------------------------
def main():
    init_db()
    # try quick bot check (non-blocking)
    try:
        bot.get_me()
    except Exception as e:
        logger.warning("bot.get_me() failed (still okay if network blocked): %s", e)

    # start bot thread
    t = threading.Thread(target=run_bot_forever, daemon=True)
    t.start()

    # start GUI
    app = AdminApp()
    app.mainloop()

if __name__ == "__main__":
    main()