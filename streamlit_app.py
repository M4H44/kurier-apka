import streamlit as st
import easyocr
import numpy as np
from PIL import Image

st.set_page_config(page_title="Kuriér Pro", page_icon="🚛")

# --- SLOVNÍK: Kľúčové slovo : (Mesto, Celý názov/Adresa pre Maps) ---
slovnik_cieľov = {
    "solmark": ("považská bystrica", "Solmark, Robotnícka 4351, Považská Bystrica"),
    "hajdu": ("trenčín", "RKS Hajdu, Trenčín"),
    "koval": ("beluša", "Koval Systems, Krížna 950, Beluša"),
    "steelcom": ("dubnica", "Steelcom, Dubnica nad Váhom"),
    "mitice": ("mitice", "Trenčianske Mitice"),
    "nmnv": ("nové mesto", "Nové Mesto nad Váhom"),
    "knm": ("kysucké nové mesto", "Kysucké Nové Mesto"),
    "pb": ("považská bystrica", "Považská Bystrica"),
    "beluša": ("beluša", "Beluša"),
    "dubnica": ("dubnica", "Dubnica nad Váhom"),
    "bytča": ("bytča", "Bytča"),
    "ba": ("bratislava", "Bratislava")
}

@st.cache_resource
def load_reader():
    return easyocr.Reader(['sk', 'cs'], gpu=False)

reader = load_reader()

st.title("🚛 Kuriér Pro: Inteligentný Skener")
st.write("Vodič: **Martin Huťka**")

uploaded_file = st.file_uploader("📂 Nahraj fotku rozpisu", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    img_np = np.array(img)
    
    with st.spinner('Umelá inteligencia číta papier...'):
        vysledok = reader.readtext(img_np, detail=0)
    
    vsetok_text = " ".join(vysledok).lower()
    st.divider()

    najdene_mesta = set()
    finalne_adresy = []

    # 1. NAJPRV hľadáme konkrétne firmy (Koval, Solmark atď.)
    # Zoradíme slovník tak, aby firmy boli prvé (dlhšie/špecifickejšie kľúče)
    for kľúč in sorted(slovnik_cieľov.keys(), key=len, reverse=True):
        mesto, adresa = slovnik_cieľov[kľúč]
        if kľúč in vsetok_text:
            # Ak ešte v tomto meste nemáme zastávku, pridáme ju
            if mesto not in najdene_mesta:
                finalne_adresy.append(adresa)
                najdene_mesta.add(mesto)

    if finalne_adresy:
        st.success(f"📍 Naplánovaná trasa ({len(finalne_adresy)} zastávok)")
        for a in finalne_adresy:
            st.write(f"✅ {a}")
        
        # Google Maps trasa
        trasa = ["Kovex Žilina"] + finalne_adresy
        link = "https://www.google.com/maps/dir/" + "/".join(trasa).replace(" ", "+")
        st.link_button("🚀 OTVORIŤ VYČISTENÚ NAVIGÁCIU", link)
    else:
        st.warning("Nenašiel som žiadne známe ciele.")

    with st.expander("Surové dáta pre kontrolu"):
        st.write(vysledok)
