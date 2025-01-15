from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class client(db.Model):


    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(255))
    number = db.Column(db.String(20))
    city = db.Column(db.String(100))
    cellphone = db.Column(db.String(20))

    def __repr__(self):
        return f"<Client {self.name}>"


