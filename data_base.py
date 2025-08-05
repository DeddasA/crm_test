from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re
from sqlalchemy.orm import validates
db = SQLAlchemy()


class Client(db.Model):
    __tablename__ = 'clients'

    id = db.Column(db.Integer, primary_key=True)
    nome_do_cliente = db.Column(db.String(100), nullable=False)
    telefone_do_cliente = db.Column(db.String(20),unique = True, nullable=True)
    cnpj_cliente = db.Column(db.String(14), unique=True, nullable=False)


    def __repr__(self):
        return f'<Client {self.nome_do_cliente}>'




class partners(db.Model):

    __tablename__ = 'partners'
    id = db.Column(db.Integer, primary_key=True)

    nome_do_parceiro = db.Column(db.String(100), nullable=False)
    telefone_do_parceiro = db.Column(db.String(20), nullable=True)
    modelo_cursos = db.Column(db.String(50), nullable=False)
    cnpj_parceiro = db.Column(db.String(14), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=True)
    descrição_curso = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False, default='Aguardando Avaliação')  # Status interno da oficina
    registration_date = db.Column(db.Date, default=datetime.utcnow)

    @validates('cnpj')
    def validate_cnpj(self, key, value):
        pattern = r'^[0-9./-]+$'
        if not re.match(pattern, value):
            raise ValueError("CNPJ can only contain numbers and characters: '.', '/', '-'")
        return value

    # Relationship to RepairLog
    repair_logs = db.relationship('RepairLog',
                                  backref='partners', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Car {self.license_plate}>'

class RepairLog(db.Model):
    __tablename__ = 'repair_logs'

    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('partners.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<RepairLog {self.id} for partner {self.partners}>'