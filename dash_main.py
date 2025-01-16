from flask import Flask, render_template
import dash
from dash import dash_table
import pandas as pd
from dash import dcc, html
from pandas_editing import con_data

# Initialize Flask app
app= Flask(__name__)


def create_dash_app(flask_app):
    # Initialize the Dash app and bind it to the Flask app
    dash_app = dash.Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dashboard/'
    )

    # Call your data processing function
    con_data()

    # Load the CSV data into a Pandas DataFrame
    df = pd.read_csv("csvs/2025-01-16/output_file.csv")

    # Create Dash layout
    dash_app.layout = html.Div([
        html.H1("Spreadsheet Data Display"),
        dash_table.DataTable(
            id='table',
            columns=[{'name': col, 'id': col} for col in df.columns],
            data=df.to_dict('records'),
            style_table={'height': '400px', 'overflowY': 'auto'},
        ),
    ])

    return dash_app









dash_app = create_dash_app(app)

if __name__ == '__main__':
    app.run(debug=True)
#001