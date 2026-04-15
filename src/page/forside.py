import streamlit as st

def show_forside():
    st.title("Forside")
    st.markdown("## Velkommen til Randers Kommunes jobindsats-dashboardet")
    st.markdown("Formålet med dashboardet er at give et overblik over jobindsatsen i Randers Kommune og gøre det nemt for medarbejdere, ledere og beslutningstagere at få indsigt i relevante data.")
    st.markdown("Dashboardet er opdelt i flere sektioner, som hver især fokuserer på forskellige aspekter af jobindsatsen. I menuen til venstre kan du navigere mellem de forskellige sektioner og udforske de data og grafer, der er tilgængelige.")
    st.markdown("Data trækkes fra [api.jobindsats.dk](https://api.jobindsats.dk/) og opdateres ugentlig.")
    st.markdown("Data på arbejdsamarkedsområdet fra kommunes KMD Insight-løsning (BI) kan tilgås via [KMD Insight](https://ssolaunchpad.kmd.dk/SSO/Redirect?https://kmd-opus-ledelsesinformation.kmd.dk/BOE/OpenDocument/opendoc/openDocument.jsp?sIDType=CUID&iDocID=AZk._LD5leVIvvXtHie8kM0&sViewer=fiori&kommune=730) " )
    st.markdown("""
        ## Indhold
  
        | Menupunkt         | Beskrivelse
        |---------------------------|-------------------------------------|
        | ***JobRanders***     | Måltal for centre og afdelinger i JobRanders (under udvikling) | 
        | ***Ydelser***          | Udvikling i enkeltydelser over tid (under udvikling) | 
        | ***Fremtidens Randers***    | Diverse grafer i relation til Fremtidens Randers (under udvikling) |
        | ***Datakatalog***                | Katalog over tilgængelige data fra api.jobindsats.dk  | 
        | ***Om***          | Om denne side | 
    """)
