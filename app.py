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


#Reg partner form
# ____________________________________________________________________
# ____________________________________________________________________
class parter_reg(FlaskForm):
    nome_do_parceiro = StringField('Nome do Parceiro', validators=[DataRequired()])
    telefone_do_parceiro = StringField('Telefone do Parceiro', validators=[DataRequired()])
    modelo_cursos = StringField('Modelo de Cursos', validators=[DataRequired()])
    cnpj_parceiro = StringField('CNPJ do Parceiro', validators=[DataRequired(),Length(min=14, max=14)])
    year = IntegerField('Ano', validators=[Optional()])
    descrição_da_proposta = StringField('Descrição da proposta', validators=[DataRequired()])
    status = SelectField("Status",
                         choices=[('primeiro contato'), ('Em contato'),
                                  ('Aguardando contato'), ('Concluído'), ('Pendências')],
                         validators=[DataRequired()])

    submit = SubmitField("Registrar Parceiro")

class partner_edit(FlaskForm):
    nome_do_parceiro = StringField('Nome do Parceiro', validators=[DataRequired()])
    telefone_do_parceiro = StringField('Telefone do Parceiro', validators=[DataRequired()])
    modelo_cursos = StringField('Modelo de Cursos', validators=[DataRequired()])
    cnpj_parceiro = StringField('CNPJ do Parceiro', validators=[DataRequired(),Length(min=14, max=14)])
    year = IntegerField('Ano', validators=[Optional()])
    descrição_da_proposta = TextAreaField('Descrição da proposta', validators=[DataRequired()])
    status = SelectField("Status",
                         choices=[('primeiro contato'), ('Em contato'),
                                  ('Aguardando contato'), ('Concluído'), ('Pendências')],
                         validators=[DataRequired()])
    submit = SubmitField("Salvar Alterações")


#Reg client form
# ____________________________________________________________________
# ____________________________________________________________________


class client_reg(FlaskForm):
    client_name = StringField("Nome do cliente", validators=[DataRequired()])
    client_phone = StringField("Telefone")

    cnpj_client = StringField("CNPJ", validators=[DataRequired(), Length(min=14, max=14)])
    year = IntegerField("Ano", validators=[Optional()])
    needs_description = TextAreaField("Necessidades")
    status = SelectField("Status",
                         choices=[('primeiro contato'), ('Em contato'),
                                  ('Aguardando contato'), ('Concluído'), ('Pendências')],
                         validators=[DataRequired()])
    submit = SubmitField("Registrar cliente")


class client_edit(FlaskForm):
    client_name = StringField("Nome do cliente", validators=[DataRequired()])
    client_phone = StringField("Telefone")

    cnpj_client = StringField("CNPJ", validators=[DataRequired(), Length(min=14, max=14)])
    year = IntegerField("Ano", validators=[Optional()])
    needs_description = TextAreaField("Necessidades")
    status = SelectField("Status",
                         choices=[('primeiro contato'), ('Em contato'),
                                  ('Aguardando contato'), ('Concluído'), ('Pendências')],
                         validators=[DataRequired()])


    log_date = DateField('Data do contato', validators=[Optional()])
    log_text = TextAreaField('Descrição do cliente', validators=[Optional()])



    submit = SubmitField("Salvar Alterações")





#Reg part def
# ____________________________________________________________________
# ____________________________________________________________________


@app.route("/", methods=["GET", "POST"])
def register_partner():
    form = parter_reg()



    if form.validate_on_submit():
        new_partner = partners(
            nome_do_parceiro=form.nome_do_parceiro.data,
            telefone_do_parceiro=form.telefone_do_parceiro.data,
            modelo_cursos=form.modelo_cursos.data,
            cnpj_parceiro=form.cnpj_parceiro.data.upper(),
            year=form.year.data,
            descrição_da_proposta=form.descrição_da_proposta.data,
            status=form.status.data
        )
        print("Form errors:", form.errors)
        try:
            db.session.add(new_partner)
            db.session.commit()
            print("Form errors:", form.errors)
            flash("Parceiro registrado com sucesso!", "success")
            return redirect(url_for("register_partner"))

        except IntegrityError:
            print("Form errors:", form.errors)
            db.session.rollback()
            flash(f"Erro: O seguinte CNPJ "
                  f"- '{new_partner.cnpj_parceiro}' já está registrada.", "danger")
        except Exception as e:
            print("Form errors:", form.errors)
            db.session.rollback()
            flash(f"Erro ao salvar o registro: {e}", "danger")


    return render_template("register_partner.html", form=form)



