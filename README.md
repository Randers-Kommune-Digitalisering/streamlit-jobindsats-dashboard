# Steamlit template projekt
Template til nye Python app projekter som skal visualiseres med ```Streamlit```

## Kørsel af Streamlit applikation
Start Applikationen: ```streamlit run main.py```

Bygge docker image: ```docker build -t streamlit .```

Kør container ud fra det image man byggede: ```docker run -p 8080:8080 streamlit```


## Valg af DatabaseClient
* DatbaseClient bruges til at håndtere 3 typer for databaser: ```mssql```, ```mariadb``` og ```postgresql```
* Eksempel på brug af en mssql database til at visualisere charts:
```
from utils.database import DatabaseClient # Uncomment when using database
from utils.config import DB_HOST, DB_USER, DB_PASS, DB_NAME # Uncomment when using database

db_client = DatabaseClient(db_type="mssql" ,database=DB_NAME, username=DB_USER, password=DB_PASS, host=DB_HOST) # Uncomment when using database

pd.set_option('display.max_columns', None)
st.set_page_config(page_title="Streamlit-Template", layout="wide")
st.title("Streamlit-Template")
chart_tab, csv_tab, db_tab = st.tabs(
    ["Template til grafer", "Fra CSV til Charts", "Fra DB til Charts"]
)

with db_tab:
    db_tab_df = pd.read_sql("SELECT * FROM InstalledSoftware", db_client.get_connection())
    db_tab_df['InstallDate'] = pd.to_datetime(db_tab_df['InstallDate'], errors='coerce')
    db_tab_df = db_tab_df[['ComputerName', 'DisplayName', 'DisplayVersion', 'InstallDate', 'Publisher', 'UpdateTimeStamp']]

    selected_computer = st.selectbox("Select a Computer", db_tab_df['ComputerName'].unique(), key="db_tab_computer")
    computer_df = db_tab_df[db_tab_df['ComputerName'] == selected_computer]
    update_time = computer_df.UpdateTimeStamp.mean().round('1s').strftime('%d/%m-%Y %H:%M:%S')

    st.markdown(f'''Installed Software for: :blue-background[{selected_computer}] - :red-background[{update_time}] ''')

    st.markdown(computer_df.drop(columns=['ComputerName', 'UpdateTimeStamp']).to_html(index=False), unsafe_allow_html=True)

```