from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class UserInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    bairro = db.Column(db.String(100), nullable=False)
    numero = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"<UserInfo {self.name}>"
#
#
