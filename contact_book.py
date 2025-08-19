import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector

# MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",       
    password="server", 
    database="contact_book"
)
cursor = conn.cursor()

# Dictionary to map contact name to phone
contact_map = {}

# GUI functions
def load_contacts():
    tree.delete(*tree.get_children())   # clear previous entries
    contact_map.clear()

    cursor.execute("SELECT name, phone FROM contacts ORDER BY name")
    rows = cursor.fetchall()

    for index, (name, phone) in enumerate(rows):
        tag = "evenrow" if index % 2 == 0 else "oddrow"
        tree.insert("", tk.END, values=(name, phone), tags=(tag,))
        contact_map[name] = phone

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
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("No selection", "Select a contact to delete.")
        return

    item = tree.item(selected[0])
    name, phone = item["values"]

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
    selected = tree.selection()
    if not selected:
        return

    item = tree.item(selected[0])
    name, phone = item["values"]

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

    tree.delete(*tree.get_children())
    contact_map.clear()

    cursor.execute("SELECT name, phone FROM contacts WHERE name LIKE %s ORDER BY name", ('%' + query + '%',))
    rows = cursor.fetchall()

    for index, (name, phone) in enumerate(rows):
        tag = "evenrow" if index % 2 == 0 else "oddrow"
        tree.insert("", tk.END, values=(name, phone), tags=(tag,))
        contact_map[name] = phone

# --- GUI Setup ---
app = tk.Tk()
app.title("Contact Book (MySQL)")
app.geometry("600x400")

# Center window on screen
app.update_idletasks()
w = 600
h = 400
x = (app.winfo_screenwidth() // 2) - (w // 2)
y = (app.winfo_screenheight() // 2) - (h // 2)
app.geometry(f"{w}x{h}+{x}+{y}")

# Main Frame (holds left and right frames)
main_frame = tk.Frame(app)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Left frame for form and buttons
left_frame = tk.Frame(main_frame)
left_frame.pack(side=tk.LEFT, fill=tk.Y)

# Input fields
tk.Label(left_frame, text="Name").pack()
entry_name = tk.Entry(left_frame)
entry_name.pack()

tk.Label(left_frame, text="Phone").pack()
entry_phone = tk.Entry(left_frame)
entry_phone.pack()

# Buttons
tk.Button(left_frame, text="Add Contact", command=add_contact).pack(pady=5)
tk.Button(left_frame, text="Update Contact", command=update_contact).pack(pady=5)
tk.Button(left_frame, text="Delete Contact", command=delete_contact).pack(pady=5)

# Search
tk.Label(left_frame, text="Search").pack()
entry_search = tk.Entry(left_frame)
entry_search.pack()
tk.Button(left_frame, text="Search", command=search_contact).pack(pady=5)

# Right frame for Treeview
right_frame = tk.Frame(main_frame)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(50, 0))

# Scrollbar
scrollbar = tk.Scrollbar(right_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Treeview Styling
style = ttk.Style()
style.configure("Treeview", rowheight=25, font=("Arial", 10))
style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

# Treeview (Name & Phone columns)
tree = ttk.Treeview(right_frame, columns=("Name", "Phone"), show="headings", yscrollcommand=scrollbar.set)
tree.heading("Name", text="Name")
tree.heading("Phone", text="Phone")
tree.column("Name", width=200, anchor="center")
tree.column("Phone", width=150, anchor="center")
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Scrollbar config
scrollbar.config(command=tree.yview)

# Striped row colors
tree.tag_configure("oddrow", background="#f2f2f2")
tree.tag_configure("evenrow", background="#ffffff")

# Bind selection
tree.bind("<<TreeviewSelect>>", show_contact_details)

# Load contacts on startup
load_contacts()

app.mainloop()
