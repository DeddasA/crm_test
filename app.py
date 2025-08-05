from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, TextAreaField,
                     SelectField, DateField, IntegerField)
from wtforms.validators import DataRequired, Length, Optional,Regexp
from data_base import partners, RepairLog, db,Client
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import pandas as pd

app = Flask(__name__)
app.secret_key = "srets3dokillaz@"

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///learnconnect.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db.init_app(app)


# Form for car registration add email
class parter_reg(FlaskForm):
    owner_name = StringField("Nome do parceiro", validators=[DataRequired()])
    owner_phone = StringField("Telefone")
    car_model = StringField("Modelo de cursos oferecidos", validators=[DataRequired(),
            Regexp(r'^\d+$', message="Only numbers are allowed.")])
#check this up to only acepot numbers its not gestering anything

    license_plate = StringField("CNPJ", validators=[DataRequired(), Length(min=14, max=14)])
    year = IntegerField("Ano", validators=[Optional()])
    problem_description = TextAreaField("Soluções propostas")
    status = SelectField("Status",
                         choices=[('primeiro contato'), ('Em contato'),
                                  ('Aguardando contato'), ('Concluído'), ('Pendências')],
                         validators=[DataRequired()])
    submit = SubmitField("Registrar Parceiro")



# Form for editing car and managing repair logs add email
class partner_edit(FlaskForm):
    owner_name = StringField("Nome do cliante", validators=[DataRequired()])
    owner_phone = StringField("Telefone")
    car_model = StringField("Modelo de cursos oferecidos", validators=[DataRequired()])
    license_plate = StringField("cnpj", validators=[DataRequired(), Length(min=7, max=8)])
    year = IntegerField("Ano", validators=[Optional()])
    problem_description = TextAreaField("Descrição do curso")
    status = SelectField("Status",
                         choices=[('primeiro contato'), ('Em contato'),
                                  ('Aguardando contato'), ('Concluído'), ('Pendências')],
                         validators=[DataRequired()])
    # Fields for adding a new repair log entry
    log_date = DateField('Data do contato', validators=[Optional()])
    log_text = TextAreaField('Descrição do curso', validators=[Optional()])
    submit = SubmitField("Salvar Alterações")





# Troca descrição do curso por descrição da solução proposta






#Add customer form
#Edit customer form



class client_reg(FlaskForm):
    client_name = StringField("Nome do cliente", validators=[DataRequired()])
    client_phone = StringField("Telefone")

    Cnpj = StringField("CNPJ", validators=[DataRequired(), Length(min=7, max=8)])
    year = IntegerField("Ano", validators=[Optional()])
    needs_description = TextAreaField("Necessidades")
    status = SelectField("Status",
                         choices=[('primeiro contato'), ('Em contato'),
                                  ('Aguardando contato'), ('Concluído'), ('Pendências')],
                         validators=[DataRequired()])
    submit = SubmitField("cliente")



# Form for editing car and managing repair logs add email
class client_edit(FlaskForm):
    owner_name = StringField("Nome do cliante", validators=[DataRequired()])
    owner_phone = StringField("Telefone")
    car_model = StringField("Modelo de cursos oferecidos", validators=[DataRequired()])
    license_plate = StringField("cnpj", validators=[DataRequired(), Length(min=7, max=8)])
    year = IntegerField("Ano", validators=[Optional()])
    problem_description = TextAreaField("Descrição do curso")
    status = SelectField("Status",
                         choices=[('primeiro contato'), ('Em contato'),
                                  ('Aguardando contato'), ('Concluído'), ('Pendências')],
                         validators=[DataRequired()])
    # Fields for adding a new repair log entry
    log_date = DateField('Data do contato', validators=[Optional()])
    log_text = TextAreaField('Descrição do curso', validators=[Optional()])



    submit = SubmitField("Salvar Alterações")





























# Route for the main registration form
@app.route("/", methods=["GET", "POST"])
def register_car():
    form = parter_reg()
    if form.validate_on_submit():
        new_partner = partners(
            nome_do_parceiro=form.owner_name.data,
            telefone_do_parceiro=form.owner_phone.data,
            modelo_cursos=form.car_model.data,
            cnpj_parceiro=form.license_plate.data.upper(),
            year=form.year.data,
            descrição_curso=form.problem_description.data,
            status=form.status.data
        )
        try:
            db.session.add( new_partner )
            db.session.commit()
            flash("Parceiro registrado com sucesso!", "success")
            return redirect(url_for("register_car"))
        except IntegrityError:
            db.session.rollback()
            flash(f"Erro: O seguinte CNPJ - '{new_partner.cnpj_parceiro}' já está registrada.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao salvar o registro: {e}", "danger")
    return render_template("register_car.html", form=form)


