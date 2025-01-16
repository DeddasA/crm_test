from flask import Flask, render_template
import dash
from dash import dash_table
import pandas as pd
from dash import dcc, html
from pandas_editing import con_data

# Initialize Flask app
app_dashboard = Flask(__name__)


def create_dash_app():
    dash_app = dash.Dash(__name__, server=app_dashboard, url_base_pathname='/dashboard/')

    # Call your data processing function
    con_data()

    # Load the CSV data into a Pandas DataFrame
    df = pd.read_csv("csvs/2025-01-16/output_file.csv")

    # Step 2: Create Dash layout
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


# Step 2: Create the Dash app and integrate it with Flask
dash_app = create_dash_app()


# Step 3: Flask route to render the dashboard page (You can add more routes here)
# Flask home page template


@app_dashboard.route("/dashboard")
def dashboard():
    return dash_app.index()  # This will render the dashboard app


# Run the Flask app
if __name__ == '__main__':
    app_dashboard.run(debug=True)
