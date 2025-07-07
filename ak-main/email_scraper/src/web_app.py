import streamlit as st
import pandas as pd
from email_scraper import EmailScraper
import tempfile
import os
from datetime import datetime

def main():
    st.set_page_config(
        page_title="Email Scraper",
        page_icon="📧",
        layout="wide"
    )
    
    st.title("📧 Bulk Email Scraper")
    st.markdown("""
    Upload a text file containing URLs (one per line) to extract email addresses.
    The results will be saved as a CSV file with timestamps.
    """)
    
    uploaded_file = st.file_uploader("Choose a text file with URLs", type=['txt'])
    
    if uploaded_file is not None:
        # Create a temporary file to store the uploaded content
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as temp_file:
            temp_file.write(uploaded_file.getvalue().decode())
            temp_file_path = temp_file.name
        
        try:
            if st.button("Start Scraping"):
                with st.spinner("Scraping emails... This may take a while."):
                    scraper = EmailScraper()
                    results = scraper.scrape_emails_from_file(temp_file_path)
                    
                    if results:
                        df = pd.DataFrame(results)
                        
                        # Create a temporary file for the CSV
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as csv_file:
                            df.to_csv(csv_file.name, index=False)
                            
                            # Read the CSV file for download
                            with open(csv_file.name, 'rb') as f:
                                csv_data = f.read()
                            
                            # Clean up the temporary CSV file
                            os.unlink(csv_file.name)
                        
                        # Display results
                        st.success(f"Found {len(results)} emails!")
                        st.dataframe(df)
                        
                        # Download button
                        st.download_button(
                            label="Download Results as CSV",
                            data=csv_data,
                            file_name=f"email_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("No emails found in the provided URLs.")
        
        finally:
            # Clean up the temporary input file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

if __name__ == "__main__":
    main() 