# Route to display all cars in a searchable table
@app.route('/dashboard')
def car_dashboard():
    search_query = request.args.get('search', '').lower()

    if search_query:
        # Search by owner name or license plate
        search_filter = f"%{search_query}%"
        cars = partners.query.filter(
            (partners.owner_name.ilike(search_filter)) |
            (partners.license_plate.ilike(search_filter))
        ).all()
    else:
        cars = partners.query.order_by(partners.registration_date.desc()).all()


    data = [{
        'id': car.id,
        'Proprietário': car.owner_name,
        'Modelo': car.car_model,
        'Placa': car.license_plate,
        'Status': car.status,
        'Data de Registro': car.registration_date.strftime('%d/%m/%Y')
    } for car in cars]

    df = pd.DataFrame(data)

    if not df.empty:
        # Make the license plate a link to the edit page
        df['Placa'] = df.apply(
            lambda row: f'<a href="/edit/{row["id"]}">{row["Placa"]}</a>', axis=1
        )
        df = df.drop(columns=['id'])  # Remove the ID column for display

    table_html = df.to_html(classes='table table-striped table-hover', escape=False, index=False)

    return render_template('car_dashboard.html', table=table_html, search=search_query)


# Route to edit car information
@app.route("/edit/<int:car_id>", methods=["GET", "POST"])
def edit_car(car_id):
    car = partners.query.get_or_404(car_id)
    form = partner_edit(obj=car)

    if form.validate_on_submit():
        # Update car data from form
        car.owner_name = form.owner_name.data
        car.owner_phone = form.owner_phone.data
        car.car_model = form.car_model.data
        car.license_plate = form.license_plate.data.upper()
        car.year = form.year.data
        car.problem_description = form.problem_description.data
        car.status = form.status.data

        try:
            db.session.commit()
            flash("Dados do carro atualizados com sucesso!", "success")
            return redirect(url_for('car_dashboard'))
        except IntegrityError:
            db.session.rollback()
            flash(f"Erro: A placa '{car.license_plate}' já pertence a outro registro.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao atualizar os dados: {e}", "danger")

    return render_template("edit_car.html", form=form, car=car)


# Route to delete a car
@app.route("/delete/<int:car_id>", methods=["POST"])
def delete_car(car_id):
    car = partners.query.get_or_404(car_id)
    try:
        # The 'cascade' option in the relationship will automatically delete associated repair logs
        db.session.delete(car)
        db.session.commit()
        flash("Registro do carro excluído com sucesso!", "success")
        return redirect(url_for("car_dashboard"))
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao excluir o registro: {e}", "danger")
        return redirect(url_for("edit_car", car_id=car.id))


# Route to manage repair log for a specific car
@app.route("/car/<int:car_id>/log", methods=["GET", "POST"])
def repair_log(car_id):
    car = partners.query.get_or_404(car_id)

    if request.method == "POST":
        log_date_str = request.form.get("log_date")
        log_text = request.form.get("log_text")

        if not log_date_str or not log_text:
            flash("Para adicionar uma nova entrada, data e descrição são obrigatórias.", "warning")
            return redirect(url_for("repair_log", car_id=car_id))

        try:
            log_date = datetime.strptime(log_date_str, "%Y-%m-%d").date()

            # Check for existing entry on the same date to avoid duplicates
            existing_entry = RepairLog.query.filter_by(car_id=car_id, date=log_date).first()
            if existing_entry:
                flash("Já existe um registro de reparo para esta data. Por favor, edite o existente.", "danger")
            else:
                new_log = RepairLog(car_id=car_id, date=log_date, text=log_text)
                db.session.add(new_log)
                db.session.commit()
                flash("Novo registro de reparo adicionado com sucesso!", "success")

        except ValueError:
            flash("Formato de data inválido. Use o seletor de data.", "danger")

        return redirect(url_for("repair_log", car_id=car_id))

    logs = RepairLog.query.filter_by(car_id=car_id).order_by(RepairLog.date.desc()).all()
    return render_template("repair_log.html", car=car, logs=logs)


# Route to delete a repair log entry
@app.route("/log/delete/<int:log_id>", methods=["POST"])
def delete_log_entry(log_id):
    log_entry = RepairLog.query.get_or_404(log_id)
    car_id = log_entry.car_id
    try:
        db.session.delete(log_entry)
        db.session.commit()
        flash("Entrada do histórico de reparo excluída!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao excluir a entrada: {e}", "danger")
    return redirect(url_for("repair_log", car_id=car_id))


# Route to update a repair log entry
@app.route("/log/update/<int:log_id>", methods=["POST"])
def update_log_entry(log_id):
    log_entry = RepairLog.query.get_or_404(log_id)
    car_id = log_entry.car_id

    updated_text = request.form.get("text")
    updated_date_str = request.form.get("date")

    if not updated_text:
        flash("A descrição do reparo não pode ficar vazia.", "warning")
        return redirect(url_for("repair_log", car_id=car_id))

    log_entry.text = updated_text
    if updated_date_str:
        try:
            log_entry.date = datetime.strptime(updated_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Formato de data inválido para atualização.", "danger")
            return redirect(url_for("repair_log", car_id=car_id))

    try:
        db.session.commit()
        flash("Entrada do histórico atualizada com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao atualizar a entrada: {e}", "danger")

    return redirect(url_for("repair_log", car_id=car_id))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)