import sqlite3
import pandas as pd
import os
from datetime import datetime

def con_data():
    conn = sqlite3.connect('instance/data.db')  # Replace with the correct path to your existing database

    # Step 2: Read the table from the database into a Pandas DataFrame

    date = datetime.now().strftime('%Y-%m-%d')  # This will give the current date in 'YYYY-MM-DD' format

    df = pd.read_sql('SELECT * FROM user_info', conn)

    os.makedirs(f"csvs/{date}", exist_ok=True)
    df.to_csv(f'csvs/{date}/output_file.csv', index=False)

    # Optional: Verify that the DataFrame has been read correctly
    print(df.head())

    # Step 4: Close the connection
    conn.close()
    return df


