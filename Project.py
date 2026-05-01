import tkinter as tk
from tkinter import ttk, messagebox
import json

students = []

#------------------ LIGHT/DARK MODE TOGGLE ------------------#
current_theme = "light"

light_theme = {
    "bg": "#f0f0f0",
    "fg": "black",
    "entry_bg": "white",
    "tree_bg": "white"
}

dark_theme = {
    "bg": "#1e1e1e",
    "fg": "white",
    "entry_bg": "#2b2b2b",
    "tree_bg": "#2b2b2b"
}

def apply_theme(theme):
    root.configure(bg=theme["bg"])

    # Labels
    for widget in root.winfo_children():
        if isinstance(widget, tk.Label):
            widget.configure(bg=theme["bg"], fg=theme["fg"])

    # Entries
    for entry in [name_entry, roll_entry, marks_entry]:
        entry.configure(bg=theme["entry_bg"], fg=theme["fg"], insertbackground=theme["fg"])

    # Treeview style
    style = ttk.Style()
    style.theme_use("default")

    style.configure("Treeview",
                    background=theme["tree_bg"],
                    foreground=theme["fg"],
                    fieldbackground=theme["tree_bg"])

    style.map("Treeview",
              background=[("selected", "#6a9cff")])
    
def toggle_theme():
    global current_theme

    if current_theme == "light":
        apply_theme(dark_theme)
        current_theme = "dark"
    else:
        apply_theme(light_theme)
        current_theme = "light"

# ------------------ FILE HANDLING ------------------ #
def save_data():
    with open('students.json', 'w') as f:
        json.dump(students, f, indent=4)

def load_data():
    global students
    try:
        with open('students.json', 'r') as f:
            students = json.load(f)
    except FileNotFoundError:
        students = []

# ------------------ TABLE REFRESH ------------------ #
def refresh_table():
    for row in tree.get_children():
        tree.delete(row)
    for student in students:
        tree.insert("", tk.END, values=(student['name'], student['roll_no'], student['marks']))

# ------------------ ADD STUDENT ------------------ #
def add_student():
    name = name_entry.get()
    roll_no = roll_entry.get()
    marks = marks_entry.get()

    if not name or not roll_no or not marks:
        messagebox.showwarning("Input Error", "All fields are required!")
        return

    try:
        marks = int(marks)
    except ValueError:
        messagebox.showerror("Error", "Marks must be a number!")
        return

    # Prevent duplicate roll number
    for student in students:
        if student['roll_no'] == roll_no:
            messagebox.showerror("Error", "Roll number already exists!")
            return

    students.append({
        "name": name,
        "roll_no": roll_no,
        "marks": marks
    })

    save_data()
    refresh_table()

    name_entry.delete(0, tk.END)
    roll_entry.delete(0, tk.END)
    marks_entry.delete(0, tk.END)

    messagebox.showinfo("Success", "Student added successfully!")

# ------------------ DELETE STUDENT ------------------ #
def delete_student():
    selected = tree.selection()

    if not selected:
        messagebox.showwarning("Warning", "Select a student!")
        return

    item = tree.item(selected[0])
    roll = str(item['values'][1])
    name = item['values'][0]

    # 🔥 Confirmation popup
    confirm = messagebox.askyesno(
        "Confirm Delete",
        f"Are you sure you want to delete:\n\n{name} (Roll No: {roll})?"
    )

    if not confirm:
        return  # user clicked "No"

    deleted = False

    for student in students:
        if str(student['roll_no']) == roll:
            students.remove(student)
            deleted = True
            break

    if deleted:
        save_data()
        refresh_table()
        messagebox.showinfo("Deleted", "Student removed successfully!")
    else:
        messagebox.showerror("Error", "Student not found!")

