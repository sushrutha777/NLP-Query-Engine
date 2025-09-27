# sample_db_init.py
import sqlite3

conn = sqlite3.connect("company_demo.db")
c = conn.cursor()

c.executescript("""
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;
""")

c.execute("""
CREATE TABLE departments (
    dept_id INTEGER PRIMARY KEY,
    dept_name TEXT,
    manager_id INTEGER
)
""")

c.execute("""
CREATE TABLE employees (
    emp_id INTEGER PRIMARY KEY,
    full_name TEXT,
    dept_id INTEGER,
    position TEXT,
    annual_salary REAL,
    join_date TEXT,
    skills TEXT,
    reports_to INTEGER,
    office_location TEXT,
    FOREIGN KEY(dept_id) REFERENCES departments(dept_id)
)
""")

departments = [
    (1, "Engineering", None),
    (2, "Product", None),
    (3, "HR", None)
]
c.executemany("INSERT INTO departments (dept_id, dept_name, manager_id) VALUES (?, ?, ?)", departments)

employees = [
    (1, "Alice Johnson", 1, "Senior Engineer", 120000, "2023-03-15", "Python,SQL,ML", None, "Bangalore"),
    (2, "Bob Smith", 1, "Engineer", 90000, "2024-01-10", "Java,Python", 1, "Bangalore"),
    (3, "Carol Lee", 2, "Product Manager", 110000, "2022-07-05", "roadmaps,communication", None, "Bangalore"),
    (4, "David Kim", 1, "Engineering Manager", 150000, "2019-10-01", "management,python", None, "Mumbai"),
    (5, "Eve Patel", 3, "HR Executive", 70000, "2021-11-11", "people,process", None, "Bangalore")
]
c.executemany("""INSERT INTO employees (emp_id, full_name, dept_id, position, annual_salary, join_date, skills, reports_to, office_location) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", employees)

conn.commit()
conn.close()
print("Created company_demo.db with sample data.")
