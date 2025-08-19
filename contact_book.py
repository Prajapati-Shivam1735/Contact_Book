import tkinter as tk
from tkinter import messagebox
import mysql.connector

# --- MySQL Connection ---
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="server",
    database="contact_book"
)
cursor = conn.cursor()

contact_map = {}

# --- Functions ---
def load_contacts():
    listbox.delete(0, tk.END)
    contact_map.clear()
    cursor.execute("SELECT name, phone FROM contacts ORDER BY name")
    for name, phone in cursor.fetchall():
        display = f"{name} ({phone})"
        listbox.insert(tk.END, display)
        contact_map[display] = name

def add_contact():
    name = entry_name.get().strip()
    phone = entry_phone.get().strip()

    if not name:
        messagebox.showwarning("Input Error", "Name is required.")
        return

    cursor.execute("SELECT id FROM contacts WHERE name = %s", (name,))
    if cursor.fetchone():
        messagebox.showerror("Duplicate", "Contact already exists.")
        return

    cursor.execute("INSERT INTO contacts (name, phone) VALUES (%s, %s)", (name, phone))
    conn.commit()
    load_contacts()
    clear_fields()
    messagebox.showinfo("Success", f"Contact '{name}' added.")

def delete_contact():
    selected = listbox.curselection()
    if not selected:
        messagebox.showwarning("No selection", "Select a contact to delete.")
        return

    display = listbox.get(selected[0])
    name = contact_map.get(display)
    if not name:
        return

    cursor.execute("DELETE FROM contacts WHERE name = %s", (name,))
    conn.commit()
    load_contacts()
    clear_fields()
    messagebox.showinfo("Deleted", f"Contact '{name}' deleted.")

def update_contact():
    name = entry_name.get().strip()
    phone = entry_phone.get().strip()

    if not name:
        messagebox.showwarning("Input Error", "Name is required.")
        return

    cursor.execute("SELECT id FROM contacts WHERE name = %s", (name,))
    if not cursor.fetchone():
        messagebox.showwarning("Not Found", "Contact does not exist.")
        return

    cursor.execute("UPDATE contacts SET phone = %s WHERE name = %s", (phone, name))
    conn.commit()
    load_contacts()
    messagebox.showinfo("Updated", f"Contact '{name}' updated.")

def show_contact_details(event):
    selected = listbox.curselection()
    if not selected:
        return

    display = listbox.get(selected[0])
    name = contact_map.get(display)
    if not name:
        return

    cursor.execute("SELECT phone FROM contacts WHERE name = %s", (name,))
    result = cursor.fetchone()
    if result:
        phone = result[0]
        entry_name.delete(0, tk.END)
        entry_name.insert(0, name)
        entry_phone.delete(0, tk.END)
        entry_phone.insert(0, phone)

def clear_fields():
    entry_name.delete(0, tk.END)
    entry_phone.delete(0, tk.END)

def search_contact():
    query = entry_search.get().strip()
    if not query:
        load_contacts()
        return

    listbox.delete(0, tk.END)
    contact_map.clear()

    cursor.execute("SELECT name, phone FROM contacts WHERE name LIKE %s ORDER BY name", ('%' + query + '%',))
    for name, phone in cursor.fetchall():
        display = f"{name} ({phone})"
        listbox.insert(tk.END, display)
        contact_map[display] = name

# --- GUI Setup ---
app = tk.Tk()
app.title("Contact Book Application")

# Center the window
window_width = 600
window_height = 400
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))
app.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Main container
main_frame = tk.Frame(app)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# --- Left Frame ---
left_frame = tk.Frame(main_frame)
left_frame.pack(side=tk.LEFT, fill=tk.Y)

tk.Label(left_frame, text="Name").pack()
entry_name = tk.Entry(left_frame)
entry_name.pack()

tk.Label(left_frame, text="Phone").pack()
entry_phone = tk.Entry(left_frame)
entry_phone.pack()

tk.Button(left_frame, text="Add Contact", command=add_contact).pack(pady=5)
tk.Button(left_frame, text="Update Contact", command=update_contact).pack(pady=5)
tk.Button(left_frame, text="Delete Contact", command=delete_contact).pack(pady=5)

tk.Label(left_frame, text="Search").pack(pady=(10,0))
entry_search = tk.Entry(left_frame)
entry_search.pack()
tk.Button(left_frame, text="Search", command=search_contact).pack(pady=5)

# --- Right Frame ---
right_frame = tk.Frame(main_frame)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(50, 0))

scrollbar = tk.Scrollbar(right_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox = tk.Listbox(right_frame, yscrollcommand=scrollbar.set)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
listbox.bind("<<ListboxSelect>>", show_contact_details)

scrollbar.config(command=listbox.yview)

# --- Load Data ---
load_contacts()
app.mainloop()
