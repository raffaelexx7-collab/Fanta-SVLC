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
def get_default_dati():
    return {
        "amici": {nome: 0.0 for nome in PARTECIPANTI_FISSI},
        "punti_giornalieri": {nome: 0.0 for nome in PARTECIPANTI_FISSI},
        "log": [],
        "regolamento": TABELLA_PUNTI_DEFAULT,
        "is_running": False,
        "ultima_pulizia": None
    }

def carica_dati():
    default = get_default_dati()
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
    df = pd.DataFrame(list(dati_dict.items()), columns=["Partecipante", "Punteggio"]).sort_values("Punteggio", ascending=False)
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
    if not dati.get("is_running", False):
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
    st.divider()
    if st.button("🔥 RESET TOTALE", help="Azzera TUTTI i dati"):
        dati = get_default_dati()
        salva_dati(dati)
        st.rerun()

# --- FUNZIONE GRAFICA CLASSIFICA ---
def mostra_classifica_grafica(dizionario_punti):
    df = pd.DataFrame(list(dizionario_punti.items()), columns=["Amico", "Punti"]).sort_values("Punti", ascending=False)
    for i, row in enumerate(df.itertuples(), 1):
        classe = "card-comune " + ("card-oro" if i==1 else "card-argento" if i==2 else "card-bronzo" if i==3 else "")
        st.markdown(f'<div class="{classe}"><div class="nome-partecipante">{i}. {row.Amico}</div><div class="punti-display">{round(row.Punti, 2)}</div></div>', unsafe_allow_html=True)

# --- MENU: CLASSIFICHE ---
if menu == "📊 Classifiche":
    st.title("🏆 Classifiche San Vito")
    tab1, tab2 = st.tabs(["🌎 Classifica Totale", "📅 Classifica di Oggi"])
    
    with tab1:
        mostra_classifica_grafica(dati["amici"])
        ex_gen = genera_excel(dati["amici"], "Totale")
        st.download_button("📥 Scarica Excel Totale", ex_gen, f"Totale_{oggi_str}.xlsx")

    with tab2:
        mostra_classifica_grafica(dati["punti_giornalieri"])
        ex_day = genera_excel(dati["punti_giornalieri"], "Oggi")
        st.download_button("📥 Scarica Excel Oggi", ex_day, f"Oggi_{oggi_str}.xlsx")

# --- MENU: ASSEGNA PUNTI ---
elif menu == "⚡ Assegna Punti":
    st.title("📝 Gestione Punti")
    
    st.subheader("Aggiungi Punteggio")
    if not dati.get("is_running", False):
        st.warning("Attiva la vacanza nella sidebar!")
    else:
        with st.form("form_punti", clear_on_submit=True):
            amico = st.selectbox("Chi?", PARTECIPANTI_FISSI)
            azione = st.selectbox("Cosa?", list(dati["regolamento"].keys()))
            qta = st.number_input("Quantità", 1, 100, 1)
            if st.form_submit_button("REGISTRA 🚀"):
                base = dati["regolamento"].get(azione, 0)
                tot = sum(base * (1.25 ** i) for i in range(qta)) if azione in EVENTI_MOLTIPLICATORE else base * qta
                
                log_entry = {
                    "id": datetime.now().timestamp(),
                    "nome": amico, 
                    "data_ora": datetime.now().strftime("%d/%m %H:%M"), 
                    "azione": azione, 
                    "punti": round(tot, 2),
                    "giorno": oggi_str 
                }
                dati["log"].append(log_entry)
                dati["amici"][amico] += tot
                dati["punti_giornalieri"][amico] += tot
                salva_dati(dati)
                
                # --- PALLONCINI REINSERITI QUI ---
                st.balloons()
                st.success(f"Registrato: {amico} +{round(tot, 2)}!")
                # Il rerun deve essere chiamato dopo i palloncini o st.success per dar modo di vederli
                # ma in Streamlit a volte i palloncini scompaiono subito col rerun.
                # Se non li vedi, togli lo st.rerun() qui sotto.

    st.divider()
    
    # ELIMINAZIONE SELETTIVA
    st.subheader("🗑️ Elimina un errore")
    if dati["log"]:
        opzioni_log = {f"{l['data_ora']} - {l['nome']} ({l['azione']} {l['punti']}pt)": i 
                       for i, l in enumerate(reversed(dati["log"]))}
        
        selezione = st.selectbox("Quale inserimento vuoi eliminare?", list(opzioni_log.keys()))
        
        if st.button("ELIMINA SELEZIONATO ❌"):
            idx_reale = len(dati["log"]) - 1 - opzioni_log[selezione]
            eliminato = dati["log"].pop(idx_reale)
            
            dati["amici"][eliminato["nome"]] -= eliminato["punti"]
            if eliminato.get("giorno") == oggi_str:
                dati["punti_giornalieri"][eliminato["nome"]] -= eliminato["punti"]
            
            salva_dati(dati)
            st.error(f"Eliminato: {selezione}")
            st.rerun()
    else:
        st.info("Nessun punteggio presente da eliminare.")

# --- MENU: CRONOLOGIA ---
elif menu == "🕒 Cronologia":
    st.title("🕒 Cronologia")
    for persona in PARTECIPANTI_FISSI:
        log_persona = [l for l in dati["log"] if isinstance(l, dict) and l.get("nome") == persona]
        with st.expander(f"👤 {persona} - {round(dati['amici'][persona], 2)} pt"):
            if log_persona:
                df_log = pd.DataFrame(log_persona)[["data_ora", "azione", "punti"]]
                df_log.columns = ["Ora", "Azione", "PT"]
                st.table(df_log.iloc[::-1])
            else:
                st.write("Nessun dato.")

# --- MENU: REGOLAMENTO ---
elif menu == "📜 Regolamento":
    st.title("📖 Regolamento")
    st.table(pd.DataFrame(list(dati["regolamento"].items()), columns=["Azione", "Punti"]))
    
