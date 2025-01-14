from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired
import spacy
import re
import pandas as pd
from fuzzywuzzy import process
app = Flask(__name__)
app.secret_key = "your_secret_key"

df_cities =pd.read_csv("./data_base/municipios.csv",sep=";",encoding='latin-1')
# df_address =pd.read_csv("./data_base/33_RJ.csv",sep=";",encoding='latin-1')
cities = df_cities["MUNICÍPIO - IBGE"]

cities_list = df_cities["MUNICÍPIO - IBGE"].tolist()




# df_cities_capitalized  = cities.applymap(lambda x: x.capitalize() if isinstance(x, str) else x)



# enderecos_rj = df_address["NOM_SEGLOGR"]









# Load spaCy's Portuguese language model
nlp = spacy.load("pt_core_news_sm")


# Define the form
class NLPForm(FlaskForm):
    user_input = TextAreaField("Descreva os seus detalhes (por exemplo, Mariana Souza, Avenida Paulista, 1578, São Paulo, SP, "
                               "mar_motta@example.com, 21979853591. Use vírgulas para separar cada informação por favor.)",
                               validators=[DataRequired()])
    submit = SubmitField("Enviar")


@app.route("/", methods=["GET", "POST"])
def nlp_form():
    form = NLPForm()
    if form.validate_on_submit():
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
                clients.append(ent.text)

            elif ent.label_ == "EMAIL":
                emails.append(ent.text)

            if ent.label_ == "LOC" or ent.label_ == "MISC":
                if ent.text not in numbers and ent.text not in BRAZILIAN_STATES.values() and ent.text not in cities_list:
                    adress.append(ent.text)

            if ent.label_ == "LOC" or ent.label_ == "MISC":

                if ent.text not in numbers and ent.text not in BRAZILIAN_STATES.values() and ent.text not in cities_list:
                    states.append(ent.text)

            if ent.label_ == "LOC":
                if ent.text not in numbers and ent.text in BRAZILIAN_STATES.values() or ent.text in BRAZILIAN_STATES.keys() and not ent.text in cities_list:

                    city.append(ent.text)

            if ent.label_ == "NUM":
                celphone.append(ent.text)





        numbers = [token.text for token in doc if token.like_num]

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




        return redirect(url_for("nlp_form"))
    return render_template("home.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)
