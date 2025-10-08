import time
import random
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import pandas as pd
import requests
import whois  # fallback
from datetime import datetime
import streamlit as st
from typing import Dict, List, Optional

# ----------------- CONFIG -----------------
MAX_THREADS = 5                    # concurrency (keep modest)
RDAP_TIMEOUT = 10                  # seconds for RDAP/HTTP requests
RETRIES = 3
INITIAL_BACKOFF = 1.0              # seconds
MAX_BACKOFF = 8.0
WHOIS_API_KEY = ""                 # Optional: set your paid WHOIS API key if you have one
WHOIS_API_URL = "https://example-whois-api.com/v1/whois"  # placeholder - change if using paid API
# ------------------------------------------

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; WhoisFetcher/1.0; +https://yourdomain.example/)"
}

class AdvancedWHOISFetcher:
    def __init__(self, max_threads=5, api_key=""):
        self.max_threads = max_threads
        self.api_key = api_key
        self.results = []
        
    def exponential_backoff_sleep(self, attempt):
        """Sleep with exponential backoff + jitter."""
        backoff = min(MAX_BACKOFF, INITIAL_BACKOFF * (2 ** attempt))
        jitter = random.uniform(0, backoff * 0.2)
        time.sleep(backoff + jitter)

    def parse_rdap_date(self, datestr):
        if not datestr:
            return None
        try:
            return datetime.fromisoformat(datestr.replace("Z", "")).strftime("%Y-%m-%d")
        except Exception:
            return datestr[:10]  # fallback

    def extract_vcard_name(self, vcard_array):
        """Extract readable org name from RDAP vcard array."""
        try:
            if isinstance(vcard_array, list):
                for item in vcard_array:
                    if isinstance(item, list):
                        for sub in item:
                            if isinstance(sub, list) and sub[0] == "fn":
                                return sub[3] or None
        except Exception:
            pass
        return None

    def rdap_lookup(self, domain):
        url = f"https://rdap.org/domain/{domain}"
        resp = requests.get(url, headers=HEADERS, timeout=RDAP_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        registrar = None
        creation = None
        expiration = None
        updated = None

        # Extract events
        for ev in data.get("events", []):
            ev_type = ev.get("eventAction", "").lower()
            ev_date = ev.get("eventDate") or ev.get("timestamp")
            if not ev_date:
                continue
            date_parsed = self.parse_rdap_date(ev_date)
            if ev_type in ("registration", "create", "registered"):
                creation = creation or date_parsed
            elif ev_type in ("expiration", "expiry", "expire"):
                expiration = expiration or date_parsed
            elif ev_type in ("last changed", "update", "modified"):
                updated = updated or date_parsed

        # Extract registrar
        for ent in data.get("entities", []):
            roles = ent.get("roles", [])
            if any("registrar" in r.lower() for r in roles):
                vcard = ent.get("vcardArray")
                name = self.extract_vcard_name(vcard)
                if name:
                    registrar = name
                    break

        return {
            "Domain": domain,
            "Registrar": registrar,
            "Creation Date": creation,
            "Expiration Date": expiration,
            "Updated Date": updated,
            "Source": "RDAP",
            "Error": None
        }

    def whois_api_lookup(self, domain, api_key):
        """
        Placeholder for paid WHOIS API lookup.
        You must replace WHOIS_API_URL with real API endpoint and parse its JSON response.
        """
        params = {"domain": domain, "apiKey": api_key}
        resp = requests.get(WHOIS_API_URL, params=params, headers=HEADERS, timeout=RDAP_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        # Example parsing - depends on API provider
        registrar = data.get("registrarName") or data.get("registrar")
        creation = data.get("createdDate") or data.get("created_at") or data.get("creationDate")
        expiration = data.get("expiresDate") or data.get("expires_at") or data.get("expirationDate")
        updated = data.get("updatedDate") or data.get("updated_at")
        return {
            "Domain": domain,
            "Registrar": registrar,
            "Creation Date": creation,
            "Expiration Date": expiration,
            "Updated Date": updated,
            "Source": "WHOIS_API",
            "Error": None
        }

    def python_whois_lookup(self, domain):
        w = whois.whois(domain)

        def first_date(d):
            if isinstance(d, list):
                for x in d:
                    if x:
                        try:
                            return x.strftime('%Y-%m-%d')
                        except Exception:
                            return str(x)[:10]
            elif d:
                try:
                    return d.strftime('%Y-%m-%d')
                except Exception:
                    return str(d)[:10]
            return None

        return {
            "Domain": domain,
            "Registrar": getattr(w, "registrar", None),
            "Creation Date": first_date(getattr(w, "creation_date", None)),
            "Expiration Date": first_date(getattr(w, "expiration_date", None)),
            "Updated Date": first_date(getattr(w, "updated_date", None)),
            "Source": "WHOIS_PORT43",
            "Error": None
        }

    def fetch_domain_with_backoff(self, domain):
        """
        Attempt to fetch WHOIS info using:
        1) Paid WHOIS API (if configured),
        2) RDAP (HTTP JSON),
        3) python-whois fallback (port 43).
        Uses retries + exponential backoff.
        """
        # Clean domain name
        domain = domain.strip().lower()
        if domain.startswith('http://') or domain.startswith('https://'):
            domain = domain.split('/')[2]
        if domain.startswith('www.'):
            domain = domain[4:]
            
        # Try paid API first if configured
        if self.api_key:
            for attempt in range(RETRIES):
                try:
                    return self.whois_api_lookup(domain, self.api_key)
                except Exception:
                    if attempt < RETRIES - 1:
                        self.exponential_backoff_sleep(attempt)
                    else:
                        # fallthrough to RDAP
                        break

        # Try RDAP next
        for attempt in range(RETRIES):
            try:
                return self.rdap_lookup(domain)
            except Exception:
                if attempt < RETRIES - 1:
                    self.exponential_backoff_sleep(attempt)
                else:
                    # fallthrough to python-whois
                    break

        # Final fallback: python-whois (may be blocked/rate-limited)
        for attempt in range(RETRIES):
            try:
                res = self.python_whois_lookup(domain)
                # optional small sleep to be polite to port43 servers
                time.sleep(0.2 + random.uniform(0, 0.3))
                return res
            except Exception:
                if attempt < RETRIES - 1:
                    self.exponential_backoff_sleep(attempt)
                else:
                    return {
                        "Domain": domain,
                        "Registrar": None,
                        "Creation Date": None,
                        "Expiration Date": None,
                        "Updated Date": None,
                        "Source": "FAILED",
                        "Error": "All methods failed"
                    }

    def fetch_multiple_domains_advanced(self, domains: List[str], progress_callback=None) -> pd.DataFrame:
        """
        Fetch WHOIS data for multiple domains using advanced concurrent approach
        """
        if not domains:
            return pd.DataFrame()

        max_threads = min(self.max_threads, len(domains))
        results = []

        # Submit tasks with progress tracking
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = {executor.submit(self.fetch_domain_with_backoff, d): d for d in domains}
            
            completed = 0
            for future in as_completed(futures):
                try:
                    res = future.result()
                except Exception as e:
                    # Shouldn't happen due to internal error handling, but capture anyway
                    res = {
                        "Domain": futures.get(future, "unknown"),
                        "Registrar": None,
                        "Creation Date": None,
                        "Expiration Date": None,
                        "Updated Date": None,
                        "Source": "EXCEPTION",
                        "Error": str(e)
                    }
                
                results.append(res)
                completed += 1
                
                # Update progress if callback provided
                if progress_callback:
                    progress_callback(completed, len(domains), res['Domain'])

        return pd.DataFrame(results)


