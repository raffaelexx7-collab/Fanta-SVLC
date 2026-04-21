import streamlit as st
import pandas as pd
import json
import os

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Fanta-Amici Mobile", layout="centered")

FILE_DATI = "fanta_data_v2.json"

def carica_dati():
    if os.path.exists(FILE_DATI):
        with open(FILE_DATI, "r") as f:
            return json.load(f)
    return {"amici": {}, "log": [], "regolamento": {}}

def salva_dati(dati):
    with open(FILE_DATI, "w") as f:
        json.dump(dati, f)

dati = carica_dati()

# --- SIDEBAR / MENU ---
st.sidebar.title("🏆 Fanta-Amici")
menu = st.sidebar.radio("Vai a:", ["Classifica", "Assegna Punti", "Gestione Amici", "Configurazione Excel"])

# --- 1. CONFIGURAZIONE EXCEL (IMPORT REGOLAMENTO) ---
if menu == "Configurazione Excel":
    st.header("📂 Importa Regolamento")
    st.write("Carica un file Excel con le colonne: **Azione** e **Punteggio**")
    
    file_caricato = st.file_uploader("Scegli un file Excel", type=["xlsx", "csv"])
    
    if file_caricato:
        try:
            if file_caricato.name.endswith('.csv'):
                df = pd.read_csv(file_caricato)
            else:
                df = pd.read_excel(file_caricato)
            
            # Trasformiamo il dataframe in un dizionario per l'app
            nuovo_regolamento = dict(zip(df['Azione'], df['Punteggio']))
            dati["regolamento"] = nuovo_regolamento
            salva_dati(dati)
            st.success("✅ Regolamento aggiornato con successo!")
            st.dataframe(df) # Mostra l'anteprima
        except Exception as e:
            st.error(f"Errore nel caricamento: Assicurati che le colonne si chiamino 'Azione' e 'Punteggio'.")

# --- 2. GESTIONE AMICI ---
elif menu == "Gestione Amici":
    st.header("👥 Partecipanti")
    nuovo_amico = st.text_input("Nome nuovo amico:")
    if st.button("Aggiungi"):
        if nuovo_amico and nuovo_amico not in dati["amici"]:
            dati["amici"][nuovo_amico] = 0
            salva_dati(dati)
            st.rerun()
    
    for nome in list(dati["amici"].keys()):
        col1, col2 = st.columns([3, 1])
        col1.write(nome)
        if col2.button("Elimina", key=nome):
            del dati["amici"][nome]
            salva_dati(dati)
            st.rerun()

# --- 3. ASSEGNA PUNTI ---
elif menu == "Assegna Punti":
    st.header("⚡ Bonus e Malus")
    
    if not dati["amici"] or not dati["regolamento"]:
        st.warning("Configura prima gli amici e carica il regolamento Excel!")
    else:
        amico = st.selectbox("Chi?", list(dati["amici"].keys()))
        azione = st.selectbox("Cosa ha fatto?", list(dati["regolamento"].keys()))
        giorno = st.date_input("Quando?")
        
        if st.button("Conferma Punti"):
            punti = dati["regolamento"][azione]
            dati["amici"][amico] += punti
            dati["log"].append(f"{giorno} - {amico}: {punti} pt ({azione})")
            salva_dati(dati)
            st.success(f"Punti assegnati a {amico}!")

# --- 4. CLASSIFICA ---
elif menu == "Classifica":
    st.header("📊 Leaderboard")
    if dati["amici"]:
        classifica = pd.DataFrame(
            list(dati["amici"].items()), 
            columns=["Amico", "Punti"]
        ).sort_values(by="Punti", ascending=False)
        
        # Design classifica
        for i, row in enumerate(classifica.itertuples(), 1):
            st.subheader(f"{i}. {row.Amico} ➔ {row.Punti} pt")
        
        st.divider()
        st.write("📖 Storico eventi:")
        for log in reversed(dati["log"]):
            st.caption(log)
    else:
        st.info("Nessun partecipante ancora iscritto.")
      
