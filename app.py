import streamlit as st
from reports import work_orders_client, work_orders, unit_details, view_tables

def main():
    # Sidebar navigation
    reports = {
        "Welcome": welcome_page,
         "Work Orders Data Dump": work_orders.display_report,
         "Work Orders By Client": work_orders_client.display_report,
        "Unit Detail": unit_details.unit_detail_report,
        "View Tables": view_tables.display_report
    }

    choice = st.sidebar.selectbox("Choose a report", list(reports.keys()))
    reports[choice]()

def welcome_page():
    st.title("Welcome")
    st.write("Welcome to the reporting dashboard. Please select a report from the left sidebar to view its contents.")

if __name__ == "__main__":
    main()
