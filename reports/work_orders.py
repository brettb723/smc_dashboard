import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from utils.data_fetcher import fetch_appfolio_report


st.set_page_config(layout="wide")

# Custom CSS to make the data table wider
def _max_width_():
    max_width_str = f"max-width: 2000px;"
    st.markdown(
        f"""
        <style>
        .reportview-container .main .block-container{{
            {max_width_str}
        }}
        </style>    
        """,
        unsafe_allow_html=True,
    )

# Call the function to apply custom CSS for max width
_max_width_()

def process_data(work_order_data, property_directory_data):
    # Convert to DataFrame
    work_order_df = pd.DataFrame(work_order_data)
    property_directory_df = pd.DataFrame(property_directory_data)
    
    # Join work_order_df with property_directory_df on PropertyId
    work_order_df = work_order_df.merge(property_directory_df, on='PropertyId', how='left')

    return work_order_df

def display_report():
    st.title("Work Order Reports")
    
    # Fetch data
    work_order_data = fetch_appfolio_report("work_order")
    property_directory_data = fetch_appfolio_report("property_directory")
    
    if not work_order_data or not property_directory_data:
        st.error("Failed to fetch data. Please check the connection or credentials.")
        return

    # Process data for visualization
    df = process_data(work_order_data, property_directory_data)

    # Filter by status
    unique_statuses = sorted(list(set(df['Status'])))
    selected_status = st.selectbox("Filter by status:", ["All"] + unique_statuses)

    if selected_status != "All":
        df = df[df['Status'] == selected_status]

    # Check if all the specified columns exist in the dataframe
    columns_to_display = ['Owners','PropertyAddress_x', 'UnitName', 'Status','AssignedUser', 'WorkOrderType', 'FollowUpOn','VendorTrade', 'CreatedBy', 'CreatedAt', 'WorkOrderNumber','ServiceRequestDescription']
    missing_columns = [column for column in columns_to_display if column not in df.columns]

    if missing_columns:
        st.error(f"The following columns are missing from the data: {', '.join(missing_columns)}")
        # Optionally, you can display the dataframe without the missing columns
        columns_to_display = [column for column in columns_to_display if column not in missing_columns]

    # Display the data table with specified columns
    st.subheader(f"Work Orders - {selected_status}")
    st.dataframe(df[columns_to_display])  # Render only specified columns

    # Add a button to export the data to CSV
    if columns_to_display:
        csv_export_df = df[columns_to_display]
        csv = csv_export_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download selected data as CSV",
            data=csv,
            file_name='work_orders_selected_columns.csv',
            mime='text/csv',
        )

    # Print all DataFrame keys below
    st.subheader("Data Keys")
    all_keys = pd.DataFrame(df.keys(), columns=["Key"])
    st.table(all_keys)  # Use st.table to render the DataFrame keys as a static table
