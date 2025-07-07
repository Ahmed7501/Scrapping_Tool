import streamlit as st
import pandas as pd
import tempfile
import os
from email_scraper.scraper import EmailScraper
import docx
import io
import time

# Configure Streamlit page
st.set_page_config(
    page_title="Bulk Email Scraper",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Increase file size limit to 200MB
# st.set_option('server.maxUploadSize', 200)  # This is now configured in .streamlit/config.toml

def extract_urls_from_txt(file_content):
    """Extract URLs from text file content."""
    return [line.strip() for line in file_content.decode('utf-8').splitlines() if line.strip()]

def extract_urls_from_excel(file_content):
    """Extract URLs from Excel file content."""
    df = pd.read_excel(file_content)
    # Try to find URL column
    url_columns = [col for col in df.columns if 'url' in col.lower()]
    if url_columns:
        return df[url_columns[0]].dropna().tolist()
    # If no URL column found, try to find URLs in all columns
    urls = []
    for col in df.columns:
        urls.extend(df[col].astype(str).str.extract(r'(https?://\S+)')[0].dropna().tolist())
    return list(set(urls))

def extract_urls_from_docx(file_content):
    """Extract URLs from Word document content."""
    doc = docx.Document(io.BytesIO(file_content))
    urls = []
    for paragraph in doc.paragraphs:
        urls.extend([url.strip() for url in paragraph.text.split() if url.startswith(('http://', 'https://'))])
    return list(set(urls))

def process_file(uploaded_file):
    """Process uploaded file and extract URLs."""
    file_content = uploaded_file.read()
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    try:
        if file_extension == 'txt':
            urls = extract_urls_from_txt(file_content)
        elif file_extension in ['xlsx', 'xls']:
            urls = extract_urls_from_excel(file_content)
        elif file_extension == 'docx':
            urls = extract_urls_from_docx(file_content)
        else:
            st.error(f"Unsupported file type: {file_extension}")
            return None
        
        if not urls:
            st.warning("No URLs found in the file.")
            return None
            
        return urls
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

# Main app interface
st.title("Bulk Email Scraper")
st.write("Upload a file containing URLs (supported formats: TXT, Excel, Word)")

# File uploader with multiple file types
uploaded_file = st.file_uploader(
    "Upload your file",
    type=['txt', 'xlsx', 'xls', 'docx'],
    help="Upload a file containing URLs. Supported formats: TXT, Excel (XLSX/XLS), Word (DOCX)"
)

if uploaded_file:
    st.write(f"File uploaded: {uploaded_file.name}")
    
    # Process the file
    urls = process_file(uploaded_file)
    
    if urls:
        st.write(f"Found {len(urls)} URLs in the file")
        
        # Show preview of URLs
        with st.expander("Preview URLs"):
            st.write(urls[:10])
            if len(urls) > 10:
                st.write(f"... and {len(urls) - 10} more URLs")
        
        # Scraping options
        st.write("### Scraping Options")
        col1, col2 = st.columns(2)
        with col1:
            delay = st.slider("Delay between requests (seconds)", 0.1, 2.0, 0.5, 0.1)
        with col2:
            max_concurrent = st.slider("Max concurrent requests", 1, 20, 10, 1)
        
        if st.button("Start Scraping"):
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with st.spinner("Scraping emails. Please wait..."):
                # Create temporary files
                with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
                    tmp.write('\n'.join(urls).encode('utf-8'))
                    tmp_path = tmp.name
                
                output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv").name
                
                # Initialize scraper with custom settings
                scraper = EmailScraper(delay=delay, max_concurrent=max_concurrent)
                
                # Start time
                start_time = time.time()
                
                # Process URLs
                processed_count = scraper.process_urls(tmp_path, output_file)
                
                # Calculate time taken
                time_taken = time.time() - start_time
                
                if processed_count > 0:
                    # Read and display results
                    df = pd.read_csv(output_file)
                    df['emails'] = df['emails'].fillna('').astype(str)
                    
                    # Update progress to 100%
                    progress_bar.progress(100)
                    status_text.text("Scraping complete!")
                    
                    st.success(f"Scraping completed in {time_taken:.1f} seconds!")
                    
                    # Show results in expandable sections
                    with st.expander("View Results", expanded=True):
                        st.dataframe(df)
                    
                    # Download button
                    with open(output_file, "rb") as f:
                        st.download_button(
                            label="Download CSV",
                            data=f,
                            file_name="scraped_emails.csv",
                            mime="text/csv"
                        )
                    
                    # Show enhanced statistics
                    st.write("### 📊 Detailed Statistics")
                    
                    # Calculate statistics
                    total_urls = len(df)
                    successful_scrapes = len(df[df['status'] == 'success'])
                    failed_scrapes = total_urls - successful_scrapes
                    
                    # Count total emails
                    total_emails = 0
                    urls_with_emails = 0
                    for _, row in df.iterrows():
                        if row['emails'] and row['emails'] != '':
                            email_count = len(row['emails'].split(','))
                            total_emails += email_count
                            urls_with_emails += 1
                    
                    # Display statistics in columns
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total URLs", total_urls)
                    
                    with col2:
                        st.metric("Successful Scrapes", successful_scrapes)
                    
                    with col3:
                        st.metric("Total Emails Found", total_emails)
                    
                    with col4:
                        st.metric("URLs with Emails", urls_with_emails)
                    
                    # Show success rate
                    if total_urls > 0:
                        success_rate = (successful_scrapes / total_urls) * 100
                        st.info(f"Success Rate: {success_rate:.1f}%")
                    
                    # Show average emails per URL
                    if urls_with_emails > 0:
                        avg_emails = total_emails / urls_with_emails
                        st.info(f"Average emails per URL (with emails): {avg_emails:.1f}")
                    
                    # Show failed URLs if any
                    if failed_scrapes > 0:
                        with st.expander("Failed URLs"):
                            failed_df = df[df['status'] != 'success']
                            st.dataframe(failed_df[['url', 'status']])
                    
                    # Show top domains with most emails
                    if total_emails > 0:
                        with st.expander("Top Domains by Email Count"):
                            domain_stats = df.groupby('domain').agg({
                                'email_count': 'sum',
                                'url': 'count'
                            }).reset_index()
                            domain_stats.columns = ['Domain', 'Total Emails', 'URLs Scraped']
                            domain_stats = domain_stats.sort_values('Total Emails', ascending=False)
                            st.dataframe(domain_stats.head(10))
                
                # Cleanup temporary files
                os.remove(tmp_path)
                os.remove(output_file) 