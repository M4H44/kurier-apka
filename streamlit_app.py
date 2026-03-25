import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import difflib

st.set_page_config(page_title="Kuriér Pro", page_icon="🚛")

# 1. TVOJ SLOVNÍK SKRATIEK A FIRIEM (Tu pridávaj ďalšie, ktoré jazdíš)
prekladovy_slovnik = {
    "PB": "Považská Bystrica",
    "KNM": "Kysucké Nové Mesto",
    "NMnV": "Nové Mesto nad Váhom",
    "BA": "Bratislava",
    "Solmark": "Solmark Považská Bystrica",
    "Steelcom": "Steelcom Dubnica nad Váhom",
    "Koval": "Koval Beluša",
    "Teckon": "Teckon Bytča",
    "Mitice": "Trenčianske Mitice",
    "Hradiště": "Uherské Hradiště"
}

# 2. DATABÁZA OBCÍ (Zoznam pre všeobecné hľadanie)
@st.cache_data
def load_all_towns():
    # Sem budeme postupne pridávať všetko, čo potrebuješ
    return ["Žilina", "Bytča", "Beluša", "Dubnica nad Váhom", "Trenčín", "Púchov", "Ilava"]

vsetky_obce = load_all_towns()

@st.cache_resource
def load_reader():
    # gpu=False zaistí, že to na Streamlite nezamrzne
    return easyocr.Reader(['sk', 'cs'], gpu=False)

reader = load_reader()

st.title("🚛 Kuriér Pro: SK/CZ Skener")
st.write("Vodič: **Martin Huťka**")

uploaded_file = st.file_uploader("📂 Nahraj rozpis (z galérie alebo foťáku)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    img_np = np.array(img)
    
    with st.spinner('Umelá inteligencia číta papier...'):
        vysledok = reader.readtext(img_np, detail=0)
    
    vsetok_text = " ".join(vysledok)
    st.divider()

    # --- HLAVNÁ LOGIKA HĽADANIA ---
    najdene_do_mapy = []
    
    # Rozdelíme text na slová a čistíme ich od bodiek a čiarok
    slova_z_papiera = vsetok_text.replace(",", " ").replace(":", " ").replace(".", " ").split()
    
    for slovo in slova_z_papiera:
        # A. Skúsime nájsť slovo v našom slovníku skratiek (napr. "PB")
        if slovo in prekladovy_slovnik:
            najdene_do_mapy.append(prekladovy_slovnik[slovo])
        
        # B. Ak to nie je v slovníku, skúsime nájsť podobnú obec v databáze
        else:
            zhoda = difflib.get_close_matches(slovo, vsetky_obce, n=1, cutoff=0.8)
            if zhoda:
                najdene_do_mapy.append(zhoda[0])
    
    # Odstránenie duplicít
    najdene_do_mapy = list(dict.fromkeys(najdene_do_mapy))

    if najdene_do_mapy:
        st.success(f"📍 Rozpoznané ciele: {', '.join(najdene_do_mapy)}")
        
        # Vygenerovanie Google Maps trasy
        trasa = ["Kovex Žilina"] + najdene_do_mapy
        link = "https://www.google.com/maps/dir/" + "/".join(trasa).replace(" ", "+")
        st.link_button("🚀 OTVORIŤ NAVIGÁCIU", link)
    else:
        st.warning("V texte som nenašiel žiadnu známu firmu ani obec.")

    with st.expander("Surové dáta z papiera (čo vidí AI)"):
        st.write(vysledok)