@app.route("/client", methods=["GET", "POST"])
def register_client():
    form = client_reg()

    if form.validate_on_submit():
        new_client = Client(
            nome_do_cliente=form.client_name.data,
            telefone_do_cliente=form.client_name.data,

            cnpj_cliente=form.cnpj_client.data.upper(),
            year=form.year.data,

            status=form.status.data
        )
        print("Form errors:", form.errors)
        try:
            db.session.add(new_client)
            db.session.commit()
            print("Form errors:", form.errors)
            flash("clienr registrado com sucesso!", "success")
            return redirect(url_for("register_client"))

        except IntegrityError:
            print("Form errors:", form.errors)
            db.session.rollback()
            flash(f"Erro: O seguinte CNPJ "
                  f"- '{new_client.cnpj_cliente}' já está registrada.", "danger")
        except Exception as e:
            print("Form errors:", form.errors)
            db.session.rollback()
            flash(f"Erro ao salvar o registro: {e}", "danger")


    return render_template("register_client.html", form=form)




def truncate_words(s, num_words=25):
    words = s.split()
    if len(words) > num_words:
        return " ".join(words[:num_words]) + "..."
    return s

app.jinja_env.filters['truncate_words'] = truncate_words

@app.route('/partners_dash')
def partners_dash():
    search_query = request.args.get('search', '').lower()

    if search_query:
        search_filter = f"%{search_query}%"

        #use a different var for the whoe data query never the same as the databsse name!

        partners_data = partners.query.filter(
            (partners.nome_do_parceiro.ilike(search_filter)) |
            (partners.cnpj_parceiro.ilike(search_filter))
        ).all()
    else:
        partners_data = partners.query.order_by(partners.registration_date.desc()).all()




    data = [{
        'id': partner.id,
        'Nome': partner.nome_do_parceiro,
        'Descrição dos serviços': partner.descrição_da_proposta,
        'Cnpj': partner.cnpj_parceiro,
        'Status':partner.status

    } for partner in partners_data]

    df = pd.DataFrame(data)

    if not df.empty:
        # Make the license plate a link to the edit page
        df['Cnpj'] = df.apply(
            lambda row: f'<a href="/edit/{row["id"]}">{row["Cnpj"]}</a>', axis=1
        )
        df['Descrição dos serviços'] = df['Descrição dos serviços'].apply(truncate_words)
        df = df.drop(columns=['id'])  # Remove the ID column for display

    table_html = df.to_html(classes='table table-striped table-hover text-justify', escape=False, index=False
                           )
    return render_template('partners_dashboard.html',
                           table=table_html, search=search_query,flash = "ass")





@app.route('/clients_dash')
def clients_dash():
    search_query = request.args.get('search', '').lower()

    if search_query:
        search_filter = f"%{search_query}%"

        #use a different var for the whoe data query never the same as the databsse name!

        clients_data = Client.query.filter(
            (clients.nome_do_cliente.ilike(search_filter)) |
            (clients.cnpj_c.ilike(search_filter))
        ).all()
    else:
        clients_data = Client.query.order_by(Client.id).all()


    data = [{
        'id': clients.id,
        'Nome': clients.nome_do_cliente,
        'Cnpj': clients.nome_do_cliente,
        'Status':clients.status

    } for clients in clients_data]

    df = pd.DataFrame(data)

    if not df.empty:
        # Make the license plate a link to the edit page
        df['Cnpj'] = df.apply(
            lambda row: f'<a href="/edit/{row["id"]}">{row["Cnpj"]}</a>', axis=1
        )
        # df['Descrição dos serviços'] = df['Descrição dos serviços'].apply(truncate_words)
        df = df.drop(columns=['id'])  # Remove the ID column for display

    table_html = df.to_html(classes='table table-striped table-hover text-justify', escape=False, index=False
                           )
    return render_template('clients_dashboard.html',
                           table=table_html, search=search_query,flash = "ass")



