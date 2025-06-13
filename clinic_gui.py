import sqlite3
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox

conn = sqlite3.connect("clinic.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        pid TEXT PRIMARY KEY,
        name TEXT,
        age TEXT,
        gender TEXT,
        contact TEXT
    )
""")
conn.commit()

class ClinicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clinic Patient Management System")
        self.root.geometry("850x550")
        self.selected_id = None

        tb.Label(root, text="Clinic Patient Management System", font=("Arial", 20, "bold")).pack(pady=10)

        form = tb.Frame(root)
        form.pack(pady=10)

        labels = ["Patient ID", "Name", "Age", "Gender", "Contact"]
        self.entries = {}

        for i, label in enumerate(labels):
            tb.Label(form, text=label + ":").grid(row=i, column=0, sticky="e", padx=10, pady=5)
            if label == "Gender":
                entry = tb.Combobox(form, values=["Male", "Female", "Other"], width=25, bootstyle="info")
            else:
                entry = tb.Entry(form, width=27, bootstyle="primary")
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[label.lower()] = entry

        btns = tb.Frame(root)
        btns.pack(pady=10)

        tb.Button(btns, text="Add", width=15, bootstyle="success", command=self.add_patient).grid(row=0, column=0, padx=5)
        tb.Button(btns, text="Update", width=15, bootstyle="warning", command=self.update_patient).grid(row=0, column=1, padx=5)
        tb.Button(btns, text="Delete", width=15, bootstyle="danger", command=self.delete_patient).grid(row=0, column=2, padx=5)
        tb.Button(btns, text="Clear", width=15, bootstyle="secondary", command=self.clear_fields).grid(row=0, column=3, padx=5)

        self.tree = tb.Treeview(root, columns=("ID", "Name", "Age", "Gender", "Contact"), show="headings", bootstyle="info")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.bind("<<TreeviewSelect>>", self.load_selected)
        self.tree.pack(pady=15, fill="both", expand=True)

        self.refresh_table()

    def get_form_data(self):
        return {
            "pid": self.entries["patient id"].get(),
            "name": self.entries["name"].get(),
            "age": self.entries["age"].get(),
            "gender": self.entries["gender"].get(),
            "contact": self.entries["contact"].get()
        }

    def add_patient(self):
        data = self.get_form_data()
        if not all(data.values()):
            messagebox.showwarning("Missing Info", "Please fill all fields.")
            return
        try:
            cursor.execute("INSERT INTO patients VALUES (?, ?, ?, ?, ?)", tuple(data.values()))
            conn.commit()
            self.refresh_table()
            self.clear_fields()
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate ID", "Patient ID already exists.")

    def update_patient(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Please select a patient to update.")
            return
        data = self.get_form_data()
        cursor.execute("""
            UPDATE patients SET name=?, age=?, gender=?, contact=? WHERE pid=?
        """, (data['name'], data['age'], data['gender'], data['contact'], self.selected_id))
        conn.commit()
        self.refresh_table()
        self.clear_fields()

    def delete_patient(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Please select a patient to delete.")
            return
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this patient?")
        if confirm:
            cursor.execute("DELETE FROM patients WHERE pid=?", (self.selected_id,))
            conn.commit()
            self.refresh_table()
            self.clear_fields()

    def load_selected(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        values = self.tree.item(selected)['values']
        self.selected_id = values[0]
        for i, key in enumerate(["patient id", "name", "age", "gender", "contact"]):
            self.entries[key].delete(0, "end")
            self.entries[key].insert(0, values[i])

    def clear_fields(self):
        for entry in self.entries.values():
            entry.delete(0, "end")
        self.selected_id = None

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        cursor.execute("SELECT * FROM patients")
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

if __name__ == "__main__":
    app = tb.Window(themename="darkly")
    ClinicApp(app)
    app.mainloop()
