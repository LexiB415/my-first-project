import sqlite3
con = sqlite3.connect("StudentRecords.db")
cur = con.cursor()
#cur.execute("CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, major TEXT)")

# cur.execute("INSERT INTO students VALUES (1, 'Alice', 20, 'Computer Science')")
# cur.execute("INSERT INTO students VALUES (2, 'Bob', 22, 'Mathematics')")
# cur.execute("INSERT INTO students VALUES (3, 'Charlie', 21, 'Physics')")
# cur.execute("INSERT INTO students VALUES (4, 'David', 23, 'Chemistry')")
# cur.execute("INSERT INTO students VALUES (5, 'Eve', 20, 'Biology')")

con.commit()

cur.execute("SELECT name, age, major FROM students")
rows = cur.fetchall()
for r in rows:
    print(r)

student = (input("Would you like to add a student? (yes/no): "))
if student == 'yes':
    student = (input("Enter name: "), int(input("Enter age: ")), input("Enter major: "))
cur.execute("INSERT INTO students (name, age, major) VALUES (?, ?, ?)", student)
con.commit()