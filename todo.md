WHOIS Domain Data Fetcher - MVP Implementation

Overview

A Python server-side application that reads domains from a spreadsheet and fetches WHOIS data including registrar name, registration date, expiry date, and update date.

Files to Create
    app.py - Main Streamlit application with UI
    whois_fetcher.py - Core WHOIS data fetching logic
    requirements.txt - Python dependencies
    utils.py - Utility functions for data processing

Key Features
    Upload spreadsheet (CSV/Excel) with domain list
    Fetch WHOIS data for each domain
    Display results in a structured table
    Export results to CSV
    Error handling for invalid domains

Implementation Strategy
    Use python-whois library for WHOIS queries
    Use pandas for spreadsheet processing
    Use streamlit for web interface
    Implement rate limiting to be respectful to WHOIS servers
    Handle common WHOIS parsing errors gracefully