import streamlit as st
import PIL.Image

st.set_page_config(page_title="Kuriérsky Pomocník", layout="centered")

# --- ÚVOD ---
st.title("🚛 Kuriérska Apka v1.0")
st.write("Vodič: **Martin Huťka**")

# Konštanty pre tvoje vozidlo (25.6t s nákladom)
VAHA_AUTO_KG = 13000 
LIMIT_TONAZ = 7.5

# --- FUNKCIA PRE ČÍTANIE TEXTU ---
# Poznámka: Pre reálne čítanie textu v Streamlite sa najčastejšie používa EasyOCR
# Tu je pripravená štruktúra, ktorá spracuje dáta hneď po odfotení
def spracuj_obrazok(foto):
    # Simulujeme AI analýzu tvojho rozpisu
    # V plnej verzii by tu bol riadok: results = reader.readtext(foto)
    data = [
        {"firma": "Teckon Bytča", "vaha": 525},
        {"firma": "IMC Považská Bystrica", "vaha": 6336},
        {"firma": "Moravia Uherské Hradiště", "vaha": 5762}
    ]
    poznama = "Kód pre vodiča: 231 1613 | Plechy 2/3"
    return data, poznama

# --- ROZHRANIE PRE FOTENIE ---
foto = st.camera_input("📸 Odfotiť ranný rozpis")

if foto:
    st.success("Papier bol úspešne odfotený!")
    
    # Spracovanie dát
    firmy, info = spracuj_obrazok(foto)
    
    # Výpočty hmotnosti
    celkovy_naklad = sum(f["vaha"] for f in firmy)
    total_vaha_t = (VAHA_AUTO_KG + celkovy_naklad) / 1000
    
    # Zobrazenie výsledkov
    st.subheader("📋 Dnešný itinerár")
    for f in firmy:
        st.write(f"• **{f['firma']}** ({f['vaha']} kg)")
    
    st.divider()
    
    st.metric("Celková hmotnosť súpravy", f"{total_vaha_t:.2f} t")
    
    if total_vaha_t > LIMIT_TONAZ:
        st.error(f"⚠️ POZOR: Máš {total_vaha_t:.1f}t. Zákaz vjazdu nad 7.5t!")
        st.info("Navigácia bude nastavená na cesty I. triedy a diaľnice.")

    st.warning(f"ℹ️ **Poznámka:** {info}")

    # --- NAVIGÁCIA ---
    # Vygenerujeme trasu: Štart -> Firma 1 -> Firma 2 -> Firma 3
    body_trasy = ["Kovex Zilinska cesta"] + [f["firma"] for f in firmy]
    map_link = "https://www.google.com/maps/dir/" + "/".join(body_trasy).replace(" ", "+")
    
    st.link_button("🗺️ SPUSTIŤ NAVIGÁCIU (Google Maps)", map_link)

else:
    st.info("Ahoj Martin! Odfotografuj papier z dispečingu a ja ti vypočítam váhu a trasu.")

# Pridanie odkazu na mýto alebo servis ako bonus
with st.expander("Nástroje pre vodiča"):
    st.write("- Kontrola mýtneho stavu")
    st.write("- Najbližší servis (26.03. plánovaný)")
