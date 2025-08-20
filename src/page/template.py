import streamlit as st
import streamlit_antd_components as sac
import streamlit_shadcn_ui as ui


def get_template_overview():

    col_1 = st.columns([1])[0]

    with col_1:
        content_tabs = sac.tabs([
            sac.TabsItem('Template Item', tag='Template Item', icon='bi bi-card-list'),
        ], color='dark', size='md', position='top', align='start', use_container_width=True)

    try:

        if content_tabs == 'Template Item':

            col1, col2, col3 = st.columns(3)

            with col1:
                ui.metric_card(title="Template Item 1", description="Template Item 1 beskrivelse")
            with col2:
                ui.metric_card(title="Template Item 2", description="Template Item 2 beskrivelse")
            with col3:
                ui.metric_card(title="Template Item 3", description="Template Item 3 beskrivelse")

    except Exception as e:
        st.error(f'An error occurred: {e}')
