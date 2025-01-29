from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class DiaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    text = db.Column(db.Text, nullable=False)
    user = db.relationship('UserInfo', backref=db.backref('diary_entries', lazy=True))



class UserInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False,unique = True)
    email = db.Column(db.String(100), nullable=False,unique = True)
    phone = db.Column(db.String(20), nullable=False,unique = True)
    state = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    bairro = db.Column(db.String(100), nullable=False)
    numero = db.Column(db.String(10), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False)









    def __repr__(self):
        return f"<UserInfo {self.name}>"
#
#
#