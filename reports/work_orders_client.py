import streamlit as st
import pandas as pd
from utils.data_fetcher import fetch_appfolio_report
from streamlit import session_state as state

if 'selected_owner' not in state:
    state.selected_owner = 'All'

def process_data(work_order_data, property_directory_data):
    # Convert data to pandas DataFrames
    work_order_df = pd.DataFrame(work_order_data)
    property_directory_df = pd.DataFrame(property_directory_data)

    # Filter out the unwanted statuses
    filtered_work_order_df = work_order_df[
        ~work_order_df['Status'].isin(['Completed', 'Canceled', 'Completed No Need To Bill'])
    ]
    
    # Merge filtered dataframes on 'PropertyId'
    merged_df = filtered_work_order_df.merge(property_directory_df, on='PropertyId', how='left')

    merged_df.rename(columns={
        'PropertyAddress_x': 'PropertyAddress',
        'PropertyCity_x': 'PropertyCity',
        'PropertyZip_x': 'PropertyZip'
    }, inplace=True)
    return merged_df

def calculate_aging(row, current_date):
    aging_days = (current_date - pd.to_datetime(row['CreatedAt'])).days
    if aging_days <= 30:
        return '0-30'
    elif 31 <= aging_days <= 60:
        return '31-60'
    elif 61 <= aging_days <= 90:
        return '61-90'
    else:
        return '90+'


def display_report():
    st.title("Work Order Aging Report")

    # Fetch data
    work_order_data = fetch_appfolio_report("work_order")
    property_directory_data = fetch_appfolio_report("property_directory")
    if not work_order_data or not property_directory_data:
        st.error("Failed to fetch data. Please check the connection or credentials.")
        return

    # Process data
    df = process_data(work_order_data, property_directory_data)
    current_date = pd.Timestamp('now')
    df['Aging'] = df.apply(lambda row: calculate_aging(row, current_date), axis=1)

    # Filter widgets
    unique_owners = df['Owners'].unique()
    selected_owner = st.selectbox('Select a Client:', ['All'] + list(unique_owners))
    aging_buckets = ['0-30', '31-60', '61-90', '90+']
    selected_aging_bucket = st.selectbox('Select an Aging Bucket:', ['All'] + aging_buckets)

    # Apply filters for summary table
    summary_df = df.copy()
    if selected_owner != 'All':
        summary_df = summary_df[summary_df['Owners'] == selected_owner]
    if selected_aging_bucket != 'All':
        summary_df = summary_df[summary_df['Aging'] == selected_aging_bucket]

    # Generate the hyperlink for each service request number
    # But display it with WorkOrderNumber text
    df['WorkOrderNumber'] = df.apply(
        lambda x: f'<a href="https://standardmgmtco.appfolio.com/maintenance/service_requests/{x["ServiceRequestNumber"]}" target="_blank">{x["WorkOrderNumber"]}</a>', axis=1
    )

    # Ensure you convert the column to string if not already
    df['WorkOrderNumber'] = df['WorkOrderNumber'].astype(str) 

    # Generate the summary aging table
    aging_summary = summary_df.groupby(['Owners', 'Aging']).size().reset_index(name='Counts')

    # Display the summary aging table
    st.write("Summary Aging Table:")
    st.dataframe(aging_summary.pivot(index='Owners', columns='Aging', values='Counts').fillna(0))

    # Apply filters for detailed table
    if selected_owner != 'All':
        df = df[df['Owners'] == selected_owner]
    if selected_aging_bucket != 'All':
        df = df[df['Aging'] == selected_aging_bucket]

    # Define the columns to display in the detailed report
    detailed_columns = [
        'PropertyAddress', 'PropertyCity', 'PropertyZip', 'WorkOrderNumber',
        'WorkOrderType', 'ServiceRequestDescription', 'JobDescription',
        'VendorTrade', 'Status', 'UnitName', 'Owners', 'Aging'
    ]
    
    # Select only the specified columns for the detailed report
    detailed_df = df[detailed_columns]

    # Display the detailed table based on filters
    st.write("Detailed Report:")
    st.write(detailed_df.to_html(escape=False, index=False), unsafe_allow_html=True)



# Run the report display function
if __name__ == "__main__":
    display_report()