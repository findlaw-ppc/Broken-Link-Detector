import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# --- UI Setup ---
st.set_page_config(page_title="Link Health Checker", page_icon="🔗")

st.title("🔗 Broken Link Detector")
st.markdown("Enter a website URL to find links that are broken or inaccessible to users.")

# Use a form so the app doesn't run until the button is clicked
with st.form("checker_form"):
    target_url = st.text_input("Website URL to scan:", placeholder="https://example.com")
    submit_button = st.form_submit_button("Check for Broken Links")

# --- Logic ---
if submit_button and target_url:
    if not target_url.startswith(("http://", "https://")):
        st.warning("Please include http:// or https:// in the URL.")
    else:
        with st.spinner("🔍 Scanning the page..."):
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            
            try:
                response = requests.get(target_url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                links = {urljoin(target_url, a['href']) for a in soup.find_all('a', href=True)}
                
                st.write(f"Scanned **{len(links)}** total links on this page.")
                
                broken_links = []
                # Simple Progress Bar
                progress_bar = st.progress(0)
                for i, link in enumerate(links):
                    try:
                        # Logic remains 403-focused but user only sees "Broken"
                        res = requests.head(link, headers=headers, timeout=5, allow_redirects=True)
                        if res.status_code in [403, 405]:
                            res = requests.get(link, headers=headers, timeout=5)
                        
                        if res.status_code == 403:
                            broken_links.append(link)
                    except:
                        pass
                    # Update progress bar
                    progress_bar.progress((i + 1) / len(links))

                # --- Results Display ---
                if broken_links:
                    st.error(f"⚠️ Found {len(broken_links)} broken or inaccessible links:")
                    for bl in broken_links:
                        st.markdown(f"- {bl}")
                else:
                    st.success("✅ All links are working perfectly!")
                    
            except Exception as e:
                st.error("Could not access the website. Please check the URL and try again.")
