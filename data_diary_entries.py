from flask_sqlalchemy import SQLAlchemy


db_entry = SQLAlchemy()


class DiaryEntry(db_entry .Model):
    id = db_entry .Column(db_entry .Integer, primary_key=True)
    user_id = db_entry .Column(db_entry.Integer, db_entry .ForeignKey('user_info.id'), nullable=False)
    date = db_entry .Column(db_entry .Date, nullable=False)
    text = db_entry .Column(db_entry .Text, nullable=False)
    user = db_entry .relationship('UserInfo', backref=db_entry .backref('diary_entries', lazy=True))



    def __repr__(self):
        return f"<UserInfo {self.name}>"
#