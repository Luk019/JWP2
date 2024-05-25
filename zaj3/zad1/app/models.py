from app import db

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    subject = db.Column(db.String(120), unique=True, nullable=False)
    time = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return '<Teacher %r>' % self.name