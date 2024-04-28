from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

# Definicja klasy bazowej za pomocą nowego importu
Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    grade = Column(Float)

engine = create_engine('sqlite:///students.sqlite')

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
"""
# Dodawanie przykładowych danych
students_data = [
    {'name': 'Andrzej Kowalski ', 'age': 20, 'grade': 4.5},
    {'name': 'Marek Kon', 'age': 22, 'grade': 3.0},
    {'name': 'Alicja Mak', 'age': 21, 'grade': 5.0}
]

for student_data in students_data:
    new_student = Student(name=student_data['name'], age=student_data['age'], grade=student_data['grade'])
    session.add(new_student)

session.commit()
"""
# Wyświetlanie dodanych danych
students = session.query(Student).all()
for student in students:
    print(f"{student.id}, {student.name}, {student.age}, {student.grade}")

session.close()
