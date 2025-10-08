import pandas as pd
import streamlit as st
from typing import List, Optional
import io

def read_domains_from_file(uploaded_file) -> Optional[List[str]]:
    """
    Read domains from uploaded file (CSV or Excel)
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        List of domain names or None if error
    """
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload CSV or Excel file.")
            return None
        
        # Try to find domain column
        domain_column = None
        possible_names = ['domain', 'domains', 'website', 'url', 'site', 'Domain', 'Website', 'URL']
        
        for col_name in possible_names:
            if col_name in df.columns:
                domain_column = col_name
                break
        
        if domain_column is None:
            # If no obvious column found, use the first column
            domain_column = df.columns[0]
            st.warning(f"No domain column found. Using first column: '{domain_column}'")
        
        # Extract domains and clean them
        domains = df[domain_column].dropna().astype(str).tolist()
        domains = [domain.strip() for domain in domains if domain.strip()]
        
        return domains
        
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return None

def create_sample_csv() -> str:
    """Create a sample CSV content for download"""
    sample_data = {
        'domain': [
            'google.com',
            'github.com',
            'stackoverflow.com',
            'python.org',
            'streamlit.io'
        ]
    }
    df = pd.DataFrame(sample_data)
    return df.to_csv(index=False)

def format_whois_results(df: pd.DataFrame) -> pd.DataFrame:
    """Format WHOIS results for better display"""
    # Reorder columns for better readability
    column_order = ['domain', 'registrar', 'registration_date', 'expiry_date', 'update_date', 'status', 'error']
    
    # Only include columns that exist in the dataframe
    available_columns = [col for col in column_order if col in df.columns]
    df_formatted = df[available_columns].copy()
    
    # Rename columns for better display
    column_names = {
        'domain': 'Domain',
        'registrar': 'Registrar',
        'registration_date': 'Registration Date',
        'expiry_date': 'Expiry Date',
        'update_date': 'Last Update',
        'status': 'Status',
        'error': 'Error Message'
    }
    
    df_formatted = df_formatted.rename(columns=column_names)
    
    return df_formatted

def convert_df_to_csv(df: pd.DataFrame) -> str:
    """Convert DataFrame to CSV string for download"""
    return df.to_csv(index=False)