# ------------------ UPDATE STUDENT ------------------ #
def update_student():
    selected = tree.selection()

    if not selected:
        messagebox.showwarning("Warning", "Select a student!")
        return

    item = tree.item(selected[0])
    values = item['values']

    roll = str(values[1])

    # 🪟 Create popup window
    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Student")
    edit_window.geometry("300x250")
    edit_window.configure(bg="#f0f0f0")

    # Labels + Entries
    tk.Label(edit_window, text="Name:", bg="#f0f0f0").pack(pady=5)
    name_entry_edit = tk.Entry(edit_window)
    name_entry_edit.pack()
    name_entry_edit.insert(0, values[0])

    tk.Label(edit_window, text="Roll No:", bg="#f0f0f0").pack(pady=5)
    roll_entry_edit = tk.Entry(edit_window)
    roll_entry_edit.pack()
    roll_entry_edit.insert(0, values[1])
    roll_entry_edit.config(state="disabled")  # 🔒 prevent editing roll no

    tk.Label(edit_window, text="Marks:", bg="#f0f0f0").pack(pady=5)
    marks_entry_edit = tk.Entry(edit_window)
    marks_entry_edit.pack()
    marks_entry_edit.insert(0, values[2])

    # 💾 Save button inside popup
    def save_changes():
        new_name = name_entry_edit.get()
        new_marks = marks_entry_edit.get()

        if not new_name or not new_marks:
            messagebox.showwarning("Error", "All fields required!")
            return

        try:
            new_marks = int(new_marks)
        except:
            messagebox.showerror("Error", "Marks must be number!")
            return

        updated = False

        for student in students:
            if str(student['roll_no']) == roll:
                student['name'] = new_name
                student['marks'] = new_marks
                updated = True
                break

        if updated:
            save_data()
            refresh_table()
            messagebox.showinfo("Success", "Student updated!")
            edit_window.destroy()  # close popup
        else:
            messagebox.showerror("Error", "Student not found!")

    tk.Button(edit_window, text="Save Changes", command=save_changes).pack(pady=15)

# ------------------ SEARCH STUDENT ------------------ #
def search_student():
    roll = roll_entry.get()

    for row in tree.get_children():
        tree.delete(row)

    found = False
    for student in students:
        if student['roll_no'] == roll:
            tree.insert("", tk.END, values=(student['name'], student['roll_no'], student['marks']))
            found = True

    if not found:
        messagebox.showinfo("Result", "Student not found!")

# ------------------ SORT STUDENTS ------------------ #
def sort_students():
    students.sort(key=lambda x: x['marks'], reverse=True)
    save_data()
    refresh_table()

# ------------------ GUI SETUP ------------------ #
root = tk.Tk()
root.title("Smart Student Manager")
root.geometry("700x500")
root.configure(bg="#f0f0f0")

# Title
tk.Label(root, text="Smart Student Manager",
         font=("Arial", 20), bg="#f0f0f0").grid(row=0, column=0, columnspan=2, pady=20)

# Input Fields
tk.Label(root, text="Name:", font=("Arial", 14), bg="#f0f0f0").grid(row=1, column=0)
name_entry = tk.Entry(root)
name_entry.grid(row=1, column=1)

tk.Label(root, text="Roll No:", font=("Arial", 14), bg="#f0f0f0").grid(row=2, column=0)
roll_entry = tk.Entry(root)
roll_entry.grid(row=2, column=1)

tk.Label(root, text="Marks:", font=("Arial", 14), bg="#f0f0f0").grid(row=3, column=0)
marks_entry = tk.Entry(root)
marks_entry.grid(row=3, column=1)

# Buttons
tk.Button(root, text="Add Student", command=add_student, width=15).grid(row=4, column=0, pady=10)
tk.Button(root, text="Update Student", command=update_student, width=15).grid(row=4, column=1)

tk.Button(root, text="Delete Student", command=delete_student, width=15).grid(row=5, column=0)
tk.Button(root, text="Search Student", command=search_student, width=15).grid(row=5, column=1)

tk.Button(root, text="Sort by Marks", command=sort_students, width=32).grid(row=6, column=0, columnspan=2, pady=10)
tk.Button(root, text="🌙 Toggle Mode", command=toggle_theme).grid(row=0, column=2, padx=10)

# Table
columns = ("Name", "Roll No", "Marks")
tree = ttk.Treeview(root, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)

tree.grid(row=7, column=0, columnspan=2, padx=10, pady=20)

# Load Data
load_data()
refresh_table()
apply_theme(light_theme)

root.mainloop()