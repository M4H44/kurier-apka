import streamlit as st
import easyocr
import numpy as np
from PIL import Image

st.set_page_config(page_title="Kuriér Scan", page_icon="🚛")

# Spustenie čítačky (Slovenčina + Čeština)
@st.cache_resource
def load_reader():
    return easyocr.Reader(['sk', 'cs'])

reader = load_reader()

st.title("🚛 Inteligentný Rozpis")
st.write("Vodič: **Martin Huťka**")

# --- POLÍČKO PRE VÝBER Z GALÉRIE ---
st.subheader("1. Vyber fotku z pamäte")
foto_galeria = st.file_uploader("Klikni sem a vyber fotku rozpisu", type=["jpg", "jpeg", "png"])

# --- POLÍČKO PRE FOŤÁK ---
st.subheader("2. Alebo odfotografuj")
foto_kamera = st.camera_input("Odfotiť teraz")

# Ktorú fotku ideme spracovať?
finalna_fotka = foto_galeria if foto_galeria else foto_kamera

if finalna_fotka:
    img = Image.open(finalna_fotka)
    img_np = np.array(img)
    
    with st.spinner('Umelá inteligencia číta papier...'):
        # EasyOCR prečíta text
        vysledok = reader.readtext(img_np, detail=0)
    
    st.divider()
    st.subheader("🔍 Našiel som tento text:")
    
    # Spojíme nájdený text do jedného celku
    vsetok_text = " ".join(vysledok)
    st.write(vsetok_text)
    
    # Zoznam miest, ktoré má apka hľadať v texte
    mesta_zoznam = ["Bytča", "Považská", "Hradiště", "Žilina", "Bratislava", "Trenčín", "Nové Mesto", "Uherské"]
    
    najdene_zastavky = []
    for m in mesta_zoznam:
        if m.lower() in vsetok_text.lower():
            najdene_zastavky.append(m)
    
    # Odstránenie duplicít (ak nájde Bytča viackrát)
    najdene_zastavky = list(dict.fromkeys(najdene_zastavky))

    if najdene_zastavky:
        st.success(f"Rozpoznané zastávky: {', '.join(najdene_zastavky)}")
        # Vygenerovanie odkazu pre Google Maps
        # Pridáme Kovex na začiatok
        trasa = ["Kovex Žilina"] + najdene_zastavky
        link = "https://www.google.com/maps/dir/" + "/".join(trasa).replace(" ", "+")
        
        st.link_button("🗺️ OTVORIŤ NAVIGÁCIU", link)
    else:
        st.warning("V texte som nenašiel žiadne známe mestá. Skús vybrať inú fotku.")
