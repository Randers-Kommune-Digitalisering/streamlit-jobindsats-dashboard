import streamlit as st
from streamlit_option_menu import option_menu
from utils.logo import get_logo
from page.forside import show_forside
from page.jobindsats_overview import show_jobindsats_metadata_overview
from page.ydelser import get_ydelser_overview
from page.jobranders import get_jobranders
from page.diverse import get_diverse
import streamlit_antd_components as sac

st.set_page_config(page_title="Jobindsats", page_icon="assets/favicon.ico", layout="wide")
selected = None


with st.sidebar:
    st.sidebar.markdown(get_logo(), unsafe_allow_html=True)

    selected = sac.menu([
        sac.MenuItem('Forside', icon='house'),
        sac.MenuItem('JobRanders', icon='buildings', children=[
            sac.MenuItem('Center for Job og Kompetencer', icon='building', children=[
                sac.MenuItem('CJK - fælles mål', icon='bullseye'),
                sac.MenuItem('A-dagpenge og jobformidling', icon='house-door'),
                sac.MenuItem('Jobparate og integration', icon='house-door'),
                sac.MenuItem('Fleksjob', icon='house-door'),
                sac.MenuItem('Sprogcenter', icon='house-door'),
            ]),
            sac.MenuItem('Center for Job og Udvikling', icon='building', children=[
                sac.MenuItem('CJU - fælles mål', icon='bullseye'),
                sac.MenuItem('Sygedagpenge', icon='house-door'),
                sac.MenuItem('Kontanthjælp voksne', icon='house-door')
            ]),
        ]),
        sac.MenuItem('Ydelser', icon='people'),
        sac.MenuItem('Diverse statistikker', icon='graph-down-arrow', children=[
            sac.MenuItem('Årshjulsdokumenter', icon='graph-up-arrow'),
            sac.MenuItem('Arbejdspligt', icon='graph-up-arrow'),
        ]),
        sac.MenuItem('Datakatalog', icon='database'),
    ], color='#00B050', variant='filled', open_all=False)


if selected == "Forside":
    show_forside()
elif selected in ["Center for Job og Kompetencer", "Center for Job og Udvikling", "JobRanders"]:
    get_jobranders(selected)
elif selected == "Ydelser":
    get_ydelser_overview()
elif selected in ["Arbejdspligt", "Årshjulsdokumenter"]:
    get_diverse(selected)
elif selected == "Datakatalog":
    show_jobindsats_metadata_overview()
    