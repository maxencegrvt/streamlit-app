import streamlit as st
import pandas as pd
from googlesearch import search
import requests
from bs4 import BeautifulSoup

# Function to clean the URL
def clean_url(url):
    if isinstance(url, str):
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        return url.rstrip('/')
    return url

# Function to search on Google
def search_google(query):
    try:
        for url in search(query, num_results=1, stop=1):
            return url
    except Exception as e:
        return f"Error: {str(e)}"

# Function to search on Bing
def search_bing(query):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(f"https://www.bing.com/search?q={query}", headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all('li', {'class': 'b_algo'})
        if results:
            return results[0].find('a')['href']
    except Exception as e:
        return f"Error: {str(e)}"

# Function to search on DuckDuckGo
def search_duckduckgo(query):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(f"https://duckduckgo.com/html/?q={query}", headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all('a', {'class': 'result__a'})
        if results:
            return results[0]['href']
    except Exception as e:
        return f"Error: {str(e)}"

# Function to get the complete URL
def get_complete_url(simplified_url):
    if not isinstance(simplified_url, str):
        return "Invalid URL"
    full_url = clean_url(simplified_url)
    query = f"{simplified_url}"

    # Try Google first
    url = search_google(query)
    if url and "Error" not in url:
        return url

    # If Google fails, try Bing
    url = search_bing(query)
    if url and "Error" not in url:
        return url

    # If Bing fails, try DuckDuckGo
    url = search_duckduckgo(query)
    if url and "Error" not in url:
        return url

    # If all fail, return the simplified URL
    return full_url

# Main function for Streamlit
def main():
    st.title('URL Finder for Investment Funds and Start-ups')
    st.write("Upload an Excel file with company names in the first column to retrieve their official websites.")

    # Function choice
    function_choice = st.radio(
        "Choose the function you want to use:",
        ('Import to Affinity', 'Import Pitchbook')
    )

    # File upload
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.write("File uploaded successfully. Here are the first few rows:")
        st.write(df.head())

        if function_choice == 'Import to Affinity':
            # Processing for Import to Affinity
            df['URL'] = df.iloc[:, 0].apply(get_complete_url)
            df['URL'] = df['URL'].apply(clean_url)
            df.columns = ['Organization Name', 'Organization Website']
            st.write("URLs have been fetched. Here are the first few results:")
            st.write(df.head())
            output_file = 'output_with_urls.csv'
            df.to_csv(output_file, index=False, sep=',')
            with open(output_file, "rb") as file:
                btn = st.download_button(
                    label="Download updated CSV file",
                    data=file,
                    file_name=output_file,
                    mime="text/csv"
                )

        elif function_choice == 'Import Pitchbook':
            # Processing for Import Pitchbook
            if 'Website' in df.columns:
                df['Complete URL'] = df['Website'].apply(lambda x: get_complete_url(x) if isinstance(x, str) else "Invalid URL")
                st.write("Completing URLs for each simplified URL...")
                st.write(df.head())
                output_file = 'completed_urls.csv'
                df.to_csv(output_file, index=False, sep=',')
                with open(output_file, "rb") as file:
                    btn = st.download_button(
                        label="Download completed URLs CSV file",
                        data=file,
                        file_name=output_file,
                        mime="text/csv"
                    )
            else:
                st.error("The uploaded file does not contain a 'Website' column.")

if __name__ == '__main__':
    main()
