import streamlit as st
import pandas as pd
import json
import os
import io
from datetime import datetime, time

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Fanta-SanVito 2026", layout="centered", page_icon="🏖️")

# --- CSS PER LEGGIBILITÀ ---
st.markdown("""
    <style>
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
    </style>
    """, unsafe_allow_html=True)

# --- COSTANTI ---
FILE_DATI = "fanta_data_v3.json"
PARTECIPANTI_FISSI = sorted(["Alby", "Alfiere", "Edu", "Giorgio", "Keuch", "Lupo", "Marika", "Mavi", "Mery", "Raffo", "Vincenzo"])
TABELLA_PUNTI_DEFAULT = {
    "gay_ci_prova": -5, "approccio_esotico": 15, "conquista_riuscita": 10,
    "scopata_posto_esotico": 90, "mavi_insulta": 50, "jacopo_non_ruba": 100,
    "rifiuto_faccende": -20, "alfiere_beve": 50, "vestito_da_donna": 30
}
EVENTI_MOLTIPLICATORE = ["conquista_riuscita", "scopata_posto_esotico"]

# --- GESTIONE DATI ---
def carica_dati():
    default = {
        "amici": {nome: 0.0 for nome in PARTECIPANTI_FISSI},
        "punti_giornalieri": {nome: 0.0 for nome in PARTECIPANTI_FISSI},
        "log": [],
        "regolamento": TABELLA_PUNTI_DEFAULT,
        "is_running": False,
        "ultima_pulizia": None
    }
    if os.path.exists(FILE_DATI):
        try:
            with open(FILE_DATI, "r") as f:
                caricati = json.load(f)
                for k in default:
                    if k not in caricati: caricati[k] = default[k]
                return caricati
        except: return default
    return default

def salva_dati(dati):
    with open(FILE_DATI, "w") as f:
        json.dump(dati, f, indent=4)

def genera_excel(dati_dict, nome_foglio):
    df = pd.DataFrame(list(dati_dict.items()), columns=["Partecipante", "Punteggio"])
    df = df.sort_values(by="Punteggio", ascending=False)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=nome_foglio)
    return output.getvalue()

dati = carica_dati()

# --- RESET GIORNALIERO ---
ora_attuale = datetime.now()
oggi_str = ora_attuale.strftime("%Y-%m-%d")
if ora_attuale.time() >= time(8, 0) and dati.get("ultima_pulizia") != oggi_str:
    dati["punti_giornalieri"] = {nome: 0.0 for nome in PARTECIPANTI_FISSI}
    dati["ultima_pulizia"] = oggi_str
    salva_dati(dati)

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Gestione")
    is_running = dati.get("is_running", False)
    if not is_running:
        if st.button("▶️ INIZIA VACANZA"):
            dati["is_running"] = True
            salva_dati(dati)
            st.rerun()
    else:
        st.success("✅ Vacanza Attiva")
        if st.button("⏹️ STOP VACANZA"):
            dati["is_running"] = False
            salva_dati(dati)
            st.rerun()
    menu = st.radio("Sezioni:", ["📊 Classifiche", "⚡ Assegna Punti", "🕒 Cronologia", "📜 Regolamento"])

# --- MENU: CLASSIFICHE ---
if menu == "📊 Classifiche":
    st.title("🏆 Classifiche San Vito")
    tab1, tab2 = st.tabs(["🌎 Totale", "📅 Oggi"])
    
    with tab1:
        df_gen = pd.DataFrame(list(dati["amici"].items()), columns=["Amico", "Punti"]).sort_values("Punti", ascending=False)
        for i, row in enumerate(df_gen.itertuples(), 1):
            classe = "card-comune " + ("card-oro" if i==1 else "card-argento" if i==2 else "card-bronzo" if i==3 else "")
            st.markdown(f'<div class="{classe}"><div class="nome-partecipante">{i}. {row.Amico}</div><div class="punti-display">{round(row.Punti, 2)}</div></div>', unsafe_allow_html=True)
        
        ex_gen = genera_excel(dati["amici"], "Generale")
        st.download_button("📥 Scarica Excel Totale", ex_gen, f"Fanta_Generale_{oggi_str}.xlsx")

    with tab2:
        df_day = pd.DataFrame(list(dati["punti_giornalieri"].items()), columns=["Amico", "Punti"]).sort_values("Punti", ascending=False)
        st.table(df_day)

# --- MENU: ASSEGNA PUNTI ---
elif menu == "⚡ Assegna Punti":
    st.title("📝 Registra Azione")
    if not dati.get("is_running", False):
        st.warning("⚠️ La vacanza è chiusa. Attivala dalla sidebar.")
    else:
        with st.form("form_punti"):
            amico = st.selectbox("Chi?", PARTECIPANTI_FISSI)
            azione = st.selectbox("Cosa?", list(dati["regolamento"].keys()))
            qta = st.number_input("Quantità", 1, 100, 1)
            if st.form_submit_button("REGISTRA 🚀"):
                base = dati["regolamento"].get(azione, 0)
                tot = sum(base * (1.25 ** i) for i in range(qta)) if azione in EVENTI_MOLTIPLICATORE else base * qta
                
                # Registrazione nel Log per la Cronologia
                timestamp = datetime.now().strftime("%Y-%m-%d | %H:%M")
                dati["log"].append({"nome": amico, "data": timestamp, "azione": azione, "punti": round(tot, 2)})
                
                dati["amici"][amico] += tot
                dati["punti_giornalieri"][amico] += tot
                salva_dati(dati)
                st.success(f"Registrato! {amico} +{round(tot, 2)} pt")

# --- MENU: CRONOLOGIA (NUOVO) ---
elif menu == "🕒 Cronologia":
    st.title("🕒 Cronologia Punteggi")
    st.info("Clicca sul nome di una persona per vedere tutti i suoi punteggi.")

    # Creiamo un dizionario per filtrare i log per persona
    for persona in PARTECIPANTI_FISSI:
        log_persona = [l for l in dati["log"] if l["nome"] == persona]
        
        with st.expander(f"👤 {persona} (Totale: {round(dati['amici'][persona], 2)} pt)"):
            if not log_persona:
                st.write("Nessuna azione registrata.")
            else:
                # Trasformiamo in DataFrame per visualizzarlo meglio
                df_log = pd.DataFrame(log_persona)[["data", "azione", "punti"]]
                df_log.columns = ["Data e Ora", "Cosa ha fatto", "Punti"]
                # Invertiamo l'ordine per vedere le più recenti in alto
                st.table(df_day = df_log.iloc[::-1])

# --- MENU: REGOLAMENTO ---
elif menu == "📜 Regolamento":
    st.title("📖 Tabella Punteggi")
    st.table(pd.DataFrame(list(dati["regolamento"].items()), columns=["Azione", "Punti"]))
    
    
