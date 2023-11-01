import streamlit as st
import pandas as pd
from datetime import datetime
from data_fetcher import fetch_appfolio_report

# Define aging bucket labels
labels = ["0-7 days", "8-30 days", "31-60 days", "61-90 days", "90+ days"]

def process_data(data):
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Use 'CreatedAt' as the column name for when the work order was created
    df['CreatedAt'] = pd.to_datetime(df['CreatedAt'])
    df['age'] = (datetime.now() - df['CreatedAt']).dt.days

    # Create aging buckets based on the age of the work orders
    bins = [0, 7, 30, 60, 90, float('inf')]
    df['aging_bucket'] = pd.cut(df['age'], bins=bins, labels=labels, right=False)

    # Exclude specific statuses
    excluded_statuses = ['Canceled', 'Completed', 'Completed No Need To Bill']
    df = df[~df['Status'].isin(excluded_statuses)]

    return df

def main():
    st.title("Work Orders Visualization")

    # Fetch data
    data = fetch_appfolio_report("work_order")

    if not data:
        st.error("Failed to fetch data. Please check the connection or credentials.")
        return

    # Process data for visualization
    df = process_data(data)

    # Filter by status
    unique_statuses = sorted(list(set(df['Status'])))
    selected_status = st.selectbox("Filter by status:", ["All"] + unique_statuses)

    if selected_status != "All":
        df = df[df['Status'] == selected_status]

    # Display the Work Orders Aging filtered by the selected status
    st.subheader("Work Orders Aging")
    summary_age = df['aging_bucket'].value_counts().reset_index()
    summary_age.columns = ['Aging Bucket', 'Count']
    st.write(summary_age.set_index('Aging Bucket'))  # Set 'Aging Bucket' as the index

    # Allow users to drill down into specific aging buckets, also filtered by the selected status
    st.subheader("Drill Down into Specific Aging Buckets")
    selected_bucket = st.selectbox("Select an aging bucket to drill down:", labels)

    # Filtering columns for the drill-down section
    desired_columns = ['PropertyAddress', 'UnitName', 'WorkOrderType', 'ServiceRequestDescription', 'CreatedBy', 'WorkOrderNumber']
    filtered_df = df[df['aging_bucket'] == selected_bucket][desired_columns]

    # Resetting the index to start from 1
    filtered_df = filtered_df.reset_index(drop=True)
    filtered_df.index += 1
    st.write(filtered_df.reset_index(drop=True))  # Reset index and drop the default index column

if __name__ == "__main__":
    main()
