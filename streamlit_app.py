import streamlit as st
import easyocr
import numpy as np
from PIL import Image

st.set_page_config(page_title="Martin Huťka - Presný Rozpis", page_icon="🚛")

# --- TVOJ SLOVNÍK (Kľúč : Adresa) ---
slovnik_firiem = {
    "solmark": "Solmark, Robotnícka 4351, Považská Bystrica",
    "steelcom": "STEELCOM. SK, Továrenská 4203, Dubnica nad Váhom",
    "mitice": "Trenčianske Mitice 913 22",
    "hajdu": "RKS Hajdu, Súvoz 1, Trenčín",
    "koval": "KOVAL SYSTEMS, a. s., Krížna 950/10, Beluša"
}

@st.cache_resource
def load_reader():
    return easyocr.Reader(['sk', 'cs'], gpu=False)

reader = load_reader()

st.title("🚛 Inteligentný stĺpcový skener")

uploaded_file = st.file_uploader("📂 Nahraj rozpis", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    img_np = np.array(img)
    
    with st.spinner('Analyzujem stĺpce a poradie...'):
        # Tu pýtame od AI aj súradnice (detail=1)
        vysledok = reader.readtext(img_np, detail=1)
    
    # 1. NÁJDEME TVOJU POLOHU (Kde na papieri si?)
    x_zaciatok = 0
    x_koniec = 9999
    nasiel_sa_martin = False

    for (bbox, text, prob) in vysledok:
        if "martin" in text.lower() and "hutka" in text.lower().replace("ť", "t"):
            # bbox sú 4 body [vlavo_hore, vpravo_hore, vpravo_dole, vlavo_dole]
            x_zaciatok = bbox[0][0] - 50 # malá rezerva vľavo
            x_koniec = bbox[1][0] + 50   # malá rezerva vpravo
            nasiel_sa_martin = True
            break

    # 2. FILTRUJEME FIRMY, KTORÉ SÚ POD TEBOU A RADÍME ICH PODĽA VÝŠKY (Y)
    moje_detekcie = []
    
    if nasiel_sa_martin:
        for (bbox, text, prob) in vysledok:
            stred_x = (bbox[0][0] + bbox[1][0]) / 2
            vyska_y = bbox[0][1]
            
            # Ak je firma v tvojom stĺpci (medzi x_zaciatok a x_koniec)
            if x_zaciatok <= stred_x <= x_koniec:
                for kluc, adresa in slovnik_firiem.items():
                    if kluc in text.lower():
                        # Uložíme si adresu a jej výšku na papieri (vyska_y)
                        moje_detekcie.append((vyska_y, adresa))

        # ZORADENIE: Podľa výšky na papieri (zhora nadol)
        moje_detekcie.sort() 
        moje_zastavky = [d[1] for d in moje_detekcie]
        # Odstránenie duplicít pri zachovaní poradia
        moje_zastavky = list(dict.fromkeys(moje_zastavky))

        if moje_zastavky:
            st.success(f"📍 Zastávky v stĺpci Martina Huťku:")
            for i, z in enumerate(moje_zastavky, 1):
                st.write(f"{i}. **{z}**")
            
            link = "https://www.google.com/maps/dir/" + "/".join(["KOVEX Žilina"] + moje_zastavky).replace(" ", "+")
            st.link_button("🚀 SPUSTIŤ NAVIGÁCIU (SPRÁVNE PORADIE)", link)
        else:
            st.warning("V tvojom stĺpci som nenašiel žiadne firmy.")
    else:
        st.error("Na papieri som nenašiel meno 'Martin Huťka'. Skús odfotiť celú hornú časť.")

    with st.expander("Surové dáta pre kontrolu"):
        st.write(vysledok)
