import streamlit as st
import pandas as pd
import json
import os
import io

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Fanta-Amici 2026", layout="centered")

FILE_DATI = "fanta_data_v3.json"

# Lista FISSA dei partecipanti
PARTECIPANTI_FISSI = [
    "Alby", "Alfiere", "Edu", "Giorgio", "Keuch", 
    "Lupo", "Marika", "Mavi", "Mery", "Raffo", "Vincenzo"
]

# --- LOGICA PUNTEGGI INTEGRATA ---
TABELLA_PUNTI_DEFAULT = {
    "gay_ci_prova": -5,
    "approccio_esotico": 15,
    "conquista_riuscita": 10,
    "fingersi_straniero": 10,
    "scopata_posto_esotico": 90,
    "mavi_insulta": 50,
    "jacopo_non_ruba": 100,
    "rifiuto_faccende": -20,
    "medusa_punto": -15,
    "medusa_pisciata": 30,
    "alfiere_sclera": -15,
    "alfiere_beve": 50,
    "dormire_fuori": 25,
    "ospedale": -100,
    "secchiata_acqua": -40,
    "vestito_da_donna": 30
}

# Eventi che attivano il moltiplicatore esponenziale x1.25
EVENTI_MOLTIPLICATORE = ["conquista_riuscita", "scopata_posto_esotico"]

def calcola_punteggio_evento(evento, quantita, regolamento):
    """Calcola i punti applicando il bonus del 25% se previsto."""
    punti_base = regolamento.get(evento, 0)
    
    if evento in EVENTI_MOLTIPLICATORE and quantita > 1:
        totale = 0
        for i in range(quantita):
            totale += punti_base * (1.25 ** i)
        return round(totale, 2)
    
    return round(punti_base * quantita, 2)

# --- GESTIONE DATI ---
def carica_dati():
    if os.path.exists(FILE_DATI):
        with open(FILE_DATI, "r") as f:
            dati = json.load(f)
            # Assicuriamoci che tutti i partecipanti fissi siano presenti
            for nome in PARTECIPANTI_FISSI:
                if nome not in dati["amici"]:
                    dati["amici"][nome] = 0.0
            return dati
    
    return {
        "amici": {nome: 0.0 for nome in PARTECIPANTI_FISSI},
        "log": [],
        "regolamento": TABELLA_PUNTI_DEFAULT
    }

def salva_dati(dati):
    with open(FILE_DATI, "w") as f:
        json.dump(dati, f)

dati = carica_dati()

# --- SIDEBAR ---
st.sidebar.title("🏆 Fanta-Amici")
menu = st.sidebar.radio("Vai a:", ["Classifica", "Assegna Punti", "Configurazione Excel", "Esporta Dati"])

# --- 1. CONFIGURAZIONE EXCEL ---
if menu == "Configurazione Excel":
    st.header("📂 Gestione Regolamento")
    st.write("Puoi caricare un nuovo file Excel (colonne: 'Azione' e 'Punteggio') o usare quello predefinito.")
    
    file_caricato = st.file_uploader("Carica Excel Regolamento", type=["xlsx"])
    
    if file_caricato:
        try:
            df = pd.read_excel(file_caricato)
            dati["regolamento"] = dict(zip(df['Azione'], df['Punteggio']))
            salva_dati(dati)
            st.success("✅ Regolamento aggiornato!")
        except:
            st.error("Errore: Assicurati che le colonne siano 'Azione' e 'Punteggio'")
    
    st.subheader("Regolamento Attuale")
    st.table(pd.DataFrame(list(dati["regolamento"].items()), columns=["Azione", "Punti"]))

# --- 2. ASSEGNA PUNTI ---
elif menu == "Assegna Punti":
    st.header("⚡ Registro Eventi")
    
    amico = st.selectbox("Chi è il protagonista?", PARTECIPANTI_FISSI)
    azione = st.selectbox("Cosa è successo?", list(dati["regolamento"].keys()))
    
    # Se l'azione prevede moltiplicatori, chiediamo la quantità
    quantita = 1
    if azione in EVENTI_MOLTIPLICATORE:
        quantita = st.number_input("Quante persone coinvolte (nella stessa sera)?", min_value=1, value=1)
        st.info("💡 Questo evento applica il moltiplicatore esponenziale 1.25x")
    
    giorno = st.date_input("Data")
    
    if st.button("Registra Azione"):
        punti_ottenuti = calcola_punteggio_evento(azione, quantita, dati["regolamento"])
        dati["amici"][amico] += punti_ottenuti
        
        testo_log = f"{giorno} - {amico}: {punti_ottenuti} pt ({azione} x{quantita})"
        dati["log"].append(testo_log)
        
        salva_dati(dati)
        st.success(f"Registrato! {amico} guadagna {punti_ottenuti} punti.")

# --- 3. CLASSIFICA ---
elif menu == "Classifica":
    st.header("📊 Classifica Generale")
    
    df_classifica = pd.DataFrame(
        list(dati["amici"].items()), 
        columns=["Amico", "Punti Totalizzati"]
    ).sort_values(by="Punti Totalizzati", ascending=False)
    
    # Visualizzazione dinamica
    for i, row in enumerate(df_classifica.itertuples(), 1):
        prefisso = "🥇" if i==1 else "🥈" if i==2 else "🥉" if i==3 else f"{i}."
        st.subheader(f"{prefisso} {row.Amico}: {round(row._2, 2)} pt")
    
    if dati["log"]:
        st.divider()
        st.write("📜 **Cronologia Eventi:**")
        for log in reversed(dati["log"]):
            st.caption(log)

# --- 4. ESPORTA DATI (LOGICA EXCEL DI APP.PY) ---
elif menu == "Esporta Dati":
    st.header("📤 Esporta in Excel")
    st.write("Scarica la classifica finale in formato Excel.")
    
    df_export = pd.DataFrame(list(dati["amici"].items()), columns=["Partecipante", "Punteggio Totale"])
    df_export = df_export.sort_values(by="Punteggio Totale", ascending=False)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, index=False, sheet_name='Classifica')
    output.seek(0)
    
    st.download_button(
        label="📥 Scarica Classifica.xlsx",
        data=output,
        file_name="Classifica_Vacanza_2026.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
