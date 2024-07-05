import pandas as pd
import streamlit as st
import requests
from itertools import cycle

# Liste de proxies à utiliser
proxies = [
    {"http": "http://proxy1.com:port", "https": "https://proxy1.com:port"},
    {"http": "http://proxy2.com:port", "https": "https://proxy2.com:port"},
    {"http": "http://proxy3.com:port", "https": "https://proxy3.com:port"},
]

proxy_pool = cycle(proxies)

def get_complete_url(simplified_url):
    if not isinstance(simplified_url, str):
        return "Invalid URL"
    if not simplified_url.startswith("http://") and not simplified_url.startswith("https://"):
        simplified_url = "https://" + simplified_url
    for i in range(3):  # Essayer jusqu'à 3 fois avec différents proxies
        proxy = next(proxy_pool)
        try:
            response = requests.get(simplified_url, timeout=10, proxies=proxy)
            response.raise_for_status()
            return response.url
        except requests.exceptions.HTTPError as e:
            return f"HTTP Error: {e.response.status_code} for URL: {simplified_url}"
        except requests.RequestException as e:
            return f"Request Exception: {e} for URL: {simplified_url}"
    return f"Error: Could not retrieve URL for {simplified_url}"

def get_url(company_name):
    query = f"{company_name} site officiel"
    try:
        for url in search(query, num_results=1):
            return url
    except Exception as e:
        return f"Error: {str(e)}"
    return "URL non trouvée"

def clean_url(url):
    if not isinstance(url, str):
        return url
    if url.startswith("http://"):
        url = url[len("http://"):]
    elif url.startswith("https://"):
        url = url[len("https://"):]
    if url.endswith('/'):
        url = url[:-1]
    return url

def main():
    st.title('URL Finder for Investment Funds and Start-ups')
    st.write("Upload an Excel file with company names in the first column to retrieve their official websites.")
    
    option = st.radio("Choose the function you want to use:", ('Import to Affinity', 'Import Pitchbook'))

    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

    if uploaded_file is not None:
        # Lire le fichier Excel
        df = pd.read_excel(uploaded_file)
        st.write("File uploaded successfully. Here are the first few rows:")
        st.write(df.head())
        
        if option == 'Import to Affinity':
            # Ajouter une colonne pour les URLs en fonction des noms de sociétés dans la colonne A
            df['URL'] = df.iloc[:, 0].apply(get_url)
            # Nettoyer les URLs pour enlever le schéma
            df['URL'] = df['URL'].apply(clean_url)
            # Renommer les colonnes pour correspondre au template
            df.columns = ['Organization Name', 'Organization Website']
        else:
            # Ajouter une colonne pour les URLs complètes en fonction des URLs simplifiées dans la colonne B
            df['Complete URL'] = df.iloc[:, 1].apply(get_complete_url)
        
        # Afficher les résultats
        st.write("URLs have been fetched. Here are the first few results:")
        st.write(df.head())
        
        # Permettre le téléchargement du fichier avec les URLs ajoutées
        output_file = 'output_with_urls.csv'
        df.to_csv(output_file, index=False)
        
        with open(output_file, "rb") as file:
            btn = st.download_button(
                label="Download updated CSV file",
                data=file,
                file_name=output_file,
                mime="text/csv"
            )

if __name__ == '__main__':
    main()