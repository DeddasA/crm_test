from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,TextAreaField,SelectField,DateField,FieldList
from wtforms.validators import DataRequired, Email,Regexp
from data_base import UserInfo,DiaryEntry, db
from datetime import datetime
# from dash_main import create_dash_app
from sqlalchemy.exc import IntegrityError


app = Flask(__name__)
# create_dash_app(app)
app.secret_key = "your_secret_key"

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db.init_app(app)


# Form for user input
class SimpleForm(FlaskForm):
    name = StringField("Nome", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Telefone")
    state = StringField("Estado")
    city = StringField("Cidade")
    address = StringField("Endereço")
    bairro = StringField("Bairro")
    numero = StringField("numero")
    status = SelectField("Status", choices=[(""),("Iniciado"), ('Conluído'), ('Em andamento'),
                                           ('Pendente'), ("Nã iniciado")],
                        validators=[DataRequired()])









    submit = SubmitField("Enviar")

# Route for the form
@app.route("/", methods=["GET", "POST"])
def simple_form():
    form = SimpleForm()
    if request.method == "POST":
        if form.validate_on_submit():
            # Gather form data
            name = form.name.data
            email = form.email.data
            phone = form.phone.data
            state = form.state.data
            city = form.city.data
            address = form.address.data
            bairro = form.bairro.data
            numero = form.numero.data
            status = form.status.data
            # reg_date = form.reg_date.data

            existing_user = UserInfo.query.filter_by(email=email).first()
            if existing_user:
                flash(f"Email '{email}' já está em uso.", "danger")
                return render_template("simple_form.html", form=form)
            #Little fukcer! The keywords have to be in the fuking db.model! Fuck!
            new_user = UserInfo(
                name=name,
                email=email,
                phone=phone,
                state=state,
                city=city,
                address=address,
                bairro=bairro,
                numero=numero,
                status=status,
                # date=reg_date

            )


            try:
                db.session.add(new_user)
                db.session.commit()
                flash("Usuário salvo com sucesso!", "success")
                return redirect(url_for("simple_form"))
            except IntegrityError:
                db.session.rollback()
                flash("Erro: já existe um registro com este email.", "danger")
            except Exception as e:
                db.session.rollback()
                flash(f"Erro ao salvar o usuário: {e}", "danger")
        return render_template("simple_form.html", form=form)

    return render_template("simple_form.html", form=form)



@app.route("/search", methods=["GET", "POST"])
def search_user():
    if request.method == "POST":
        email = request.form.get("email")
        user = UserInfo.query.filter_by(email=email).first()
        if user:
            return redirect(url_for("edit_user", user_id=user.id))
        else:
            flash("Usuário não encontrado", "warning")
    return render_template("search.html")


class EditUserForm(FlaskForm):
    name = StringField("Nome:", validators=[DataRequired()])
    email = StringField("Email:", validators=[DataRequired(), Email()])
    phone = StringField("Telefone:")
    state = StringField("Estado:")
    city = StringField("Cidade:")
    address = StringField("Endereço:")
    bairro = StringField("Bairro:")
    numero = StringField("Número:")
    status = SelectField("Status", choices=[(""), ('Conluído'), ('Em andamento'),
                                            ('Pendente'), ("Nã iniciado")],
                         validators=[DataRequired()])

    reg_date = DateField('Data')

    diary_dates = FieldList(DateField('Data do Diário'), min_entries=1)
    diary_texts = FieldList(TextAreaField('Texto do Diário'), min_entries=1)
    user_id = StringField("Id")



    submit = SubmitField("Salvar Alterações")


@app.route("/edit/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    user = UserInfo.query.get_or_404(user_id)

    form = EditUserForm(obj=user)


    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.phone = form.phone.data
        user.state = form.state.data
        user.city = form.city.data
        user.address = form.address.data
        user.bairro = form.bairro.data
        user.numero = form.numero.data
        user.status = form.status.data


        try:

            db.session.commit()
            flash("Dados Atualizados!", "sucesso")
            return redirect(url_for("search_user"))
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao atualizar os dados: {e}", "perigo")
    return render_template("user_editing.html", form=form, user=user)


#_______Delete user____________________________________________________________________
#___________________________________________________________________________
#___________________________________________________________________________

@app.route("/delete/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    print(f"Deleting user with ID: {user_id}")
    user = UserInfo.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        print(f"User deleted: {user.name}")
        db.session.commit()
        flash("Usuário excluído com sucesso!", "success")
        return redirect(url_for("simple_form"))
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao excluir o usuário: Existe entradas no diaário", "Perigo")
        return redirect(url_for("diary_entries",user_id = user.id))


#_____________Diary entries______________________________________________________________
#___________________________________________________________________________
#___________________________________________________________________________

@app.route("/diary/<int:user_id>", methods=["GET", "POST"])
def diary_entries(user_id):

    user = UserInfo.query.get_or_404(user_id)
    form = EditUserForm(obj=user)

    if request.method == "POST":

        date = form.reg_date.data

        text = request.form.get("text")

        if not text:
            flash("Both date and text fields are required.", "danger")

            return redirect(url_for("diary_entries", user_id=user_id))

        try:

            existing_entry = DiaryEntry.query.filter_by(user_id=user_id, date=date).first()
            if existing_entry:
                flash("Há uma entrada com essa data. Caso queira continuar"
                      "atualize-a.", "danger")

                return redirect(url_for("diary_entries", user_id=user_id))

            # Add a new diary entry
            new_entry = DiaryEntry(user_id=user_id, date=date, text=text)
            db.session.add(new_entry)
            db.session.commit()
            flash("Entrada Adicionada!", "success")

        except ValueError:
            flash("Formato de data inválida. Use DD/MM/YYYY.", "danger")

    # Fetch all diary entries for this user
    diary_entries = DiaryEntry.query.filter_by(user_id=user_id).order_by(DiaryEntry.date.desc()).all()

    return render_template("diary_entries.html",
                           user=user, diary_entries=diary_entries,
                           user_id=user.id,form=form)


#____________________Delete Entries_______________________________________________________
#___________________________________________________________________________
#___________________________________________________________________________

@app.route("/diary/delete/<int:entry_id>", methods=["POST"])
def delete_diary_entry(entry_id):
    entry = DiaryEntry.query.get_or_404(entry_id)

    user_id = entry.user_id

    try:
        db.session.delete(entry)
        db.session.commit()
        flash("Diary entry deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting diary entry: {e}", "danger")

    return redirect(url_for("diary_entries", user_id=user_id))

#___________________________________________________________________________
#___________________________________________________________________________
#___________________________________________________________________________

class EditDiaryEntryForm(FlaskForm):
    text = StringField('Text', validators=[DataRequired()])

    submit = SubmitField('Update Entry')


#____________________Update Entries_______________________________________________________
#___________________________________________________________________________
#___________________________________________________________________________
@app.route("/diary/update/<int:entry_id>", methods=["GET", "POST"])
def update_diary_entry(entry_id):
    entry = DiaryEntry.query.get_or_404(entry_id)
    user_id = entry.user_id

    if request.method == "POST":

        updated_text = request.form.get("text")
        updated_date = request.form.get("date")
        # Get new text from form


        if updated_text or updated_date:
            if updated_text:
                entry.text = updated_text

            if updated_date:  # Only update if date is provided
                try:
                    entry.date = datetime.strptime(updated_date, "%d-%m-%Y").date()
                except ValueError:
                    flash("Formato de data inválido! Use DD-MM-YYYY.", "danger")
                    return redirect(url_for("update_diary_entry", entry_id=entry_id))





            try:
                db.session.commit()  # Commit the change to the database
                flash("Entrada atualizada com sucesso!", "success")
                return redirect(url_for("diary_entries", user_id=user_id))
            except Exception as e:
                db.session.rollback()  # Rollback in case of error
                flash(f"Erro em atualizar a entrada!: {e}", "danger")
        else:
            flash("Por favor não deixe o a caixa de texto vazia!", "danger")

    return redirect(url_for("diary_entries", user_id=user_id))



if __name__ == "__main__":
    with app.app_context():  # Open application context
        db.create_all()
    app.run(debug=True)