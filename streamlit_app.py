import streamlit as st
import easyocr
import numpy as np
from PIL import Image

st.set_page_config(page_title="Martin Huťka - Rozpis", page_icon="🚛")

# --- TVOJ SLOVNÍK FIRIEM (Presné adresy) ---
slovnik_firiem = {
    "solmark": "Solmark, Robotnícka 4351, Považská Bystrica",
    "steelcom": "STEELCOM. SK, Továrenská 4203, Dubnica nad Váhom",
    "mitice": "Trenčianske Mitice 913 22",
    "hajdu": "RKS Hajdu, Súvoz 1, Trenčín", # Toto je to RKS v Trenčíne
    "koval": "KOVAL SYSTEMS, a. s., Krížna 950/10, Beluša"
}

# --- ČIERNA LISTINA (Mestá, ktoré nechceš, lebo ich jazdia iní) ---
cudzie_mesta = ["bratislava", "kysucké", "knm", "nmnv", "nové mesto"]

@st.cache_resource
def load_reader():
    return easyocr.Reader(['sk', 'cs'], gpu=False)

reader = load_reader()

st.title("🚛 Rozpis: Martin Huťka")

uploaded_file = st.file_uploader("📂 Nahraj rozpis", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    img_np = np.array(img)
    
    with st.spinner('Hľadám tvoje firmy (vrátane RKS)...'):
        vysledok = reader.readtext(img_np, detail=0)
    
    vsetok_text = " ".join(vysledok).lower()
    
    moje_zastavky = []

    # LOGIKA: Prejdi slovník a pridaj firmu, ak je na papieri
    for kluc, adresa in slovnik_firiem.items():
        if kluc in vsetok_text:
            # Kontrola: Pridaj to len ak to nie je v sekcii iných miest (voliteľné)
            moje_zastavky.append(adresa)

    # Odstránenie duplicít
    moje_zastavky = list(dict.fromkeys(moje_zastavky))

    if moje_zastavky:
        st.success(f"📍 Našiel som {len(moje_zastavky)} zastávok")
        for i, z in enumerate(moje_zastavky, 1):
            st.write(f"{i}. **{z}**")
        
        # Google Maps link
        trasa = ["KOVEX Žilina"] + moje_zastavky
        link = "https://www.google.com/maps/dir/" + "/".join(trasa).replace(" ", "+")
        st.link_button("🚀 SPUSTIŤ NAVIGÁCIU (S RKS TRENČÍN)", link)
    else:
        st.warning("Nenašiel som žiadne tvoje firmy. Skús odfotiť papier zblízka.")

    with st.expander("Čo presne prečítala AI"):
        st.write(vysledok)
