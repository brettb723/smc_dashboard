
from utils.data_fetcher import fetch_appfolio_report
from datetime import datetime

def unit_detail_report():
    # Fetch the unit_detail data
    data = fetch_appfolio_report("unit_detail")
    
    # Handle the case if data fetching fails
    if not data:
        st.error("Failed to fetch unit_detail data. Please check the connection or credentials.")
        return
    
    # Convert the fetched data to a Pandas DataFrame
    df = pd.DataFrame(data)

    # Print the headers to the console
    print("Headers for unit_detail report:", df.columns.tolist())

    # Assuming there's a date column similar to 'CreatedAt' for aging calculation:
    date_column = 'CreatedAt'  # Replace this with the correct column name if different
    if date_column in df.columns:
        df[date_column] = pd.to_datetime(df[date_column])
        df['age'] = (datetime.now() - df[date_column]).dt.days

        # Create aging buckets based on the age
        bins = [0, 7, 30, 60, 90, float('inf')]
        df['aging_bucket'] = pd.cut(df['age'], bins=bins, labels=labels, right=False)
    else:
        st.warning(f"'{date_column}' column not found in unit_detail report. Aging calculation skipped.")

    # Here, you can display the processed `unit_detail` report as desired
    st.write(df)

