from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
from data_base import UserInfo,db
import dash




# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"  # Change this to your database URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db.init_app(app)

# Database model


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
                new_user = UserInfo(
                    name=name,
                    email=email,
                    phone=phone,
                    state=state,
                    city=city,
                    address=address,
                    bairro = bairro,
                    numero = numero
                )
                db.session.add(new_user)
                db.session.commit()

                flash("As informações foram salvas com sucesso!", "success")
                return redirect(url_for("simple_form"))
            except Exception as e:
                db.session.rollback()
                flash(f"Erro ao salvar os dados: {e}", "danger")

        else:
            flash("Por favor, preencha todos os campos corretamente.", "warning")
    return render_template("simple_form.html", form=form)

#test










if __name__ == "__main__":
    with app.app_context():  # Open application context
        db.create_all()
    app.run(debug=True)



