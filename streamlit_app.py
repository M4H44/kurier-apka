import streamlit as st
import easyocr
import numpy as np
from PIL import Image

st.set_page_config(page_title="Martin Huťka - Rozpis", page_icon="🚛")

# --- SLOVNÍK FIRIEM (Iba tie, ktoré naozaj jazdíš) ---
slovnik_firiem = {
    "solmark": "Solmark, Robotnícka 4351, Považská Bystrica",
    "steelcom": "STEELCOM. SK, Továrenská 4203, Dubnica nad Váhom",
    "mitice": "Trenčianske Mitice 913 22",
    "koval": "KOVAL SYSTEMS, a. s., Krížna 950/10, Beluša",
    # Sem môžeš dopísať ďalšie SVOJE firmy, ak sa objavia na papieri
}

@st.cache_resource
def load_reader():
    return easyocr.Reader(['sk', 'cs'], gpu=False)

reader = load_reader()

st.title("🚛 Rozpis: Martin Huťka")

uploaded_file = st.file_uploader("📂 Nahraj rozpis", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    img_np = np.array(img)
    
    with st.spinner('Filtrujem tvoj rozpis...'):
        vysledok = reader.readtext(img_np, detail=0)
    
    moje_zastavky = []
    som_v_sekcii_martin = False
    
    # Zoznam mien, ktoré ukončujú tvoju sekciu
    ostatni_vodici = ["michal fusko", "milan svitek", "juraj hriník", "fusko", "svitek", "hrinik"]

    for riadok in vysledok:
        text = riadok.lower()
        
        # Zapni čítanie len pre Martina
        if "martin huťka" in text or "hutka" in text:
            som_v_sekcii_martin = True
            continue
            
        # Vypni čítanie, ak príde iné meno (aby nebralo cudzí Trenčín/Belušu)
        if som_v_sekcii_martin and any(meno in text for meno in ostatni_vodici):
            som_v_sekcii_martin = False
            break
            
        # Ak sme v správnej sekcii, hľadaj firmy
        if som_v_sekcii_martin:
            for kluc, adresa in slovnik_firiem.items():
                if kluc in text and adresa not in moje_zastavky:
                    moje_zastavky.append(adresa)

    if moje_zastavky:
        st.success(f"📍 Našiel som {len(moje_zastavky)} zastávky pre Martina Huťku")
        for i, z in enumerate(moje_zastavky, 1):
            st.write(f"{i}. **{z}**")
        
        link = "https://www.google.com/maps/dir/" + "/".join(["KOVEX Žilina"] + moje_zastavky).replace(" ", "+")
        st.link_button("🚀 SPUSTIŤ MOJU NAVIGÁCIU", link)
    else:
        st.warning("Nenašiel som pod tvojím menom žiadne známe firmy.")

    with st.expander("Kontrola celého textu (Surové dáta)"):
        st.write(vysledok)
