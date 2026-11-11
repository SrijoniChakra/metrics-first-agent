import os
import json
import sys
import time
from pathlib import Path
import requests
from dotenv import load_dotenv

# Import your config loader function
from config_loader import load_companies

# Load environment variables from .env
load_dotenv()

SEC_USER_AGENT = os.getenv("SEC_USER_AGENT")
if not SEC_USER_AGENT:
    raise ValueError(
        "SEC_USER_AGENT environment variable is missing. Please define it in your .env file "
        "(format: Sample Company Name AdminContact@domain.com)."
    )

HEADERS = {
    "User-Agent": SEC_USER_AGENT,
    "Accept-Encoding": "gzip, deflate",
}

def fetch_company_facts(cik: str | int, output_dir: str | Path = "data/raw/sec") -> Path:
    cik_str = str(cik).strip()
    padded_cik = cik_str.zfill(10)
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{padded_cik}.json"
    
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    file_path = out_dir / f"{cik_str}.json"

    max_retries = 3
    backoff_factor = 2
    response = None

    for attempt in range(1, max_retries + 1):
        try:
            time.sleep(0.2)  # Rate limiting
            response = requests.get(url, headers=HEADERS, timeout=30)
            
            if response.status_code == 200:
                break
            elif response.status_code == 404:
                raise ValueError(f"CIK {cik_str} returned 404 Not Found from SEC EDGAR.")
            else:
                response.raise_for_status()
                
        except (requests.RequestException, ValueError) as e:
            if attempt == max_retries:
                raise RuntimeError(f"Failed to fetch SEC facts for CIK {cik_str}: {e}")
            time.sleep(backoff_factor ** (attempt - 1))

    if response is None:
        raise RuntimeError(f"Failed to retrieve data for CIK {cik_str}.")

    raw_data = response.json()
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=2)

    print(f"Successfully fetched and saved CIK {cik_str} -> {file_path}")
    return file_path


if __name__ == "__main__":
    # Pull config data from YAML
    config_path = Path("config/companies.yml")
    # Extract the list of companies/CIKs
    company_list = load_companies(config_path)
    print(company_list)
    
    if not company_list:
        print("No companies found in config/companies.yml")
    
    for company in company_list:
        ciks = company.ciks
        name = company.name
        for cik_spec in ciks:
            # Access the cik attribute directly using dot notation
            cik = cik_spec.cik  
            
            if cik:
                print(f"Processing {name} (CIK: {cik}, FY From: {cik_spec.fiscal_year_from}, FY To: {cik_spec.fiscal_year_to})...")
                try:
                    fetch_company_facts(cik)
                except Exception as e:
                    print(f"Error processing {name} (CIK {cik}): {e}", file=sys.stderr)
       