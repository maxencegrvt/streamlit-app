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

st.title('URL Finder for Investment Funds and Start-ups')
st.write("Upload an Excel file with company names in the first column to retrieve their official websites.")

uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    # Lire le fichier Excel
    df = pd.read_excel(uploaded_file)
    st.write("File uploaded successfully. Here are the first few rows:")
    st.write(df.head())
    
    # Ajouter une colonne pour les URLs en fonction des noms de sociétés dans la colonne A
    st.write("Fetching URLs for each company name...")
    df['URL'] = df.iloc[:, 0].apply(get_url)
    
    # Nettoyer les URLs pour enlever le schéma, le 'www.' et tout ce qui suit le premier '/'
    df['URL'] = df['URL'].apply(clean_url)
    
    # Renommer les colonnes pour correspondre au template
    df.columns = ['Organization Name', 'Organization Website']
    
    # Afficher les résultats
    st.write("URLs have been fetched. Here are the first few results:")
    st.write(df.head())
    
    # Permettre le téléchargement du fichier avec les URLs ajoutées
    output_file = 'output_with_urls.csv'
    df.to_csv(output_file, index=False, sep=',')
    
    with open(output_file, "rb") as file:
        btn = st.download_button(
            label="Download updated CSV file",
            data=file,
            file_name=output_file,
            mime="text/csv"
        )