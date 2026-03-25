import streamlit as st
import easyocr
import numpy as np
from PIL import Image

st.set_page_config(page_title="Martin Huťka - Rozpis", page_icon="🚛")

# --- TVOJ SLOVNÍK (Kľúč : Adresa pre Google Maps) ---
slovnik_firiem = {
    "solmark": "Solmark, Robotnícka 4351, Považská Bystrica",
    "hajdu": "RKS Trenčín s.r.o, Súvoz 1/37, Kubrá, Trenčín",
    "koval": "KOVAL SYSTEMS, a. s., Krížna 950/10, Beluša",
    "steelcom": "STEELCOM. SK, Továrenská 4203, Dubnica nad Váhom",
    "mitice": "Trenčianske Mitice 913 22"
}

@st.cache_resource
def load_reader():
    return easyocr.Reader(['sk', 'cs'], gpu=False)

reader = load_reader()

st.title("🚛 Rozpis pre Martina Huťku")

uploaded_file = st.file_uploader("📂 Nahraj fotku spoločného rozpisu", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    img_np = np.array(img)
    
    with st.spinner('Filtrujem tvoje zastávky...'):
        vysledok = reader.readtext(img_np, detail=0)
    
    # --- LOGIKA: HĽADÁME LEN TVOJU ČASŤ ---
    moje_zastavky = []
    som_v_mojej_sekcii = False
    
    for riadok in vysledok:
        text = riadok.lower()
        
        # Ak narazíme na tvoje meno, začíname pridávať
        if "martin huťka" in text:
            som_v_mojej_sekcii = True
            continue
            
        # Ak narazíme na iné meno, končíme (aby nebralo Bratislavu iným)
        if som_v_mojej_sekcii and any(meno in text for meno in ["michal fusko", "milan svitek", "juraj hriník"]):
            som_v_mojej_sekcii = False
            break
            
        # Ak sme v tvojej sekcii, hľadáme firmy zo slovníka
        if som_v_mojej_sekcii:
            for kluc, adresa in slovnik_firiem.items():
                if kluc in text and adresa not in moje_zastavky:
                    moje_zastavky.append(adresa)

    if moje_zastavky:
        st.success(f"📍 Našiel som {len(moje_zastavky)} tvojich zastávok")
        
        for i, z in enumerate(moje_zastavky, 1):
            st.write(f"{i}. **{z}**")
        
        # Trasa: Štart -> tvoje firmy v poradí ako sú na papieri
        trasa = ["Pracovisko (KOVEX)"] + moje_zastavky
        link = "https://www.google.com/maps/dir/" + "/".join(trasa).replace(" ", "+")
        st.link_button("🚀 OTVORIŤ MOJU NAVIGÁCIU", link)
    else:
        st.warning("Nenašiel som v sekcii 'Martin Huťka' žiadne známe firmy.")

    with st.expander("Kontrola celého papiera"):
        st.write(vysledok)
