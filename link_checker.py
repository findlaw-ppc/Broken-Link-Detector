import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# --- UI Setup ---
st.set_page_config(page_title="Broken Link Detector", page_icon="🔍")
st.title("🔍 Forbidden Link Finder")
st.markdown("Enter a website URL below to scan for **403 Forbidden** errors.")

target_url = st.text_input("Target URL", placeholder="https://example.com")
scan_button = st.button("Run Scan")

# --- Logic ---
if scan_button and target_url:
    with st.spinner("Scanning links... please wait."):
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        
        try:
            response = requests.get(target_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            links = {urljoin(target_url, a['href']) for a in soup.find_all('a', href=True)}
            
            st.info(f"Found {len(links)} unique links. Checking status codes...")
            
            broken_links = []
            for link in links:
                try:
                    res = requests.head(link, headers=headers, timeout=5, allow_redirects=True)
                    if res.status_code in [403, 405]:
                        res = requests.get(link, headers=headers, timeout=5)
                    
                    if res.status_code == 403:
                        broken_links.append(link)
                except:
                    continue

            # --- Results Display ---
            if broken_links:
                st.error(f"Found {len(broken_links)} Forbidden (403) links:")
                for bl in broken_links:
                    st.write(f"❌ {bl}")
            else:
                st.success("No 403 errors found! All links are accessible.")
                
        except Exception as e:
            st.error(f"Error accessing the site: {e}")
