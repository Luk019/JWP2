from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class Census(Base):
    __tablename__ = 'census'
    id = Column(Integer, primary_key=True)
    state = Column(String)
    sex = Column(String)
    age = Column(Integer)
    pop2000 = Column(Integer)
    pop2008 = Column(Integer)

engine = create_engine('sqlite:///census.sqlite')
Session = sessionmaker(bind=engine)
session = Session()

states = session.query(Census.state).distinct().all()
print("Nazwy stanów:")
for state in states:
    print(state.state)

states_to_check = ['Alaska', 'New York']
for state in states_to_check:
    population_2000 = session.query(func.sum(Census.pop2000)).filter(Census.state == state).scalar()
    population_2008 = session.query(func.sum(Census.pop2008)).filter(Census.state == state).scalar()
    print(f"Populacja w stanie {state} w roku 2000: {population_2000}")
    print(f"Populacja w stanie {state} w roku 2008: {population_2008}")

sex_counts = session.query(Census.sex, func.sum(Census.pop2008)).filter(Census.state == 'New York').group_by(Census.sex).all()
print("Liczba kobiet i mężczyzn w stanie New York w roku 2008:")
for sex, count in sex_counts:
    print(f"{sex}: {count}")

session.close()
