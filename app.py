from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,TextAreaField,SelectField,DateField
from wtforms.validators import DataRequired, Email,Regexp
from data_base import UserInfo, db
from datetime import datetime
# from dash_main import create_dash_app
from sqlalchemy.exc import IntegrityError


app = Flask(__name__)
# create_dash_app(app)
app.secret_key = "your_secret_key"

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"  # Change this to your database URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db.init_app(app)

# Form for user input
class SimpleForm(FlaskForm):
    name = StringField("Nome", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Telefone", validators=[DataRequired()])
    state = StringField("Estado", validators=[DataRequired()])
    city = StringField("Cidade", validators=[DataRequired()])
    address = StringField("Endereço", validators=[DataRequired()])
    bairro = StringField("Bairro", validators=[DataRequired()])
    numero = StringField("numero", validators=[DataRequired()])
    status = SelectField("Status", choices=[(""), ('Conluído'), ('Em andamento'),
                                           ('Pendente'), ("Nã iniciado")],
                        validators=[DataRequired()])

    reg_date = DateField('Data',validators=[DataRequired()])





    email_body = TextAreaField("Corpo do Email")

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
            email_body = form.email_body.data
            reg_date = form.reg_date.data

            existing_user = UserInfo.query.filter_by(email=email).first()
            if existing_user:
                flash(f"Email '{email}' já está em uso.", "danger")
                return render_template("simple_form.html", form=form)

            new_user = UserInfo(
                name=name,
                email=email,
                phone=phone,
                state=state,
                city=city,
                address=address,
                bairro=bairro,
                numero=numero,
                email_body=email_body,
                status=status,
                reg_date=reg_date

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

    reg_date = StringField('Data')


    email_body = TextAreaField("Corpo do Email")

    submit = SubmitField("Salvar Alterações")

@app.route("/edit/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    user = UserInfo.query.get_or_404(user_id)
    form = EditUserForm(obj=user)  # Pre-fill form with user's current data
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
        user.email_body = form.email_body.data
        # user.reg_date = form.reg_date.data


        try:
            db.session.commit()
            flash("User details updated successfully!", "success")
            return redirect(url_for("search_user"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating user: {e}", "danger")
    return render_template("user_editing.html", form=form, user=user)


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
        flash(f"Erro ao excluir o usuário: {e}", "danger")
        return redirect(url_for("simple_form"))







if __name__ == "__main__":
    with app.app_context():  # Open application context
        db.create_all()
    app.run(debug=True)