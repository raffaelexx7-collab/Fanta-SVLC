import streamlit as st
import pandas as pd
import json
import os
import io

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Fanta-SanVito 2026", layout="centered", page_icon="🏖️")

# --- CSS AGGIORNATO PER MASSIMA LEGGIBILITÀ ---
st.markdown("""
    <style>
    .main {
        background-color: #eef2f7;
    }
    /* Stile per le card della classifica */
    .card-comune {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 12px;
        border: 2px solid #d1d9e6;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .card-oro { border: 3px solid #FFD700; background-color: #FFFDF0; }
    .card-argento { border: 3px solid #C0C0C0; background-color: #F8F8F8; }
    .card-bronzo { border: 3px solid #CD7F32; background-color: #FFF9F5; }
    
    .nome-partecipante {
        color: #1a2a6c;
        font-size: 24px !important;
        font-weight: 800 !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .punti-display {
        color: #ff4b4b;
        font-size: 28px !important;
        font-weight: 900 !important;
    }
    .stButton>button {
        border-radius: 10px;
        height: 3em;
        background-color: #1a2a6c;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

FILE_DATI = "fanta_data_v3.json"
PARTECIPANTI_FISSI = ["Alby", "Alfiere", "Edu", "Giorgio", "Keuch", "Lupo", "Marika", "Mavi", "Mery", "Raffo", "Vincenzo"]

# --- FUNZIONI CORE ---
TABELLA_PUNTI_DEFAULT = {
    "gay_ci_prova": -5, "approccio_esotico": 15, "conquista_riuscita": 10,
    "fingersi_straniero": 10, "scopata_posto_esotico": 90, "mavi_insulta": 50,
    "jacopo_non_ruba": 100, "rifiuto_faccende": -20, "medusa_punto": -15,
    "medusa_pisciata": 30, "alfiere_sclera": -15, "alfiere_beve": 50,
    "dormire_fuori": 25, "ospedale": -100, "secchiata_acqua": -40, "vestito_da_donna": 30
}
EVENTI_MOLTIPLICATORE = ["conquista_riuscita", "scopata_posto_esotico"]

def calcola_punteggio_evento(evento, quantita, regolamento):
    punti_base = regolamento.get(evento, 0)
    if evento in EVENTI_MOLTIPLICATORE and quantita > 1:
        totale = sum(punti_base * (1.25 ** i) for i in range(quantita))
        return round(totale, 2)
    return round(punti_base * quantita, 2)

def carica_dati():
    if os.path.exists(FILE_DATI):
        with open(FILE_DATI, "r") as f:
            dati = json.load(f)
            for nome in PARTECIPANTI_FISSI:
                if nome not in dati["amici"]: dati["amici"][nome] = 0.0
            return dati
    return {"amici": {nome: 0.0 for nome in PARTECIPANTI_FISSI}, "log": [], "regolamento": TABELLA_PUNTI_DEFAULT}

def salva_dati(dati):
    with open(FILE_DATI, "w") as f: json.dump(dati, f)

dati = carica_dati()

# --- HEADER ---
st.image("https://images.unsplash.com/photo-1544015759-237f87d3a002?q=80&w=1000", use_column_width=True)
st.title("🏖️ Fanta-San Vito 2026")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Menu")
    menu = st.radio("Seleziona:", ["📊 Classifica", "⚡ Registra Azione", "📂 Impostazioni", "📤 Export"])

# --- SEZIONE 1: CLASSIFICA ---
if menu == "📊 Classifica":
    st.markdown("### 🏆 Classifica in tempo reale")
    
    df_classifica = pd.DataFrame(list(dati["amici"].items()), columns=["Amico", "Punti"]).sort_values(by="Punti", ascending=False)
    
    for i, row in enumerate(df_classifica.itertuples(), 1):
        # Determina classe CSS in base alla posizione
        classe_card = "card-comune"
        if i == 1: classe_card += " card-oro"
        elif i == 2: classe_card += " card-argento"
        elif i == 3: classe_card += " card-bronzo"
        
        emoji = "🥇" if i==1 else "🥈" if i==2 else "🥉" if i==3 else f"{i}."
        
        st.markdown(f"""
            <div class="{classe_card}">
                <div class="nome-partecipante">{emoji} {row.Amico}</div>
                <div class="punti-display">{round(row.Punti, 2)} <span style='font-size:14px; color:#666;'>PT</span></div>
            </div>
            """, unsafe_allow_html=True)

# --- SEZIONE 2: ASSEGNA PUNTI ---
elif menu == "⚡ Registra Azione":
    st.markdown("### 📝 Aggiungi punti")
import streamlit as st
import pandas as pd
import json
import os
import io
from datetime import datetime, time
from fpdf import FPDF

# --- CONFIGURAZIONE PAGINA ---

    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, txt=titolo, ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(95, 10, "Partecipante", border=1)
    pdf.cell(95, 10, "Punti", border=1, ln=True)
    pdf.set_font("Arial", "", 12)
    classifica = sorted(dati_amici.items(), key=lambda x: x[1], reverse=True)
    for nome, punti in classifica:
        pdf.cell(95, 10, nome, border=1)
        pdf.cell(95, 10, str(round(punti, 2)), border=1, ln=True)
    return pdf.output(dest='S').encode('latin-1')

def carica_dati():
    if os.path.exists(FILE_DATI):
        with open(FILE_DATI, "r") as f:
            dati = json.load(f)
    else:
        dati = {
            "amici": {nome: 0.0 for nome in PARTECIPANTI_FISSI},
            "punti_giornalieri": {nome: 0.0 for nome in PARTECIPANTI_FISSI},
            "log": [],
            "regolamento": TABELLA_PUNTI_DEFAULT,
            "is_running": False,
            "ultima_pulizia": None
        }
    
    # Logica Reset Ore 08:00
    ora_attuale = datetime.now()
    oggi_str = ora_attuale.strftime("%Y-%m-%d")
    if ora_attuale.time() >= time(8, 0) and dati.get("ultima_pulizia") != oggi_str:
        dati["punti_giornalieri"] = {nome: 0.0 for nome in PARTECIPANTI_FISSI}
        dati["ultima_pulizia"] = oggi_str
        with open(FILE_DATI, "w") as f: json.dump(dati, f)
    return dati

def calcola_punti_esponenziali(evento, qta, regolamento):
    base = regolamento.get(evento, 0)
    if evento in EVENTI_MOLTIPLICATORE and qta > 1:
        return round(sum(base * (1.25 ** i) for i in range(qta)), 2)
    return round(base * qta, 2)

dati = carica_dati()

# --- SIDEBAR CONTROLLI ---
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1544015759-237f87d3a002?q=80&w=1000")
    st.title("⚙️ Gestione")
    if not dati["is_running"]:
        if st.button("▶️ INIZIA VACANZA"):
            dati["is_running"] = True
            with open(FILE_DATI, "w") as f: json.dump(dati, f)
            st.rerun()
    else:
        if st.button("⏹️ STOP VACANZA"):
            dati["is_running"] = False
            with open(FILE_DATI, "w") as f: json.dump(dati, f)
            st.rerun()
    
    menu = st.radio("Naviga:", ["📊 Classifiche", "⚡ Assegna Punti", "📜 Regolamento"])

# --- MENU: CLASSIFICHE ---
if menu == "📊 Classifiche":
    st.title("🏆 Classifiche San Vito")
    tab1, tab2 = st.tabs(["🌎 Generale", "📅 Di Oggi (Reset 08:00)"])
    
    with tab1:
        df_gen = pd.DataFrame(list(dati["amici"].items()), columns=["Amico", "Punti"]).sort_values("Punti", ascending=False)
        for i, row in enumerate(df_gen.itertuples(), 1):
            classe = "card-comune"
            if i==1: classe += " card-oro"
            elif i==2: classe += " card-argento"
            elif i==3: classe += " card-bronzo"
            st.markdown(f'<div class="{classe}"><div class="nome-partecipante">{i}. {row.Amico}</div><div class="punti-display">{round(row.Punti, 2)}</div></div>', unsafe_allow_html=True)
        
        pdf_data = genera_pdf(dati["amici"], "Classifica Generale Finale")
        st.download_button("📥 Scarica PDF Classifica", data=pdf_data, file_name="classifica_fanta.pdf")

    with tab2:
        df_day = pd.DataFrame(list(dati["punti_giornalieri"].items()), columns=["Amico", "Punti"]).sort_values("Punti", ascending=False)
        st.table(df_day)

# --- MENU: ASSEGNA PUNTI ---
elif menu == "⚡ Assegna Punti":
    st.title("📝 Registra Evento")
    if not dati["is_running"]:
        st.warning("⚠️ La vacanza non è ancora iniziata! Clicca INIZIA nella sidebar.")
    else:
        with st.form("punti_form"):
            amico = st.selectbox("Chi?", PARTECIPANTI_FISSI)
            azione = st.selectbox("Cosa?", list(dati["regolamento"].keys()))
            qta = st.number_input("Quantità (per baci/scopate)", min_value=1, step=1)
            if st.form_submit_button("CONFERMA"):
                punti = calcola_punti_esponenziali(azione, qta, dati["regolamento"])
                dati["amici"][amico] += punti
                dati["punti_giornalieri"][amico] += punti
                dati["log"].append(f"{amico}: {punti} pt ({azione})")
                with open(FILE_DATI, "w") as f: json.dump(dati, f)
                st.balloons()
                st.success("Punteggio aggiornato!")

# --- MENU: REGOLAMENTO ---
elif menu == "📜 Regolamento":
    st.title("Regole del Gioco")
    st.table(pd.DataFrame(list(dati["regolamento"].items()), columns=["Evento", "Punti"]))
