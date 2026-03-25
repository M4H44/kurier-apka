import streamlit as st
import easyocr
import numpy as np
from PIL import Image

st.set_page_config(page_title="Kuriér Scan", page_icon="🚛")

# Inicializácia čítačky (Slovenčina + Čeština)
@st.cache_resource
def load_reader():
    return easyocr.Reader(['sk', 'cs'])

reader = load_reader()

st.title("🚛 Inteligentný Rozpis")
st.write("Vodič: **Martin Huťka**")

foto = st.camera_input("📸 Odfotiť rozpis")

if foto:
    # Prevod fotky na formát, ktorému rozumie AI
    img = Image.open(foto)
    img_np = np.array(img)
    
    with st.spinner('Čítam papier...'):
        vysledok = reader.readtext(img_np, detail=0)
    
    st.subheader("Nájdený text na papieri:")
    
    # Tu filter, ktorý hľadá mestá alebo firmy
    # Pre začiatok ti vypíšeme všetko, čo to našlo
    for riadok in vysledok:
        st.write(f"🔍 {riadok}")
    
    # Tvorba trasy z nájdených slov
    # (Ak program nájde známe mestá, pridá ich do linku)
    mesta = ["Bytča", "Považská", "Hradiště", "Žilina", "Bratislava"]
    najdene_zastavky = [s for s in vysledok if any(m in s for m in mesta)]
    
    if najdene_zastavky:
        trasa = ["Kovex Žilina"] + najdene_zastavky
        link = "https://www.google.com/maps/dir/" + "/".join(trasa).replace(" ", "+")
        st.link_button("🗺️ OTVORIŤ TRASU", link)
