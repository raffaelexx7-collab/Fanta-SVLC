import streamlit as st
import pandas as pd
import json
import os
import io

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Fanta-SanVito 2026", layout="centered", page_icon="🏖️")

# --- CSS PERSONALIZZATO PER IL LOOK ---
st.markdown("""
    <style>
    .main {
        background-color: #f0f8ff;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ff7575;
        transform: scale(1.02);
    }
    .punti-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 5px solid #007bff;
        margin-bottom: 10px;
    }
    .sidebar .sidebar-content {
        background-image: linear-gradient(#2e7bcf,#2e7bcf);
        color: white;
    }
    h1 {
        color: #1e3d59;
        font-family: 'Trebuchet MS', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

FILE_DATI = "fanta_data_v3.json"
PARTECIPANTI_FISSI = ["Alby", "Alfiere", "Edu", "Giorgio", "Keuch", "Lupo", "Marika", "Mavi", "Mery", "Raffo", "Vincenzo"]

# --- LOGICA PUNTEGGI (INVARIATA) ---
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

# --- HEADER CON FOTO DI SAN VITO ---
st.image("https://images.unsplash.com/photo-1544015759-237f87d3a002?q=80&w=1000", caption="San Vito Lo Capo 2026 🌴")
st.title("🏆 Fanta-San Vito 2026")

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🧭 Navigazione")
    menu = st.radio("Scegli sezione:", ["📊 Classifica", "⚡ Assegna Punti", "📂 Regolamento", "📤 Esporta"])
    st.divider()
    st.info("Regola d'oro: Quello che succede a San Vito, finisce in classifica.")

# --- 1. CLASSIFICA (STILE CARD) ---
if menu == "📊 Classifica":
    st.header("Classifica Generale")
    
    df_classifica = pd.DataFrame(list(dati["amici"].items()), columns=["Amico", "Punti"]).sort_values(by="Punti", ascending=False)
    
    cols = st.columns(1) # Unica colonna centrata
    for i, row in enumerate(df_classifica.itertuples(), 1):
        emoji = "🥇" if i==1 else "🥈" if i==2 else "🥉" if i==3 else "🏖️"
        st.markdown(f"""
            <div class="punti-card">
                <h3 style='margin:0;'>{emoji} {row.Amico}</h3>
                <h2 style='color:#ff4b4b; margin:0;'>{round(row.Punti, 2)} <small>pt</small></h2>
            </div>
            """, unsafe_allow_html=True)
    
    if dati["log"]:
        with st.expander("📜 Cronologia Eventi"):
            for log in reversed(dati["log"]):
                st.caption(log)

# --- 2. ASSEGNA PUNTI ---
elif menu == "⚡ Assegna Punti":
    with st.container():
        st.header("Registra un Evento")
        with st.form("form_punti"):
            col1, col2 = st.columns(2)
            with col1:
                amico = st.selectbox("Protagonista", PARTECIPANTI_FISSI)
            with col2:
                azione = st.selectbox("Azione", list(dati["regolamento"].keys()))
            
            quantita = 1
            if azione in EVENTI_MOLTIPLICATORE:
                quantita = st.number_input("Persone coinvolte", min_value=1, value=1)
            
            submit = st.form_submit_button("CONFERMA AZIONE 🚀")
            
            if submit:
                punti = calcola_punteggio_evento(azione, quantita, dati["regolamento"])
                dati["amici"][amico] += punti
                dati["log"].append(f"{amico}: {punti} pt ({azione} x{quantita})")
                salva_dati(dati)
                st.balloons()
                st.success(f"Dati salvati per {amico}!")

# --- 3. REGOLAMENTO ---
elif menu == "📂 Regolamento":
    st.header("Regolamento Attuale")
    df_reg = pd.DataFrame(list(dati["regolamento"].items()), columns=["Azione", "Punti"])
    st.dataframe(df_reg, use_container_width=True)
    
    st.divider()
    st.subheader("Aggiorna Regolamento")
    file_caricato = st.file_uploader("Carica Excel", type=["xlsx"])
    if file_caricato:
        df = pd.read_excel(file_caricato)
        dati["regolamento"] = dict(zip(df['Azione'], df['Punteggio']))
        salva_dati(dati)
        st.success("Regolamento aggiornato!")

# --- 4. ESPORTA ---
elif menu == "📤 Esporta":
    st.header("Scarica i Dati")
    df_export = pd.DataFrame(list(dati["amici"].items()), columns=["Partecipante", "Punteggio"]).sort_values(by="Punteggio", ascending=False)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, index=False)
    output.seek(0)
    
    st.download_button("📥 Scarica Excel", data=output, file_name="Classifica_SanVito.xlsx")
    
