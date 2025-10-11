import streamlit as st
import pandas as pd
import time
import io
from advanced_whois_fetcher import AdvancedWHOISFetcher
from utils import read_domains_from_file, create_sample_csv, format_whois_results, convert_df_to_csv
import base64

# Page configuration
st.set_page_config(
    page_title="WHOIS Domain Lookup Pro",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional UI with glassmorphism
def load_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sticky Header */
    .sticky-header {
        position: sticky;
        top: 0;
        z-index: 999;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    
    /* Main Container */
    .main-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
    }
    
    /* Card Components */
    .glass-card {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(31, 38, 135, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(31, 38, 135, 0.3);
    }
    
    /* Typography */
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        color: white;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.8);
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: white;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .step-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: white;
        margin-bottom: 1rem;
    }
    
    /* Step Indicator */
    .step-indicator {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 2rem 0;
        gap: 1rem;
    }
    
    .step {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: rgba(255, 255, 255, 0.7);
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .step.active {
        background: rgba(255, 255, 255, 0.2);
        color: white;
        border-color: rgba(255, 255, 255, 0.4);
        box-shadow: 0 4px 16px rgba(255, 255, 255, 0.1);
    }
    
    .step.completed {
        background: rgba(34, 197, 94, 0.2);
        color: #22c55e;
        border-color: rgba(34, 197, 94, 0.4);
    }
    
    /* Upload Area */
    .upload-area {
        border: 2px dashed rgba(255, 255, 255, 0.3);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        background: rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .upload-area:hover {
        border-color: rgba(255, 255, 255, 0.5);
        background: rgba(255, 255, 255, 0.1);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Metrics */
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: white;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.7);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Data Table */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Status Badges */
    .status-success {
        background: rgba(34, 197, 94, 0.2);
        color: #22c55e;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    
    .status-error {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    /* Info Cards */
    .info-card {
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 10px;
        padding: 1rem;
        color: rgba(255, 255, 255, 0.9);
    }
    
    .warning-card {
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid rgba(245, 158, 11, 0.2);
        border-radius: 10px;
        padding: 1rem;
        color: rgba(255, 255, 255, 0.9);
    }
    
    .success-card {
        background: rgba(34, 197, 94, 0.1);
        border: 1px solid rgba(34, 197, 94, 0.2);
        border-radius: 10px;
        padding: 1rem;
        color: rgba(255, 255, 255, 0.9);
    }
    
    /* Animation */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        
        .step-indicator {
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .glass-card {
            padding: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """Render sticky header"""
    st.markdown("""
    <div class="sticky-header">
        <div class="main-title">WHOIS Domain Lookup</div>
        <div class="subtitle">This tool is built by Tafseer Alam for bulk domain analysis with advanced WHOIS data extraction.</div>
    </div>
    """, unsafe_allow_html=True)

def render_step_indicator(current_step):
    """Render step indicator"""
    steps = [
        ("📁", "Upload", 1),
        ("⚡", "Processing", 2),
        ("📊", "Results", 3)
    ]
    
    step_html = '<div class="step-indicator">'
    
    for icon, label, step_num in steps:
        if step_num < current_step:
            class_name = "step completed"
        elif step_num == current_step:
            class_name = "step active"
        else:
            class_name = "step"
        
        step_html += f'<div class="{class_name}"><span>{icon}</span> {label}</div>'
        
        if step_num < len(steps):
            step_html += '<div style="width: 2rem; height: 2px; background: rgba(255,255,255,0.2); margin: 0 1rem;"></div>'
    
    step_html += '</div>'
    st.markdown(step_html, unsafe_allow_html=True)

def render_upload_section():
    """Render file upload section with drag & drop"""
    st.markdown('<div class="main-container fade-in-up">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📁 Upload Domain Files</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose your domain file",
            type=['txt', 'csv', 'xlsx', 'xls'],
            help="Supported formats: TXT, CSV, Excel (.xlsx, .xls)",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            st.markdown('<div class="success-card">', unsafe_allow_html=True)
            st.markdown(f"✅ **File uploaded:** {uploaded_file.name}")
            st.markdown(f"📏 **Size:** {uploaded_file.size:,} bytes")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="upload-area">
                <h3>📤 Drag & Drop Your File Here</h3>
                <p>Or click to browse and select your domain file</p>
                <small>Supports: .txt, .csv, .xlsx, .xls</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="step-title">📋 File Requirements</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
            Supported Formats:<br>
            • Plain text (.txt)<br>
            • CSV files (.csv)<br>
            • Excel files (.xlsx, .xls)
            
            Domain Format:
            • One domain per line(Row)
            • With or without www.
            • With or without http(s)://
        </div>
        """, unsafe_allow_html=True)
        
        # Sample file download
        sample_csv = create_sample_csv()
        st.download_button(
            label="📥 Download File",
            data=sample_csv,
            file_name="domains.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return uploaded_file

def render_configuration_section():
    """Render advanced configuration"""
    st.markdown('<div class="main-container fade-in-up">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚙️ Advanced Configuration</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="step-title">🔧 Processing Settings</div>', unsafe_allow_html=True)
        
        max_threads = st.slider(
            "Concurrent Threads",
            min_value=1,
            max_value=10,
            value=5,
            help="Number of simultaneous WHOIS requests"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="step-title">🔑 API Configuration</div>', unsafe_allow_html=True)
        
        api_key = st.text_input(
            "WHOIS API Key (Optional)",
            type="password",
            help="Enter your premium WHOIS API key for higher success rates"
        )
        
        if api_key:
            st.markdown('<div class="success-card">✅ API Key configured</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return max_threads, api_key

def render_processing_section(domains, max_threads, api_key):
    """Render processing section with real-time progress"""
    st.markdown('<div class="main-container fade-in-up">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚡ Processing Domains</div>', unsafe_allow_html=True)
    
    # Processing stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Total Domains</div>
        </div>
        """.format(len(domains)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Max Threads</div>
        </div>
        """.format(max_threads), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">API Status</div>
        </div>
        """.format("Premium" if api_key else "Free"), unsafe_allow_html=True)
    
    with col4:
        estimated_time = len(domains) * 2 / max_threads  # Rough estimate
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">~{}m</div>
            <div class="metric-label">Est. Time</div>
        </div>
        """.format(int(estimated_time)), unsafe_allow_html=True)
    
    # Progress tracking
    progress_container = st.container()
    status_container = st.container()
    
    # Initialize fetcher
    fetcher = AdvancedWHOISFetcher(max_threads=max_threads, api_key=api_key)
    
    # Progress tracking variables
    progress_bar = progress_container.progress(0)
    status_text = status_container.empty()
    
    try:
        start_time = time.time()
        
        def update_progress(completed, total, current_domain):
            progress = completed / total
            progress_bar.progress(progress)
            
            elapsed = time.time() - start_time
            eta = (elapsed / completed * total - elapsed) if completed > 0 else 0
            
            status_text.markdown(f"""
            <div class="glass-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>Processing:</strong> {current_domain}<br>
                        <strong>Progress:</strong> {completed}/{total} ({progress:.1%})
                    </div>
                    <div style="text-align: right;">
                        <strong>Elapsed:</strong> {elapsed:.1f}s<br>
                        <strong>ETA:</strong> {eta:.1f}s
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Process domains
        df_results = fetcher.fetch_multiple_domains_advanced(domains, update_progress)
        
        processing_time = time.time() - start_time
        
        status_text.markdown(f"""
        <div class="success-card">
            ✅ <strong>Processing Complete!</strong><br>
            Processed {len(domains)} domains in {processing_time:.1f} seconds
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return df_results, processing_time
        
    except Exception as e:
        status_text.markdown(f"""
        <div class="status-error">
            ❌ <strong>Processing Failed:</strong> {str(e)}
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return None, 0

def render_results_section(df_results, processing_time):
    """Render results section with advanced table features"""
    st.markdown('<div class="main-container fade-in-up">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 WHOIS Results</div>', unsafe_allow_html=True)
    
    if df_results is None or df_results.empty:
        st.markdown('<div class="warning-card">⚠️ No results to display</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Results summary
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_domains = len(df_results)
    rdap_success = len(df_results[df_results['Source'] == 'RDAP'])
    api_success = len(df_results[df_results['Source'] == 'WHOIS_API'])
    whois_success = len(df_results[df_results['Source'] == 'WHOIS_PORT43'])
    failed = len(df_results[df_results['Source'] == 'FAILED'])
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_domains}</div>
            <div class="metric-label">Total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{rdap_success}</div>
            <div class="metric-label">RDAP</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{api_success}</div>
            <div class="metric-label">API</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{whois_success}</div>
            <div class="metric-label">WHOIS</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{failed}</div>
            <div class="metric-label">Failed</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Search and filter controls
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">🔍 Search & Filter</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("🔍 Search domains", placeholder="Enter domain name...")
    
    with col2:
        source_filter = st.selectbox("📡 Filter by source", 
                                   options=["All"] + list(df_results['Source'].unique()))
    
    with col3:
        status_filter = st.selectbox("📊 Filter by status",
                                   options=["All", "Success", "Failed"])
    
    # Apply filters
    filtered_df = df_results.copy()
    
    if search_term:
        filtered_df = filtered_df[filtered_df['Domain'].str.contains(search_term, case=False, na=False)]
    
    if source_filter != "All":
        filtered_df = filtered_df[filtered_df['Source'] == source_filter]
    
    if status_filter == "Success":
        filtered_df = filtered_df[filtered_df['Source'] != 'FAILED']
    elif status_filter == "Failed":
        filtered_df = filtered_df[filtered_df['Source'] == 'FAILED']
    
    st.markdown(f"**Showing {len(filtered_df)} of {len(df_results)} results**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Results table
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    if not filtered_df.empty:
        # Format the dataframe for display
        display_df = filtered_df.copy()
        
        # Add status badges (simplified for Streamlit)
        display_df['Status'] = display_df['Source'].apply(
            lambda x: "✅ Success" if x != 'FAILED' else "❌ Failed"
        )
        
        # Reorder columns
        column_order = ['Domain', 'Registrar', 'Creation Date', 'Expiration Date', 'Updated Date', 'Source', 'Status']
        display_df = display_df[[col for col in column_order if col in display_df.columns]]
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Domain": st.column_config.TextColumn("🌐 Domain", width="medium"),
                "Registrar": st.column_config.TextColumn("🏢 Registrar", width="medium"),
                "Creation Date": st.column_config.DateColumn("📅 Created", width="small"),
                "Expiration Date": st.column_config.DateColumn("⏰ Expires", width="small"),
                "Updated Date": st.column_config.DateColumn("🔄 Updated", width="small"),
                "Source": st.column_config.TextColumn("📡 Source", width="small"),
                "Status": st.column_config.TextColumn("📊 Status", width="small")
            }
        )
    else:
        st.markdown('<div class="warning-card">⚠️ No results match your filters</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Export options
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">📥 Export Results</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv_data = convert_df_to_csv(filtered_df)
        st.download_button(
            label="📄 Download CSV",
            data=csv_data,
            file_name=f"whois_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Excel export would require additional libraries
        st.button("📊 Export Excel", disabled=True, help="Excel export coming soon", use_container_width=True)
    
    with col3:
        # JSON export
        json_data = filtered_df.to_json(orient='records', indent=2)
        st.download_button(
            label="📋 Download JSON",
            data=json_data,
            file_name=f"whois_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Method distribution chart
    if not df_results.empty:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="step-title">📈 Data Source Distribution</div>', unsafe_allow_html=True)
        
        source_counts = df_results['Source'].value_counts()
        st.bar_chart(source_counts, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application function"""
    load_css()
    render_header()
    
    # Initialize session state
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    if 'domains' not in st.session_state:
        st.session_state.domains = None
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'processing_time' not in st.session_state:
        st.session_state.processing_time = 0
    
    # Render step indicator
    render_step_indicator(st.session_state.current_step)
    
    # Step 1: Upload
    if st.session_state.current_step == 1:
        uploaded_file = render_upload_section()
        
        if uploaded_file is not None:
            domains = read_domains_from_file(uploaded_file)
            
            if domains:
                st.session_state.domains = domains
                
                # Show domain preview
                st.markdown('<div class="main-container fade-in-up">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">👀 Domain Preview</div>', unsafe_allow_html=True)
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                
                preview_df = pd.DataFrame({'Domain': domains[:10]})
                st.dataframe(preview_df, use_container_width=True, hide_index=True)
                
                if len(domains) > 10:
                    st.markdown(f'<div class="info-card">Showing first 10 domains. Total: {len(domains)}</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                if st.button("➡️ Continue to Configuration", type="primary", use_container_width=True):
                    st.session_state.current_step = 2
                    st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 2: Configuration and Processing
    elif st.session_state.current_step == 2:
        max_threads, api_key = render_configuration_section()
        
        if st.button("🚀 Start Processing", type="primary", use_container_width=True):
            st.session_state.current_step = 2.5  # Processing state
            st.rerun()
        
        # Back button
        if st.button("⬅️ Back to Upload"):
            st.session_state.current_step = 1
            st.rerun()
    
    # Step 2.5: Processing
    elif st.session_state.current_step == 2.5:
        max_threads = 5  # Default value during processing
        api_key = ""    # Default value during processing
        
        results, processing_time = render_processing_section(
            st.session_state.domains, max_threads, api_key
        )
        
        if results is not None:
            st.session_state.results = results
            st.session_state.processing_time = processing_time
            st.session_state.current_step = 3
            time.sleep(2)  # Brief pause to show completion
            st.rerun()
    
    # Step 3: Results
    elif st.session_state.current_step == 3:
        render_results_section(st.session_state.results, st.session_state.processing_time)
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Process New Domains", use_container_width=True):
                # Reset session state
                st.session_state.current_step = 1
                st.session_state.domains = None
                st.session_state.results = None
                st.session_state.processing_time = 0
                st.rerun()
        
        with col2:
            if st.button("⚙️ Reconfigure Settings", use_container_width=True):
                st.session_state.current_step = 2
                st.rerun()

    # --- Sticky Footer ---
st.markdown("""
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #0e1117; /* matches Streamlit dark theme */
        color: white;
        text-align: center;
        padding: 10px 0;
        font-size: 15px;
        border-top: 1px solid #333;
    }
    </style>

    <div class="footer">
        Made with ❤️ by <b>Tafseer Alam</b>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    /* Hide the empty main container */
    .main-container.fade-in-up {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()

