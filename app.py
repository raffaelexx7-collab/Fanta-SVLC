import streamlit as st
import pandas as pd
import json
import os

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Fanta-Amici", layout="centered")

FILE_DATI = "fanta_data_v3.json"

# Lista FISSA dei partecipanti (nessuna aggiunta possibile)
PARTECIPANTI_FISSI = [
    "Alby", "Alfiere", "Edu", "Giorgio", "Keuch", 
    "Lupo", "Marika", "Mavi", "Mery", "Raffo", "Vincenzo"
]

def carica_dati():
    if os.path.exists(FILE_DATI):
        with open(FILE_DATI, "r") as f:
            dati = json.load(f)
            # Filtriamo i dati per tenere solo i nomi della lista fissa
            dati["amici"] = {nome: dati["amici"].get(nome, 0) for nome in PARTECIPANTI_FISSI}
            return dati
    
    # Inizializzazione se il file non esiste
    return {
        "amici": {nome: 0 for nome in PARTECIPANTI_FISSI},
        "log": [],
        "regolamento": {}
    }

def salva_dati(dati):
    with open(FILE_DATI, "w") as f:
        json.dump(dati, f)

dati = carica_dati()

# --- SIDEBAR / MENU ---
st.sidebar.title("🏆 Fanta-Amici")
# Menu ridotto: rimossa la gestione amici
menu = st.sidebar.radio("Vai a:", ["Classifica", "Assegna Punti", "Configurazione Excel"])

# --- 1. CONFIGURAZIONE EXCEL (IMPORT REGOLAMENTO) ---
if menu == "Configurazione Excel":
    st.header("📂 Importa Regolamento")
    st.write("Carica il file Excel con le colonne: **Azione** e **Punteggio**")
    
    file_caricato = st.file_uploader("Scegli un file Excel", type=["xlsx", "csv"])
    
    if file_caricato:
        try:
            if file_caricato.name.endswith('.csv'):
                df = pd.read_csv(file_caricato)
            else:
                df = pd.read_excel(file_caricato)
            
            nuovo_regolamento = dict(zip(df['Azione'], df['Punteggio']))
            dati["regolamento"] = nuovo_regolamento
            salva_dati(dati)
            st.success("✅ Regolamento caricato correttamente!")
            st.table(df) # Mostra tabella per controllo rapido
        except Exception as e:
            st.error("Errore nel file: assicurati che le intestazioni siano 'Azione' e 'Punteggio'.")

# --- 2. ASSEGNA PUNTI ---
elif menu == "Assegna Punti":
    st.header("⚡ Assegna Bonus/Malus")
    
    if not dati["regolamento"]:
        st.warning("⚠️ Carica prima il regolamento nel menu 'Configurazione Excel'!")
    else:
        # Selettore limitato solo ai partecipanti fissi
        amico = st.selectbox("Chi ha fatto l'azione?", PARTECIPANTI_FISSI)
        azione = st.selectbox("Seleziona l'azione:", list(dati["regolamento"].keys()))
        giorno = st.date_input("Data dell'evento")
        
        if st.button("Conferma e Salva"):
            punti = dati["regolamento"][azione]
            dati["amici"][amico] += punti
            dati["log"].append(f"{giorno} - {amico}: {punti} pt ({azione})")
            salva_dati(dati)
            st.success(f"Punteggio aggiornato per {amico}!")

# --- 3. CLASSIFICA ---
elif menu == "Classifica":
    st.header("📊 Classifica Generale")
    
    # Creazione DataFrame per la visualizzazione
    classifica = pd.DataFrame(
        list(dati["amici"].items()), 
        columns=["Amico", "Punti"]
    ).sort_values(by="Punti", ascending=False)
    
    # Visualizzazione podio e altri
    for i, row in enumerate(classifica.itertuples(), 1):
        prefisso = "🥇" if i==1 else "🥈" if i==2 else "🥉" if i==3 else f"{i}."
        st.subheader(f"{prefisso} {row.Amico}: {row.Punti} pt")
    
    if dati["log"]:
        st.divider()
        st.write("📜 **Ultimi aggiornamenti:**")
        # Mostra gli ultimi 15 eventi registrati
        for log in reversed(dati["log"][-15:]):
            st.caption(log)
            