@app.route("/edit/<int:partner_id>", methods=["GET", "POST"])
def edit_partner(partner_id):

    partners_data = partners.query.get_or_404(partner_id)

    form = partner_edit(obj=partners_data)

    if form.validate_on_submit():
        form.populate_obj(partners_data)


        print(f"DEBUG: Data to be saved: "
              f"Name: {partners_data.nome_do_parceiro}, "
              f"CNPJ: {partners_data.cnpj_parceiro}, "
              f"Status: {partners_data.status}")


        try:
            db.session.commit()
            flash("Dados do parceiro atualizados com sucesso!", "success")
            return redirect(url_for('partners_dash'))
        except IntegrityError:
            db.session.rollback()
            flash(f"Erro: O Cnpj - '{partners_data.cnpj_parceiro}' "
                  f"já pertence a outro registro.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao atualizar os dados: {e}", "danger")
    else:
        print("Form validation failed. Errors:", form.errors)


    return render_template("edit_partner.html", form=form,
                           partner=partners_data)





# Route to delete a car
@app.route("/delete/<int:partner_id>", methods=["POST"])
def delete_partner(partner_id):
    partner = partners.query.get_or_404(partner_id)

    try:

        db.session.delete(partner)
        db.session.commit()
        flash("Registro do carro excluído com suceso!", "success")
        return redirect(url_for("partner_dash"))
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao excluir o registro: {e}", "danger")
        return redirect(url_for("edit_partner",partner_id=partner.id
    ))


# # Route to manage repair log for a specific car
# @app.route("/car/<int:car_id>/log", methods=["GET", "POST"])
# def repair_log(car_id):
#     car = partners.query.get_or_404(car_id)
#
#     if request.method == "POST":
#         log_date_str = request.form.get("log_date")
#         log_text = request.form.get("log_text")
#
#         if not log_date_str or not log_text:
#             flash("Para adicionar uma nova entrada, data e descrição são obrigatórias.", "warning")
#             return redirect(url_for("repair_log", car_id=car_id))
#
#         try:
#             log_date = datetime.strptime(log_date_str, "%Y-%m-%d").date()
#
#             # Check for existing entry on the same date to avoid duplicates
#             existing_entry = RepairLog.query.filter_by(car_id=car_id, date=log_date).first()
#             if existing_entry:
#                 flash("Já existe um registro de reparo para esta data. Por favor, edite o existente.", "danger")
#             else:
#                 new_log = RepairLog(car_id=car_id, date=log_date, text=log_text)
#                 db.session.add(new_log)
#                 db.session.commit()
#                 flash("Novo registro de reparo adicionado com sucesso!", "success")
#
#         except ValueError:
#             flash("Formato de data inválido. Use o seletor de data.", "danger")
#
#         return redirect(url_for("repair_log", car_id=car_id))
#
#     logs = RepairLog.query.filter_by(car_id=car_id).order_by(RepairLog.date.desc()).all()
#     return render_template("repair_log.html", car=car, logs=logs)
#

# # Route to delete a repair log entry
# @app.route("/log/delete/<int:log_id>", methods=["POST"])
# def delete_log_entry(log_id):
#     log_entry = RepairLog.query.get_or_404(log_id)
#     car_id = log_entry.car_id
#     try:
#         db.session.delete(log_entry)
#         db.session.commit()
#         flash("Entrada do histórico de reparo excluída!", "success")
#     except Exception as e:
#         db.session.rollback()
#         flash(f"Erro ao excluir a entrada: {e}", "danger")
#     return redirect(url_for("repair_log", car_id=car_id))
#
#
# # Route to update a repair log entry
# @app.route("/log/update/<int:log_id>", methods=["POST"])
# def update_log_entry(log_id):
#     log_entry = RepairLog.query.get_or_404(log_id)
#     car_id = log_entry.car_id
#
#     updated_text = request.form.get("text")
#     updated_date_str = request.form.get("date")
#
#     if not updated_text:
#         flash("A descrição do reparo não pode ficar vazia.", "warning")
#         return redirect(url_for("repair_log", car_id=car_id))
#
#     log_entry.text = updated_text
#     if updated_date_str:
#         try:
#             log_entry.date = datetime.strptime(updated_date_str, "%Y-%m-%d").date()
#         except ValueError:
#             flash("Formato de data inválido para atualização.", "danger")
#             return redirect(url_for("repair_log", car_id=car_id))
#
#     try:
#         db.session.commit()
#         flash("Entrada do histórico atualizada com sucesso!", "success")
#     except Exception as e:
#         db.session.rollback()
#         flash(f"Erro ao atualizar a entrada: {e}", "danger")
#
#     return redirect(url_for("repair_log", car_id=car_id))
#

if __name__ == "__main__":
    with app.app_context():
        app.config['SQLALCHEMY_ECHO'] = True

        db.create_all()
    app.run(debug=True)