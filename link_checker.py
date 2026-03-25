import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def check_links(target_url):
    # We use a User-Agent header to avoid being blocked immediately by basic filters
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Could not access target URL: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    links = set()

    # Extract all 'href' attributes from anchor tags
    for a_tag in soup.find_all('a', href=True):
        link = urljoin(target_url, a_tag['href'])
        links.add(link)

    print(f"Found {len(links)} unique links. Checking for 403 Forbidden errors...\n")

    broken_links = []

    for link in links:
        try:
            # Use a HEAD request first (it's faster as it doesn't download the body)
            res = requests.head(link, headers=headers, timeout=5, allow_redirects=True)
            
            # Some servers block HEAD requests, if so, retry with GET
            if res.status_code == 405 or res.status_code == 403:
                res = requests.get(link, headers=headers, timeout=5)

            if res.status_code == 403:
                print(f"[403 FORBIDDEN] -> {link}")
                broken_links.append(link)
            else:
                # Optional: print success for debugging
                # print(f"[{res.status_code}] OK -> {link}")
                pass

        except requests.exceptions.RequestException:
            print(f"[ERROR] Could not reach -> {link}")

    print("\n--- Scan Complete ---")
    print(f"Total 403 errors found: {len(broken_links)}")

if __name__ == "__main__":
    url_to_scan = input("Enter the URL to scan: ")
    check_links(url_to_scan)
