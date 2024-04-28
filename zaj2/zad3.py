from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

# Definicja klasy bazowej i modelu
Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    grade = Column(Float)
    """ Alternatywne wyswietlanie modelu
    def __repr__(self):
        return f"<Student(id={self.id}, name='{self.name}', age={self.age}, grade={self.grade})>"
    """

# Inicjalizacja silnika i sesji
engine = create_engine('sqlite:///students.sqlite')  # Zmień ścieżkę
Session = sessionmaker(bind=engine)
session = Session()

def add_student(name, age, grade):
    new_student = Student(name=name, age=age, grade=grade)
    session.add(new_student)
    session.commit()
    return new_student.id

def get_student(student_id):
    student = session.query(Student).filter(Student.id == student_id).first()
    if student:
        return f"Student ID: {student.id}, Name: {student.name}, Age: {student.age}, Grade: {student.grade}"
    else:
        return "Student not found"

def update_student(student_id, name=None, age=None, grade=None):
    student = session.query(Student).filter(Student.id == student_id).first()
    if student:
        if name:
            student.name = name
        if age:
            student.age = age
        if grade:
            student.grade = grade
        session.commit()
        return "Student updated successfully"
    else:
        return "Student not found"

def delete_student(student_id):
    student = session.query(Student).filter(Student.id == student_id).first()
    if student:
        session.delete(student)
        session.commit()
        return "Student deleted successfully"
    else:
        return "Student not found"

# Przykładowe użycie funkcji
print(get_student(3))

# Zamknięcie sesji
session.close()
