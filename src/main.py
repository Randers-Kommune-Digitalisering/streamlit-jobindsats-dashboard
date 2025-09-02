import streamlit as st
from streamlit_option_menu import option_menu
from utils.logo import get_logo
from page.sygedagpenge import get_sygedagpenge_overview
from page.jobindsats_overview import show_jobindsats_metadata_overview
from page.fremtidens_randers import get_ydelsesgrupper_overview

st.set_page_config(page_title="Jobindsats Dashboard", page_icon="assets/favicon.ico")

with st.sidebar:
    st.sidebar.markdown(get_logo(), unsafe_allow_html=True)
    selected = option_menu(
        "Jobindsats Dashboard",
        ["Sygedagpenge", "Jobindsats Overblik", "Aktiverede", "Fuldtidspersoner på offentlig forsørgelse", "Fremtidens Randers"],
        default_index=0,
        icons=['bi bi-hospital', 'bi bi-bar-chart-line', 'bi bi-person-check', 'bi bi-people-fill'],
        menu_icon="bi bi-briefcase",
        styles={
            "container": {"padding": "5px", "background-color": "#f0f0f0"},
            "icon": {"color": "#4a4a4a", "font-size": "18px"},
            "nav-link": {"font-size": "18px", "text-align": "left", "margin": "0px", "--hover-color": "#e0e0e0"},
            "nav-link-selected": {"background-color": "#d0d0d0", "color": "#4a4a4a"},
            "menu-title": {"font-size": "20px", "font-weight": "bold", "color": "#4a4a4a", "margin-bottom": "10px"},
        }
    )

if selected == "Sygedagpenge":
    get_sygedagpenge_overview()
elif selected == "Jobindsats Overblik":
    show_jobindsats_metadata_overview()
elif selected == "Fremtidens Randers":
    get_ydelsesgrupper_overview()
