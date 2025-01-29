import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import sqlite3
import pandas as pd
from flask import Flask

# Initialize Flask app
app = Flask("DashBoard")





def create_dash_app(flask_app):
    # Attach Dash to the Flask app
    dash_app = dash.Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dashboard/'
    )

    # Function to fetch data from the database
    def fetch_data():
        conn = sqlite3.connect('instance/data.db')
        query = '''
               SELECT *
               FROM user_info
               JOIN diary_entry ON user_info.id
                = diary_entry.id;
               '''


        df = pd.read_sql(query, conn)
        conn.close()
        return df



    # Initial DataFjjrame
    df = fetch_data()


    # Dash layout
    dash_app.layout = html.Div([
        html.H1("Dados dos clientes"),

        # Refresh button
        html.Button("Atualizar Banco de dados", id="refresh-button", n_clicks=0),

        html.Div([
            html.A("Retornar para a página de cadastros", href="/",
                   style={'font-size': '16px', 'color': 'blue', 'text-decoration': 'underline'})
        ], style={'margin-bottom': '20px'}),

        # Data table
        dash_table.DataTable(
            id='table',
            columns=[
                {'name': 'ID', 'id': 'id'},  # Display the 'id' column
                {'name': 'Nome', 'id': 'name'},
                {'name': 'Email', 'id': 'email'},
                {'name': 'Updates', 'id': 'text'},
                {'name': 'Update date', 'id': 'date'}
            ],
            data=df.to_dict('records'),
            style_table={'height': '100px', 'overflowY': 'auto'},
        ),
    ])




    @dash_app.callback(
        Output('table', 'data'),
        Input('refresh-button', 'n_clicks')
    )






    def refresh_table(n_clicks):
        # Fetch the updated data from the database
        updated_df = fetch_data()
        return updated_df.to_dict('records')

    return dash_app


# Attach the Dash app to the Flask app
dash_app = create_dash_app(app)

@app.route("/")
def home():
    return "Navigate to /dashboard to view the dashboard"

if __name__ == "__main__":
    app.run(debug=True)
