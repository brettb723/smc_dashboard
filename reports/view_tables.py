import streamlit as st
import pandas as pd
from utils.data_fetcher import fetch_appfolio_report

def process_data(work_order_data, property_directory_data):
    # Convert data to pandas DataFrames
    work_order_df = pd.DataFrame(work_order_data)
    property_directory_df = pd.DataFrame(property_directory_data)
    # Merge dataframes on 'PropertyId'
    merged_df = work_order_df.merge(property_directory_df, on='PropertyId', how='left')
    return merged_df

def display_report():
    st.title("Work Order Aging Report")

    # Fetch work_order data
    work_order_data = fetch_appfolio_report("work_order")
    if not work_order_data:
        st.error("Failed to fetch work order data. Please check the connection or credentials.")
        return

    # Fetch property_directory data
    property_directory_data = fetch_appfolio_report("property_directory")
    if not property_directory_data:
        st.error("Failed to fetch property directory data. Please check the connection or credentials.")
        return

    # Process the fetched data
    df = process_data(work_order_data, property_directory_data)

    # Define aging buckets
    aging_buckets = ['0-30', '31-60', '61-90', '90+']
    
    # Create an empty DataFrame for the aging report
    aging_report_df = pd.DataFrame(columns=['Owners'] + aging_buckets)

    # Group the work orders by Owner and calculate the aging
    for owner, group in df.groupby('Owners'):
        # Initialize a new row with zeros for each bucket
        new_row = {bucket: 0 for bucket in aging_buckets}
        new_row['Owners'] = owner

        # Calculate the count for each aging bucket
        for _, work_order in group.iterrows():
            aging_days = (pd.Timestamp('now') - pd.to_datetime(work_order['CreatedAt'])).days
            if aging_days <= 30:
                new_row['0-30'] += 1
            elif 31 <= aging_days <= 60:
                new_row['31-60'] += 1
            elif 61 <= aging_days <= 90:
                new_row['61-90'] += 1
            else:
                new_row['90+'] += 1

        # Append the new row to the aging report DataFrame
        aging_report_df = aging_report_df.append(new_row, ignore_index=True)

    # Calculate totals for each column (excluding the 'Owners' column)
    totals = aging_report_df.drop('Owners', axis=1).sum().rename('Total')
    # Append totals row to the DataFrame
    aging_report_df = aging_report_df.append(totals)

    # Display the aging report DataFrame with sortable headers
    st.dataframe(aging_report_df.set_index('Owners'), width=700, height=500)
