# File to test out sqlite database module in python
import sqlite3

class Student:

    def __init__(self, name, school):
        self.name = name
        self.school = school

def create_db_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
 
    return None

def add_new_student_to_table(conn, student):
    """
    Add a specified student to the students database.
    :param conn: the db connection object
    :param student: the student object to be added to db
    :return: student id, the id of the student added
    """
    sql_statement = 'INSERT INTO students(name, school) VALUES(?, ?)'
    student_record = (student.name, student.school)
    cur = conn.cursor()
    cur.execute(sql_statement, student_record)

def get_all_students_in_table(conn):
    """
    return all the students in the table
    """
    sql_statement = 'SELECT * FROM students'
    cur = conn.cursor()
    cur.execute(sql_statement)

    return cur.fetchall()

def close_db(conn):
    """
    Commit changes and close DB connection
    """
    conn.commit()
    conn.close()



student_db_conn = create_db_connection("students.db")
curr = student_db_conn.cursor()

# Create the students table
curr.execute('''CREATE TABLE IF NOT EXISTS students
             (ID INTEGER PRIMARY KEY, name TEXT, school TEXT);''')

s = Student("Conrad McArthur", "Hasselbank School of Bioengineering")
add_new_student_to_table(student_db_conn, s)

s2 = Student("Jeeves Coloria", "Ponqui Institute of Germanic Arts")
add_new_student_to_table(student_db_conn, s2)

print(get_all_students_in_table(student_db_conn))

close_db(student_db_conn)
