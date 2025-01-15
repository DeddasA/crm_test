from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField,BooleanField
from wtforms.validators import DataRequired
import spacy
import re
import pandas as pd
from fuzzywuzzy import process
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError


# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"

# Configure database URI (replace with your desired database)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clients.db'  # Use your preferred database here
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional: Disable modification tracking for performance

# Initialize SQLAlchemy

# Configure the SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional

# Initialize SQLAlchemy
db = SQLAlchemy(app)

class client(db.Model):


    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(255))
    number = db.Column(db.String(20))
    city = db.Column(db.String(100))
    cellphone = db.Column(db.String(20))


df_cities =pd.read_csv("./data_base/municipios.csv",sep=";",encoding='latin-1')
# df_address =pd.read_csv("./data_base/33_RJ.csv",sep=";",encoding='latin-1')
cities = df_cities["MUNICÍPIO - IBGE"]

cities_list = df_cities["MUNICÍPIO - IBGE"].tolist()









# Load spaCy's Portuguese language model
nlp = spacy.load("pt_core_news_sm")


# Define the form
class NLPForm(FlaskForm):
    user_input = TextAreaField(
        "Descreva os seus detalhes (por exemplo, Mariana Souza, Avenida Paulista, 1578, São Paulo, SP, "
        "mar_motta@example.com, 21979853591. Use vírgulas para separar cada informação por favor.)",
        validators=[DataRequired()],
        render_kw={"rows": 10, "cols": 80}  # Adjust rows and cols as needed
    )

    confirm_save = BooleanField("Confirmo que desejo salvar as informações acima.")
    submit = SubmitField("Enviar")






@app.route("/", methods=["GET", "POST"])
def nlp_form():
    form = NLPForm()
    if form.validate_on_submit():
        if not form.confirm_save.data:  # Check if the checkbox is checked
            flash("Por favor confirme a caixa de diálogo abaixo cas queira enviar as informações.", "warning")
            return redirect(url_for("nlp_form"))

        user_input = form.user_input.data
        doc = nlp(user_input)  # Process the text with spaCy



        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        numbers_patterm = r'\b[0,1,2,3,4,5,6,7,8,9]\b'
        brazilian_phone_pattern = r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}'

        address_pattern = r'\b(Rua|Avenida|Travessa|Servidão)\s+[A-Za-zÁáÉéÍíÓóÚúãõ]+\s+[A-Za-zÁáÉéÍíÓóÚú]+\s+\d+\b'

        BRAZILIAN_STATES = {
            "Acre": "AC", "Alagoas": "AL", "Amapá": "AP", "Amazonas": "AM", "Bahia": "BA",
            "Ceará": "CE", "Distrito Federal": "DF", "Espírito Santo": "ES", "Goiás": "GO",
            "Maranhão": "MA", "Mato Grosso": "MT", "Mato Grosso do Sul": "MS", "Minas Gerais": "MG",
            "Pará": "PA", "Paraíba": "PB", "Paraná": "PR", "Pernambuco": "PE", "Piauí": "PI",
            "Rio de Janeiro": "RJ", "Rio Grande do Norte": "RN", "Rio Grande do Sul": "RS",
            "Rondônia": "RO", "Roraima": "RR", "Santa Catarina": "SC", "São Paulo": "SP",
            "Sergipe": "SE", "Tocantins": "TO"
        }

        states_list = [state for state in BRAZILIAN_STATES.keys()]




        # Extract entities
        clients, states, emails, adress,numbers,city,celphone = [], [], [],[],[],[],[]

        emails.extend(re.findall(email_pattern,user_input))
        adress.extend(re.findall(address_pattern, user_input))

        numbers.extend(re.findall(numbers_patterm, user_input))

        celphone.extend(re.findall(brazilian_phone_pattern, user_input))




        best_match = process.extractOne(user_input.lower(), df_cities["MUNICÍPIO - IBGE"].str.lower())


        for ent in doc.ents:

            if ent.label_ == "PER":
                if "@" not in ent.text :
                    clients.append(ent.text)

            elif ent.label_ == "EMAIL":
                emails.append(ent.text)

            if ent.label_ == "LOC" or ent.label_ == "MISC":
                if (ent.text not in numbers and ent.text not in BRAZILIAN_STATES.keys() and
                        ent.text not in BRAZILIAN_STATES.values()
                        and ent.text  not in cities_list):
                    adress.append(ent.text)

            if ent.label_ == "LOC":
                if (ent.text in BRAZILIAN_STATES.values()
                        or ent.text in BRAZILIAN_STATES.keys() and ent.text not in cities_list):
                    states.append(ent.text)

            if ent.label_ == "LOC":
                if (ent.text not in numbers and ent.text not in BRAZILIAN_STATES.values() and not ent.text in
                        BRAZILIAN_STATES.keys() and ent.text in cities_list):

                    city.append(ent.text)

            if ent.label_ == "NUM":
                celphone.append(ent.text)



        numbers = [
            token.text for token in doc
            if token.like_num and not re.match(brazilian_phone_pattern, token.text)]

        # Flash the results
        flash(f"Clientes: {', '.join(clients) 
        if clients else 'Nenhum'}", "info")

        flash(f"Endereço: {','.join(adress)
        if adress else 'Nenhum'}", "info")

        flash(f"Número: {', '.join(numbers) 
        if numbers  else 'Nenhum'}", "info")

        flash(f"Cidade: {', '.join(city)
        if city else 'Nenhum'}", "info")


        flash(f"Estados: {', '.join(states) 
        if states else 'Nenhum'}", 'info')

        flash(f"Email: {', '.join(emails) 
        if emails else 'Nenhum'}", "info")

        flash(f"Telefone: {', '.join(celphone)
        if celphone else 'Nenhum'}", "info")

        for token in doc:
            flash(f"Token: {token.text} | Label: {token.ent_type_ or 'None'}", "info")

        existing_client = client.query.filter_by(email=emails[0]).first()
        if existing_client:
            flash(f"A client with the email {emails[0]} already exists!", "danger")
            return redirect(url_for("nlp_form"))

        # watch out, a single info and not a complete one will give an index error of the list!
        name = clients[0] if clients else ''
        state = states[0] if states else ''
        email = emails[0] if emails else ''
        address = adress[0] if adress else ''
        number = numbers[0] if numbers else ''
        city = city[0] if city else ''
        cellphone = celphone[0] if celphone else ''

        # Save to the database
        new_client = client(
            name=name,
            state=state,
            email=email,
            address=address,
            number=number,
            city=city,
            cellphone=cellphone
        )
        try:
            db.session.add(new_client)
            db.session.commit()
            flash("Client added successfully!", "success")
        except IntegrityError:
            db.session.rollback()
            flash(f"A client with the email {emails[0]}  and name {clients[0]} already exists!", "danger")



        return redirect(url_for("nlp_form"))
    return render_template("home.html", form=form)




with app.app_context():
    db.create_all()



if __name__ == "__main__":

    # Run the app
    app.run(debug=True)
