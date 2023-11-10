import streamlit as st
import pandas as pd
from utils.data_fetcher import fetch_appfolio_report
from datetime import datetime

def unit_vacancy_detail():
    st.title("Unit Vacancy Detail View")

    # Fetch data from the reports
    unit_details_data = fetch_appfolio_report("unit_directory")
    property_directory_data = fetch_appfolio_report("property_directory")
    unit_vacancy_data = fetch_appfolio_report("unit_vacancy")

    if unit_details_data and property_directory_data and unit_vacancy_data:
        # Convert data to dataframes
        unit_details_df = pd.DataFrame(unit_details_data)
        property_directory_df = pd.DataFrame(property_directory_data)
        unit_vacancy_df = pd.DataFrame(unit_vacancy_data)

        # Calculate days vacant and create aging buckets
        unit_vacancy_df['DaysVacant'] = (datetime.now() - pd.to_datetime(unit_vacancy_df['LastMoveOut'])).dt.days
        unit_vacancy_df['AgingBucket'] = pd.cut(unit_vacancy_df['DaysVacant'], 
                                                 bins=[0, 30, 60, 90, 120, float('inf')], 
                                                 labels=['0-30', '31-60', '61-90', '91-120', '120+'])

        # Merge unit details with property directory
        combined_df = pd.merge(
            unit_details_df, 
            property_directory_df, 
            on='PropertyId', 
            how='left', 
            suffixes=('', '_prop')
        )

        # Merge the result with unit vacancy details
        combined_df = pd.merge(
            combined_df, 
            unit_vacancy_df, 
            on='UnitId', 
            how='left', 
            suffixes=('', '_vac')
        )

        # Exclude specific owners
        excluded_owners = ['Andrews Management', 'Paladin Properties LLC']
        combined_df = combined_df[~combined_df['Owners'].isin(excluded_owners)]

        # Summary table for all units
        summary_df = combined_df.groupby('Owners').agg(
            TotalUnits=pd.NamedAgg(column='UnitName', aggfunc='count'),
            VacantUnits=pd.NamedAgg(column='DaysVacant', aggfunc=lambda x: sum(x > 0))
        )

        # Display the summary table
        st.subheader("Summary Table")
        st.dataframe(summary_df)

        # Filter for vacant units
        vacant_df = combined_df[combined_df['DaysVacant'] > 0]

        # Filter option by client (Owner)
        owner_filter = st.selectbox('Filter by Owner:', options=['All'] + list(vacant_df['Owners'].unique()))
        if owner_filter != 'All':
            vacant_df = vacant_df[vacant_df['Owners'] == owner_filter]

        # Select specific columns for detailed view
        vacant_df = vacant_df[['Owners', 'PropertyAddress', 'UnitName', 'LastMoveOut', 'LastRent', 'UnitStatus', 'AvailableOn', 'LockboxEnabled', 'AgingBucket']]

        # Display the detailed combined dataframe for vacant units
        st.subheader("Detailed Vacant Unit View")
        st.dataframe(vacant_df)

    else:
        st.error("Failed to fetch one or more reports. Please check the connection or credentials.")

