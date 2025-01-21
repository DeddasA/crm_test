from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
from data_base import UserInfo, db

from dash_main import create_dash_app

app = Flask(__name__)

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

            try:

                existing_user = UserInfo.query.filter_by(name=name).first()
                if existing_user:
                    flash(f"O Nome '{name}' já existe no banco de dados.", "Aviso")
                    flash(f"O  Email '{email}' já existe no banco de dados.", "Aviso")
                    return redirect(url_for("simple_form"))
                new_user = UserInfo(
                    name=name,
                    email=email,
                    phone=phone,
                    state=state,
                    city=city,
                    address=address,
                    bairro=bairro,
                    numero=numero
                )
                db.session.add(new_user)
                db.session.commit()
#aaaaaa
                flash("As informações foram salvas com sucesso!", "Successo")
                return redirect(url_for("simple_form"))
            except Exception as e:
                db.session.rollback()
                flash(f"Erro ao salvar os dados: {e}", "Erro")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Erro no campo '{getattr(form, field).label.text}': {error}", "Aviso")

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





create_dash_app(app)

if __name__ == "__main__":
    with app.app_context():  # Open application context
        db.create_all()
    app.run(debug=True)
