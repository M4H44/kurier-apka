import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import difflib

st.set_page_config(page_title="Kuriér Pro", page_icon="🚛")

# 1. DATABÁZA OBCÍ (Sem môžeme neskôr nahrať kompletný súbor všetkých obcí SK/CZ)
@st.cache_data
def load_all_towns():
    # Tu by bol v realite list s 9000 názvami
    # Pre test pridávam tie z tvojho papiera + okolie
    return ["Žilina", "Bytča", "Považská Bystrica", "Beluša", "Trenčianske Mitice", 
            "Dubnica nad Váhom", "Uherské Hradiště", "Kysucké Nové Mesto", "Bratislava",
            "Trenčín", "Nové Mesto nad Váhom", "Púchov", "Ilava", "Liptovský Mikuláš"]

vsetky_obce = load_all_towns()

@st.cache_resource
def load_reader():
    return easyocr.Reader(['sk', 'cs'])

reader = load_reader()

st.title("🚛 Kuriér Pro: SK/CZ Skener")
st.write("Vodič: **Martin Huťka**")

uploaded_file = st.file_uploader("📂 Nahraj rozpis (SK/CZ)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    img_np = np.array(img)
    
    with st.spinner('Prehľadávam databázu obcí...'):
        vysledok = reader.readtext(img_np, detail=0)
    
    vsetok_text = " ".join(vysledok)
    
    # HĽADANIE OBCÍ V TEXTE
    najdene_ciele = []
    slova_z_papiera = vsetok_text.split()
    
    for slovo in slova_z_papiera:
        # Hľadáme zhodu v databáze obcí (aspoň na 80%)
        zhoda = difflib.get_close_matches(slovo, vsetky_obce, n=1, cutoff=0.8)
        if zhoda:
            najdene_ciele.append(zhoda[0])
    
    # Odstránenie duplicít
    najdene_ciele = list(dict.fromkeys(najdene_ciele))

    if najdene_ciele:
        st.success(f"📍 Nájdené obce v databáze: {', '.join(najdene_ciele)}")
        
        trasa = ["Kovex Žilina"] + najdene_ciele
        link = "https://www.google.com/maps/dir/" + "/".join(trasa).replace(" ", "+")
        st.link_button("🚀 SPUSTIŤ NAVIGÁCIU", link)
    else:
        st.warning("V texte som nenašiel žiadnu obec z databázy.")

    with st.expander("Surové dáta z papiera"):
        st.write(vsetok_text)
