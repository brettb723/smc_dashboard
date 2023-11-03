import streamlit as st
import pandas as pd
from utils.data_fetcher import fetch_appfolio_report
from datetime import datetime

def unit_detail_report():
    st.title("Multiple Reports View")

    # Fetch and display unit_details data
    unit_details_data = fetch_appfolio_report("unit_directory")
    if unit_details_data:
        unit_details_df = pd.DataFrame(unit_details_data)
        st.subheader("Unit Details")
        st.write(unit_details_df)
    else:
        st.error("Failed to fetch unit details data. Please check the connection or credentials.")

    # Fetch and display owner_directory data
    owner_directory_data = fetch_appfolio_report("owner_directory")
    if owner_directory_data:
        owner_directory_df = pd.DataFrame(owner_directory_data)
        st.subheader("Owner Directory")
        st.write(owner_directory_df)
    else:
        st.error("Failed to fetch owner directory data. Please check the connection or credentials.")

        owner_directory_data = fetch_appfolio_report("owner_directory")
    if owner_directory_data:
        owner_directory_df = pd.DataFrame(owner_directory_data)
        st.subheader("Owner Directory")
        st.write(owner_directory_df)
    else:
        st.error("Failed to fetch owner directory data. Please check the connection or credentials.")    