import streamlit as st
import pandas as pd
from utils.data_fetcher import fetch_appfolio_report
from datetime import datetime

def clean_percentage(value):
    if isinstance(value, str):
        # Remove percentage signs and commas
        value = value.replace('%', '').replace(',', '')
        # Convert to float
        try:
            return float(value)
        except ValueError:
            return None  # Return None if conversion fails
    return value  # Return the original value if it's not a string

def unit_detail_report():
    st.title("Combined Report View")

    # Fetch data from the reports
    unit_details_data = fetch_appfolio_report("unit_directory")
    property_directory_data = fetch_appfolio_report("property_directory")
    rent_roll_data = fetch_appfolio_report("rent_roll")

    # Check if the data was successfully fetched
    if unit_details_data and property_directory_data and rent_roll_data:
        # Convert the lists of dictionaries to DataFrames
        unit_details_df = pd.DataFrame(unit_details_data)
        property_directory_df = pd.DataFrame(property_directory_data)
        rent_roll_df = pd.DataFrame(rent_roll_data)

        # Join unit_directory with property_directory using PropertyId
        unit_property_df = pd.merge(unit_details_df, property_directory_df, on='PropertyId', how='left')

        # Now join the combined unit and property dataframe with rent_roll using UnitId
        combined_df = pd.merge(unit_property_df, rent_roll_df, on='UnitId', how='left')

        # Convert 'ManagementFeePercent' to numeric, coercing errors to NaN
        combined_df['ManagementFeePercent'] = combined_df['ManagementFeePercent'].apply(clean_percentage)
        combined_df['ManagementFeePercent'] = pd.to_numeric(combined_df['ManagementFeePercent'], errors='coerce')

        # Convert 'Rent' and 'ManagementFlatFee' to numeric if they are not already
        combined_df['Rent'] = pd.to_numeric(combined_df['Rent'], errors='coerce')
        combined_df['ManagementFlatFee'] = pd.to_numeric(combined_df['ManagementFlatFee'], errors='coerce')

        # Add a new column for the effective management fee
        combined_df['effective_mgmt_fee'] = combined_df.apply(
            lambda row: (row['Rent'] * row['ManagementFeePercent'] / 100) 
                        if pd.notnull(row['ManagementFeePercent']) and row['ManagementFeePercent'] > 0 
                        else row['ManagementFlatFee'],
            axis=1
        )

        # Select the specified columns to display, including the new effective_mgmt_fee
        columns_to_display = [
            'Owners', 'PropertyAddress_x', 'ManagementFeePercent', 'ManagementFlatFee',
            'ManagementFeeType', 'Tenant', 'Rent', 'Deposit', 'Late', 'effective_mgmt_fee'
        ]

        # Filter the dataframe to include only the specified columns
        final_df = combined_df[columns_to_display]

        # Display the filtered data
        st.subheader("Filtered Combined Unit Details with Effective Management Fee")
        st.dataframe(final_df)

    else:
        st.error("Failed to fetch one or more reports. Please check the connection or credentials.")
