import pandas as pd
from googlesearch import search
import streamlit as st
import os
import re

def get_url(company_name):
    query = f"{company_name} site officiel"
    try:
        for url in search(query, num_results=1):
            return url
    except Exception as e:
        return f"Error: {str(e)}"
    return "URL non trouvée"

def clean_url(url):
    # Enlever les schémas http:// et https://
    url = re.sub(r'^https?://', '', url)
    # Enlever les préfixes www.
    url = re.sub(r'^www\.', '', url)
    # Supprimer tout ce qui se trouve après le premier /
    url = url.split('/')[0]
    return url

def complete_url(simplified_url):
    if pd.isna(simplified_url):
        return ""
    if not simplified_url.startswith("http://") and not simplified_url.startswith("https://"):
        return "http://" + simplified_url
    return simplified_url

def get_complete_url(simplified_url):
    full_url = complete_url(simplified_url)
    try:
        query = f"{simplified_url}"
        search_result = list(search(query, num_results=1))
        if search_result:
            return search_result[0]
        else:
            return full_url
    except Exception as e:
        return f"Error: {str(e)}"

st.title('URL Finder for Investment Funds and Start-ups')
st.write("Upload an Excel file with company names in the first column to retrieve their official websites.")

option = st.radio(
    "Choose the function you want to use:",
    ('Retrieve URLs', 'Complete URLs')
)

uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    # Lire le fichier Excel
    df = pd.read_excel(uploaded_file)
    st.write("File uploaded successfully. Here are the first few rows:")
    st.write(df.head())

    if option == 'Retrieve URLs':
        # Ajouter une colonne pour les URLs en fonction des noms de sociétés dans la colonne A
        st.write("Fetching URLs for each company name...")
        df['URL'] = df.iloc[:, 0].apply(get_url)

        # Nettoyer les URLs pour enlever le schéma, le 'www.' et tout ce qui suit le premier '/'
        df['URL'] = df['URL'].apply(clean_url)

        # Renommer les colonnes pour correspondre au template
        df.columns = ['Organization Name', 'Organization Website']
        
    elif option == 'Complete URLs':
        # Compléter les URLs dans la colonne B et ajouter une nouvelle colonne pour les URLs complètes
        st.write("Completing URLs for each simplified URL...")
        df['Complete URL'] = df.iloc[:, 1].apply(get_complete_url)
        
        # Renommer les colonnes si nécessaire (ajustez en fonction de votre template)
        # df.columns = ['Organization Name', 'Simplified Website', 'Complete Website']

    # Afficher les résultats
    st.write("Here are the first few results:")
    st.write(df.head())

    # Permettre le téléchargement du fichier avec les résultats ajoutés
    output_file = 'output_with_urls.xlsx' if option == 'Retrieve URLs' else 'output_with_complete_urls.xlsx'
    df.to_excel(output_file, index=False)

    with open(output_file, "rb") as file:
        btn = st.download_button(
            label="Download updated Excel file",
            data=file,
            file_name=output_file,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )