import whois
import pandas as pd
from datetime import datetime
import time
import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WHOISFetcher:
    def __init__(self, delay: float = 1.0):
        """
        Initialize WHOIS fetcher with rate limiting
        
        Args:
            delay: Delay between requests in seconds to be respectful to WHOIS servers
        """
        self.delay = delay
    
    def fetch_domain_whois(self, domain: str) -> Dict:
        """
        Fetch WHOIS data for a single domain
        
        Args:
            domain: Domain name to query
            
        Returns:
            Dictionary containing WHOIS data
        """
        try:
            # Clean domain name
            domain = domain.strip().lower()
            if domain.startswith('http://') or domain.startswith('https://'):
                domain = domain.split('/')[2]
            if domain.startswith('www.'):
                domain = domain[4:]
            
            logger.info(f"Fetching WHOIS data for: {domain}")
            
            # Fetch WHOIS data
            w = whois.whois(domain)
            
            # Extract relevant information
            result = {
                'domain': domain,
                'registrar': self._extract_registrar(w),
                'registration_date': self._extract_date(w.creation_date),
                'expiry_date': self._extract_date(w.expiration_date),
                'update_date': self._extract_date(w.updated_date),
                'status': 'Success',
                'error': None
            }
            
            # Add rate limiting delay
            time.sleep(self.delay)
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching WHOIS for {domain}: {str(e)}")
            return {
                'domain': domain,
                'registrar': None,
                'registration_date': None,
                'expiry_date': None,
                'update_date': None,
                'status': 'Error',
                'error': str(e)
            }
    
    def _extract_registrar(self, whois_data) -> Optional[str]:
        """Extract registrar name from WHOIS data"""
        if hasattr(whois_data, 'registrar') and whois_data.registrar:
            if isinstance(whois_data.registrar, list):
                return whois_data.registrar[0] if whois_data.registrar else None
            return str(whois_data.registrar)
        return None
    
    def _extract_date(self, date_field) -> Optional[str]:
        """Extract and format date from WHOIS data"""
        if not date_field:
            return None
        
        try:
            if isinstance(date_field, list):
                date_field = date_field[0] if date_field else None
            
            if isinstance(date_field, datetime):
                return date_field.strftime('%Y-%m-%d')
            elif isinstance(date_field, str):
                # Try to parse string date
                try:
                    parsed_date = datetime.strptime(date_field, '%Y-%m-%d')
                    return parsed_date.strftime('%Y-%m-%d')
                except:
                    return date_field
            
        except Exception as e:
            logger.warning(f"Error parsing date {date_field}: {str(e)}")
        
        return None
    
    def fetch_multiple_domains(self, domains: List[str]) -> pd.DataFrame:
        """
        Fetch WHOIS data for multiple domains
        
        Args:
            domains: List of domain names
            
        Returns:
            DataFrame containing WHOIS data for all domains
        """
        results = []
        total_domains = len(domains)
        
        for i, domain in enumerate(domains, 1):
            logger.info(f"Processing domain {i}/{total_domains}: {domain}")
            result = self.fetch_domain_whois(domain)
            results.append(result)
        
        return pd.DataFrame(results)