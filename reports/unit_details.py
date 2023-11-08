import streamlit as st
import pandas as pd
from utils.data_fetcher import fetch_appfolio_report

def clean_numeric(value):
    if isinstance(value, str):
        value = value.replace('%', '').replace(',', '')  # Remove percentage signs and commas
        try:
            return float(value)
        except ValueError:
            return None
    return value

def unit_detail_report():
    st.title("Combined Report View")

    # Fetch data from the reports
    unit_details_data = fetch_appfolio_report("unit_directory")
    property_directory_data = fetch_appfolio_report("property_directory")
    rent_roll_data = fetch_appfolio_report("rent_roll")

    if unit_details_data and property_directory_data and rent_roll_data:
        unit_details_df = pd.DataFrame(unit_details_data)
        property_directory_df = pd.DataFrame(property_directory_data)
        rent_roll_df = pd.DataFrame(rent_roll_data)

        unit_count = unit_details_df['PropertyId'].value_counts().reset_index()
        unit_count.columns = ['PropertyId', 'UnitCount']
        property_directory_df = pd.merge(property_directory_df, unit_count, on='PropertyId', how='left')
        unit_property_df = pd.merge(unit_details_df, property_directory_df, on='PropertyId', how='left')
        combined_df = pd.merge(unit_property_df, rent_roll_df, on='UnitId', how='left')

        # Apply the clean_numeric function to percentage and monetary columns
        combined_df['ManagementFeePercent'] = combined_df['ManagementFeePercent'].apply(clean_numeric)
        combined_df['Rent'] = combined_df['Rent'].apply(clean_numeric)
        combined_df['ManagementFlatFee'] = combined_df['ManagementFlatFee'].apply(clean_numeric)
        combined_df['Deposit'] = combined_df['Deposit'].apply(clean_numeric)

        def calculate_effective_mgmt_fee(row):
            if pd.notnull(row['ManagementFeePercent']) and row['ManagementFeePercent'] > 0:
                return row['Rent'] * row['ManagementFeePercent'] / 100
            elif pd.notnull(row['ManagementFlatFee']) and pd.notnull(row['UnitCount']):
                return row['ManagementFlatFee'] / row['UnitCount']
            return 0

        combined_df['EffectiveMgmtFee'] = combined_df.apply(calculate_effective_mgmt_fee, axis=1)

        # Calculate KPIs
        total_units = unit_details_df['UnitId'].nunique()
        monthly_mgmt_fees = combined_df['EffectiveMgmtFee'].sum()

         # Calculate KPIs for the summary table
        summary_df = combined_df.groupby('Owners').agg(
            UnitCount=('UnitId', 'nunique'),
            SumEffectiveMgmtFee=('EffectiveMgmtFee', 'sum')
        ).reset_index()

                # Display KPIs
        st.subheader("Key Performance Indicators")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Total Units Under Management", value=total_units)
        with col2:
            st.metric(label="Monthly Effective Management Fees", value=f"${monthly_mgmt_fees:,.2f}")

         # Display the summary table
        st.subheader("Summary by Owner")
        st.dataframe(summary_df.style.format({'SumEffectiveMgmtFee': "${:,.2f}"}))



        columns_to_display = [
            'Owners', 'PropertyAddress_x', 'ManagementFeePercent', 'ManagementFlatFee',
            'ManagementFeeType', 'Tenant', 'Rent', 'Deposit', 'Late', 'EffectiveMgmtFee'
        ]
        final_df = combined_df[columns_to_display]
        st.subheader("Filtered Combined Unit Details with Effective Management Fee")
        st.dataframe(final_df)

    else:
        st.error("Failed to fetch one or more reports. Please check the connection or credentials.")

# Call the function to display the report in Streamlit
unit_detail_report()
