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
        self.id_map = {}
        self.name_map = {}

    def add_student(self, student_id, name, grades):
        student = Student(student_id, name, grades)
        self.students.append(student)
        self.id_map[student_id] = student
        self.name_map[name.lower()] = student
        self.students.sort(key=lambda s: s.student_id)  # Keep sorted by ID for binary search

    def remove_student(self, student_id):
        self.students = [s for s in self.students if s.student_id != student_id]
        self.id_map.pop(student_id, None)
        for name, s in list(self.name_map.items()):
            if s.student_id == student_id:
                self.name_map.pop(name)

    def update_student(self, student_id, name, grades):
        student = self.id_map.get(student_id)
        if student:
            old_name = student.name.lower()
            student.name = name
            student.grades = grades
            student.average = round(sum(grades) / len(grades), 2)
            self.name_map.pop(old_name, None)
            self.name_map[name.lower()] = student
            return True
        return False

    def binary_search_by_id(self, student_id):
        low, high = 0, len(self.students) - 1
        while low <= high:
            mid = (low + high) // 2
            if self.students[mid].student_id == student_id:
                return self.students[mid]
            elif self.students[mid].student_id < student_id:
                low = mid + 1
            else:
                high = mid - 1
        return None

    def get_student_by_id(self, student_id):
        return self.id_map.get(student_id)

    def get_student_by_name(self, name_query):
        return self.name_map.get(name_query.lower())

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
            pass

class GradeManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Grade Management System")
        self.root.geometry("900x550")
        self.data = StudentData()
        self.data.load_from_file()
        self.setup_ui()
        self.display_students()

    def setup_ui(self):
        search_frame = ttk.Frame(self.root)
        search_frame.pack(pady=5)

        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_student).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Clear", command=self.display_students).pack(side=tk.LEFT, padx=5)

        title = ttk.Label(self.root, text="🎓 Student Grade Management System", font=("Helvetica", 20, "bold"))
        title.pack(pady=10)

        self.tree = ttk.Treeview(self.root, columns=("ID", "Name", "Grades", "Average"), show="headings")
        for col in ["ID", "Name", "Grades", "Average"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Add", command=self.add_student_popup).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit", command=self.edit_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete", command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save", command=self.save_data).pack(side=tk.LEFT, padx=5)

    def display_students(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for s in self.data.get_all():
            self.tree.insert("", tk.END, values=(s.student_id, s.name, s.grades, s.average))

    def add_student_popup(self):
        win = tk.Toplevel(self.root)
        win.title("Add Student")

        ttk.Label(win, text="Student ID:").pack()
        entry_id = ttk.Entry(win)
        entry_id.pack()

        ttk.Label(win, text="Name:").pack()
        entry_name = ttk.Entry(win)
        entry_name.pack()

        ttk.Label(win, text="Grades (space-separated):").pack()
        entry_grades = ttk.Entry(win)
        entry_grades.pack()

        def submit():
            try:
                sid = int(entry_id.get())
                name = entry_name.get().strip()
                grades = list(map(float, entry_grades.get().strip().split()))
                if not name or not grades:
                    raise ValueError("Invalid input")
                if self.data.get_student_by_id(sid):
                    raise ValueError("Student ID already exists")
                self.data.add_student(sid, name, grades)
                self.display_students()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(win, text="Add", command=submit).pack(pady=10)

    def edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a student to edit.")
            return

        item = self.tree.item(selected[0])
        sid = item["values"][0]
        student = self.data.get_student_by_id(sid)

        win = tk.Toplevel(self.root)
        win.title("Edit Student")

        ttk.Label(win, text="ID (cannot edit)").pack()
        entry_id = ttk.Entry(win)
        entry_id.insert(0, str(student.student_id))
        entry_id.config(state="disabled")
        entry_id.pack()

        ttk.Label(win, text="Name").pack()
        entry_name = ttk.Entry(win)
        entry_name.insert(0, student.name)
        entry_name.pack()

        ttk.Label(win, text="Grades (space-separated)").pack()
        entry_grades = ttk.Entry(win)
        entry_grades.insert(0, " ".join(map(str, student.grades)))
        entry_grades.pack()

        def submit():
            try:
                name = entry_name.get().strip()
                grades = list(map(float, entry_grades.get().split()))
                if not name or not grades:
                    raise ValueError("All fields are required")
                self.data.update_student(student.student_id, name, grades)
                self.display_students()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(win, text="Update", command=submit).pack(pady=10)

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a student to delete.")
            return

        item = self.tree.item(selected[0])
        sid = item["values"][0]
        self.data.remove_student(sid)
        self.display_students()

    def save_data(self):
        self.data.save_to_file()
        messagebox.showinfo("Saved", "Student data saved successfully!")

    def search_student(self):
        query = self.search_var.get().strip().lower()
        if not query:
            messagebox.showwarning("Search", "Enter a name or ID")
            return

        results = []
        if query.isdigit():
            student = self.data.binary_search_by_id(int(query))
            if student:
                results.append(student)
        else:
            for student in self.data.get_all():
                if student.name.lower() == query or student.name.lower().startswith(query):
                    results.append(student)

        for row in self.tree.get_children():
            self.tree.delete(row)
        for s in results:
            self.tree.insert("", tk.END, values=(s.student_id, s.name, s.grades, s.average))
        if not results:
            messagebox.showinfo("Search", "No match found")

if __name__ == "__main__":
    root = tk.Tk()
    app = GradeManagementApp(root)
    root.mainloop()
