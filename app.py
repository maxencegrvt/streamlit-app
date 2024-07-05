import streamlit as st
import pandas as pd
import requests

def get_complete_url(simplified_url):
    proxies = [
        {"http": "http://45.77.58.38:8080", "https": "https://45.77.58.38:8080"},
        {"http": "http://51.79.50.31:9300", "https": "https://51.79.50.31:9300"},
        {"http": "http://139.99.237.62:80", "https": "https://139.99.237.62:80"},
        {"http": "http://45.77.201.37:8080", "https": "https://45.77.201.37:8080"},
        {"http": "http://51.81.82.175:8888", "https": "https://51.81.82.175:8888"}
    ]

    if not isinstance(simplified_url, str):
        return "Invalid URL"
    if not simplified_url.startswith("http://") and not simplified_url.startswith("https://"):
        simplified_url = "https://" + simplified_url

    for proxy in proxies:
        try:
            response = requests.get(simplified_url, timeout=10, proxies=proxy)
            response.raise_for_status()
            return response.url
        except requests.exceptions.HTTPError as e:
            continue
        except requests.RequestException as e:
            continue

    return f"Error: Could not retrieve URL for {simplified_url}"

def main():
    st.title("URL Finder for Investment Funds and Start-ups")
    
    option = st.radio(
        "Choose the function you want to use:",
        ('Import to Affinity', 'Import Pitchbook')
    )

    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.write("File uploaded successfully. Here are the first few rows:")
        st.write(df.head())

        if option == 'Import Pitchbook':
            df['Complete URL'] = df.iloc[:, 1].apply(get_complete_url)
            st.write("URLs have been fetched. Here are the first few results:")
            st.write(df.head())

            output_file = "output_with_urls.xlsx"
            df.to_csv(output_file, index=False, sep=",")
            
            with open(output_file, "rb") as file:
                btn = st.download_button(
                    label="Download updated CSV file",
                    data=file,
                    file_name=output_file,
                    mime="text/csv"
                )

if __name__ == "__main__":
    main()