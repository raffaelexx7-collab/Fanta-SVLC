import streamlit as st
import pandas as pd
import json
import os
import io
from datetime import datetime, time

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Fanta-SanVito 2026", layout="centered", page_icon="🏖️")

# --- CSS PER GRAFICA ---
st.markdown("""
    <style>
    .main { background-color: #eef2f7; }
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
    .nome-partecipante { color: #1a2a6c; font-size: 22px !important; font-weight: 800 !important; }
    .punti-display { color: #ff4b4b; font-size: 26px !important; font-weight: 900 !important; }
    .stButton>button { border-radius: 10px; background-color: #1a2a6c; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- COSTANTI E DATI ---
FILE_DATI = "fanta_data_v3.json"
PARTECIPANTI_FISSI = ["Alby", "Alfiere", "Edu", "Giorgio", "Keuch", "Lupo", "Marika", "Mavi", "Mery", "Raffo", "Vincenzo"]
TABELLA_PUNTI_DEFAULT = {
    "gay_ci_prova": -5, "approccio_esotico": 15, "conquista_riuscita": 10,
    "fingersi_straniero": 10, "scopata_posto_esotico": 90, "mavi_insulta": 50,
    "jacopo_non_ruba": 100, "rifiuto_faccende": -20, "medusa_punto": -15,
    "medusa_pisciata": 30, "alfiere_sclera": -15, "alfiere_beve": 50,
    "dormire_fuori": 25, "ospedale": -100, "secchiata_acqua": -40, "vestito_da_donna": 30
}
EVENTI_MOLTIPLICATORE = ["conquista_riuscita", "scopata_posto_esotico"]

# --- FUNZIONI DI SERVIZIO ---
def carica_dati():
    try:
        if os.path.exists(FILE_DATI):
            with open(FILE_DATI, "r") as f:
                return json.load(f)
    except:
        pass
    return {
        "amici": {nome: 0.0 for nome in PARTECIPANTI_FISSI},
        "punti_giornalieri": {nome: 0.0 for nome in PARTECIPANTI_FISSI},
        "log": [],
        "regolamento": TABELLA_PUNTI_DEFAULT,
        "is_running": False,
        "ultima_pulizia": None
    }

def salva_dati(dati):
    with open(FILE_DATI, "w") as f:
        json.dump(dati, f, indent=4)

def genera_excel(dati_amici, titolo_foglio):
    output = io.BytesIO()
    df = pd.DataFrame(list(dati_amici.items()), columns=["Partecipante", "Punteggio Totale"])
    df = df.sort_values(by="Punteggio Totale", ascending=False)
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=titolo_foglio)
    return output.getvalue()

dati = carica_dati()

# --- LOGICA RESET ORE 08:00 ---
ora_attuale = datetime.now()
oggi_str = ora_attuale.strftime("%Y-%m-%d")
if ora_attuale.time() >= time(8, 0) and dati.get("ultima_pulizia") != oggi_str:
    dati["punti_giornalieri"] = {nome: 0.0 for nome in PARTECIPANTI_FISSI}
    dati["ultima_pulizia"] = oggi_str
    salva_dati(dati)

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Gestione")
    if not dati["is_running"]:
        if st.button("▶️ INIZIA VACANZA"):
            dati["is_running"] = True
            salva_dati(dati)
            st.rerun()
    else:
        if st.button("⏹️ STOP VACANZA"):
            dati["is_running"] = False
            salva_dati(dati)
            st.rerun()
    menu = st.radio("Vai a:", ["📊 Classifiche", "⚡ Assegna Punti", "📜 Regolamento"])

# --- MENU: CLASSIFICHE ---
if menu == "📊 Classifiche":
    st.title("🏆 Fanta-SanVito 2026")
    tab1, tab2 = st.tabs(["🌎 Classifica Generale", "📅 Classifica di Oggi"])
    
    with tab1:
        df_gen = pd.DataFrame(list(dati["amici"].items()), columns=["Amico", "Punti"]).sort_values("Punti", ascending=False)
        for i, row in enumerate(df_gen.itertuples(), 1):
            classe = "card-comune"
            if i==1: classe += " card-oro"
            elif i==2: classe += " card-argento"
            elif i==3: classe += " card-bronzo"
            st.markdown(f'<div class="{classe}"><div class="nome-partecipante">{i}. {row.Amico}</div><div class="punti-display">{round(row.Punti, 2)}</div></div>', unsafe_allow_html=True)
        
        # Bottone per scaricare Excel invece del PDF
        excel_data = genera_excel(dati["amici"], "Classifica Generale")
        st.download_button(
            label="📥 Scarica Classifica Excel",
            data=excel_data,
            file_name=f"Classifica_Generale_{oggi_str}.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with tab2:
        st.subheader("Punteggi accumulati dalle 08:00 di oggi")
        df_day = pd.DataFrame(list(dati["punti_giornalieri"].items()), columns=["Amico", "Punti"]).sort_values("Punti", ascending=False)
        st.table(df_day)
        
        # Bottone Excel per la classifica del giorno
        excel_day_data = genera_excel(dati["punti_giornalieri"], "Classifica Oggi")
        st.download_button(
            label="📥 Scarica Excel di Oggi",
            data=excel_day_data,
            file_name=f"Classifica_Giornaliera_{oggi_str}.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# --- MENU: ASSEGNA PUNTI ---
elif menu == "⚡ Assegna Punti":
    st.title("📝 Registra Evento")
    if not dati["is_running"]:
        st.warning("⚠️ La vacanza è in pausa. Clicca INIZIA nella sidebar per registrare punti.")
    else:
        with st.form("p_form"):
            amico = st.selectbox("Chi è il colpevole?", PARTECIPANTI_FISSI)
            azione = st.selectbox("Cosa ha combinato?", list(dati["regolamento"].keys()))
            qta = st.number_input("Quante volte/persone? (Per baci/scopate)", min_value=1, step=1, value=1)
            
            if st.form_submit_button("CONFERMA E REGISTRA 🚀"):
                base = dati["regolamento"].get(azione, 0)
                # Calcolo con moltiplicatore 1.25x se previsto
                if azione in EVENTI_MOLTIPLICATORE and qta > 1:
                    punti = sum(base * (1.25 ** i) for i in range(qta))
                else:
                    punti = base * qta
                
                dati["amici"][amico] += punti
                dati["punti_giornalieri"][amico] += punti
                dati["log"].append(f"{datetime.now().strftime('%H:%M')} - {amico}: {round(punti, 2)} pt ({azione})")
                salva_dati(dati)
                st.balloons()
                st.success(f"Registrato! {amico} ha ottenuto {round(punti, 2)} punti.")

# --- MENU: REGOLAMENTO ---
elif menu == "📜 Regolamento":
    st.title("📖 Regolamento e Punteggi")
    st.table(pd.DataFrame(list(dati["regolamento"].items()), columns=["Azione", "Punti"]))
    
