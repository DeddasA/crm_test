from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired
import spacy
import re
app = Flask(__name__)
app.secret_key = "your_secret_key"

# Load spaCy's Portuguese language model
nlp = spacy.load("pt_core_news_sm")


# Define the form
class NLPForm(FlaskForm):
    user_input = TextAreaField("Descreva os seus detalhes (por exemplo, 'Marcos Mottas, Rua ferreira mota 647, Rio de janiero, "
                               "mar_motta@example.com, 21979853591')",
                               validators=[DataRequired()])
    submit = SubmitField("Enviar")


@app.route("/", methods=["GET", "POST"])
def nlp_form():
    form = NLPForm()
    if form.validate_on_submit():
        user_input = form.user_input.data
        doc = nlp(user_input)  # Process the text with spaCy

        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'

        address_pattern = r'\b(Rua|Avenida|Travessa|Servidão)\s+[A-Za-zÁáÉéÍíÓóÚúãõ]+\s+[A-Za-zÁáÉéÍíÓóÚú]+\s+\d+\b'

        brazil_states = [
            "Acre", "Alagoas", "Amapá", "Amazonas", "Bahia", "Ceará", "Espírito Santo",
            "Goiás", "Maranhão", "Mato Grosso", "Mato Grosso do Sul", "Minas Gerais",
            "Pará", "Paraíba", "Paraná", "Pernambuco", "Piauí", "Rio de Janeiro",
            "Rio Grande do Norte", "Rio Grande do Sul", "Rondônia", "Roraima", "Santa Catarina",
            "São Paulo", "Sergipe", "Tocantins"
        ]

        # Extract entities
        clients, states, emails, adress = [], [], [],[]
        emails.extend(re.findall(email_pattern,user_input))
        adress.extend(re.findall(address_pattern,user_input))

        for ent in doc.ents:
            if ent.label_ == "PER" and not ent.label_ == "LOC":
                clients.append(ent.text)

            elif ent.label_ == "EMAIL":  # 'LOC' is for locations
                emails.append(ent.text)

            elif ent.label_ == "LOC":
                for state in brazil_states:
                    if state.lower() in ent.text.lower():
                        states.append(state)

            elif ent.label_ == "LOC":
                adress.append(ent.text)

        # Flash the results
        flash(f"Clientes: {', '.join(clients) if clients else 'Nenhum'}", "info")
        flash(f"Endereço: {', '.join(adress) if adress else 'Nenhum'}", "info")
        flash(f"Estados: {', '.join(states) if states else 'Nenhum'}", "info")
        flash(f"Email: {', '.join(emails) if emails else 'Nenhum'}", "info")




        return redirect(url_for("nlp_form"))
    return render_template("home.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)
