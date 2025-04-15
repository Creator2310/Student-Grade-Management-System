import tkinter as tk
from tkinter import ttk, messagebox
import json

class Student:
    def __init__(self, student_id, name, grades):
        self.student_id = student_id
        self.name = name
        self.grades = grades
        self.average = round(sum(grades) / len(grades), 2) if grades else 0.0

class StudentData:
    def __init__(self):
        self.students = []

    def add_student(self, student_id, name, grades):
        self.students.append(Student(student_id, name, grades))

    def remove_student(self, student_id):
        self.students = [s for s in self.students if s.student_id != student_id]

    def update_student(self, student_id, name, grades):
        for s in self.students:
            if s.student_id == student_id:
                s.name = name
                s.grades = grades
                s.average = round(sum(grades) / len(grades), 2) if grades else 0.0
                return True
        return False

    def get_all(self):
        return self.students

    def save_to_file(self, filename="students.json"):
        data = [
            {
                "student_id": s.student_id,
                "name": s.name,
                "grades": s.grades,
                "average": s.average
            } for s in self.students
        ]
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def load_from_file(self, filename="students.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                for s in data:
                    self.add_student(s["student_id"], s["name"], s["grades"])
        except FileNotFoundError:
            print("No existing file found. Starting fresh.")

class GradeManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Grade Management System")
        self.root.geometry("900x550")
        self.data = StudentData()
        self.data.load_from_file()
        self.create_widgets()
        self.display_students()

    def create_widgets(self):
        # Search bar
        search_frame = ttk.Frame(self.root)
        search_frame.pack(pady=5)

        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_student).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Clear", command=self.display_students).pack(side=tk.LEFT, padx=5)

        # Title label
        title = ttk.Label(self.root, text="🎓 Student Grade Management System", font=("Helvetica", 20, "bold"))
        title.pack(pady=10)

        # Treeview for displaying students
        self.tree = ttk.Treeview(self.root, columns=("ID", "Name", "Grades", "Average"), show="headings")
        self.tree.heading("ID", text="Student ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Grades", text="Grades")
        self.tree.heading("Average", text="Average")
        self.tree.column("ID", width=100, anchor="center")
        self.tree.column("Name", width=200, anchor="center")
        self.tree.column("Grades", width=250, anchor="center")
        self.tree.column("Average", width=100, anchor="center")
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        # Sorting options
        sort_frame = ttk.Frame(self.root)
        sort_frame.pack(pady=10)

        self.sort_var = tk.StringVar()
        self.sort_var.set("Average")  # Default sorting by average grade
        sort_options = ["Student ID", "Name", "Average"]
        ttk.Combobox(sort_frame, textvariable=self.sort_var, values=sort_options, state="readonly").pack(side=tk.LEFT, padx=5)
        ttk.Button(sort_frame, text="Sort", command=self.sort_students).pack(side=tk.LEFT, padx=5)

        # Buttons for operations
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Add Student", command=self.open_add_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit Student", command=self.open_edit_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Remove Student", command=self.open_delete_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save to File", command=self.save_data).pack(side=tk.LEFT, padx=5)

    def display_students(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for s in self.data.get_all():
            self.tree.insert("", tk.END, values=(s.student_id, s.name, s.grades, s.average))

    # --- Add Student Window ---
    def open_add_window(self):
        win = tk.Toplevel(self.root)
        win.title("Add Student")
        win.geometry("350x300")
        win.resizable(False, False)

        tk.Label(win, text="Student ID:", font=("Arial", 12)).pack(pady=5)
        id_entry = ttk.Entry(win)
        id_entry.pack(pady=5)

        tk.Label(win, text="Name:", font=("Arial", 12)).pack(pady=5)
        name_entry = ttk.Entry(win)
        name_entry.pack(pady=5)

        tk.Label(win, text="Grades (space-separated):", font=("Arial", 12)).pack(pady=5)
        grades_entry = ttk.Entry(win)
        grades_entry.pack(pady=5)

        def add_student_action():
            try:
                sid = int(id_entry.get())
                name = name_entry.get().strip()
                grades = list(map(float, grades_entry.get().strip().split()))
                if not name or not grades:
                    raise ValueError("Name and grades are required.")
                # Check for duplicate ID
                if any(s.student_id == sid for s in self.data.get_all()):
                    messagebox.showerror("Error", "Student ID already exists.")
                    return
                self.data.add_student(sid, name, grades)
                self.display_students()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid input: {e}")

        ttk.Button(win, text="Add", command=add_student_action).pack(pady=15)

    # --- Edit Student Window ---
    def open_edit_window(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a student to edit.")
            return
        item = self.tree.item(selected[0])
        student_id = item["values"][0]
        current_name = item["values"][1]
        current_grades = item["values"][2]

        win = tk.Toplevel(self.root)
        win.title("Edit Student")
        win.geometry("350x300")
        win.resizable(False, False)

        tk.Label(win, text="Student ID (unchangeable):", font=("Arial", 12)).pack(pady=5)
        id_label = tk.Label(win, text=str(student_id), font=("Arial", 12, "bold"))
        id_label.pack(pady=5)

        tk.Label(win, text="Name:", font=("Arial", 12)).pack(pady=5)
        name_entry = ttk.Entry(win)
        name_entry.insert(0, current_name)
        name_entry.pack(pady=5)

        tk.Label(win, text="Grades (space-separated):", font=("Arial", 12)).pack(pady=5)
        grades_entry = ttk.Entry(win)
        grades_entry.insert(0, " ".join(map(str, current_grades)))
        grades_entry.pack(pady=5)

        def edit_student_action():
            try:
                name = name_entry.get().strip()
                grades = list(map(float, grades_entry.get().strip().split()))
                if not name or not grades:
                    raise ValueError("Name and grades are required.")
                self.data.update_student(student_id, name, grades)
                self.display_students()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid input: {e}")

        ttk.Button(win, text="Update", command=edit_student_action).pack(pady=15)

    # --- Delete Student Window ---
    def open_delete_window(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a student to remove.")
            return
        item = self.tree.item(selected[0])
        student_id = item["values"][0]
        student_name = item["values"][1]

        win = tk.Toplevel(self.root)
        win.title("Remove Student")
        win.geometry("350x150")
        win.resizable(False, False)

        tk.Label(win, text=f"Are you sure you want to remove\n'{student_name}' (ID: {student_id})?", font=("Arial", 12)).pack(pady=20)

        def delete_action():
            self.data.remove_student(student_id)
            self.display_students()
            win.destroy()

        btn_frame = ttk.Frame(win)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Yes, Remove", command=delete_action).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cancel", command=win.destroy).pack(side=tk.LEFT, padx=10)

    def save_data(self):
        self.data.save_to_file()
        messagebox.showinfo("Saved", "Student data saved successfully!")

    def search_student(self):
        query = self.search_var.get().strip().lower()
        if not query:
            messagebox.showwarning("Search", "Please enter a name or ID to search.")
            return
        results = []
        for s in self.data.get_all():
        # Match by ID, full/partial name, or first letter(s) of name
            if (
                query in str(s.student_id).lower()
                or s.name.lower().startswith(query)
        ):
                results.append(s)
        for row in self.tree.get_children():
            self.tree.delete(row)
        for s in results:
            self.tree.insert("", tk.END, values=(s.student_id, s.name, s.grades, s.average))
        if not results:
            messagebox.showinfo("Search", "No matching student found.")

    def sort_students(self):
        sort_criteria = self.sort_var.get()
        if sort_criteria == "Student ID":
            self.data.students.sort(key=lambda s: s.student_id)
        elif sort_criteria == "Name":
            self.data.students.sort(key=lambda s: s.name.lower())
        elif sort_criteria == "Average":
            self.data.students.sort(key=lambda s: s.average, reverse=True)
        self.display_students()

if __name__ == "__main__":
    root = tk.Tk()
    app = GradeManagementApp(root)
    root.mainloop()
