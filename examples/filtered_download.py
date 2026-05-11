"""
Example showing how to apply filters when downloading data.
"""
import electrospinning_data_client as ed

def main():
    # Define filters
    # Here we look for PAN produced at 25kV
    filters = {
        "polymer": "PAN",
        "voltageMin": 24,
        "voltageMax": 26
    }
    
    print(f"Fetching data with filters: {filters}")
    
    df = ed.load_latest_dataset(filters=filters)
    
    if df.empty:
        print("No matching records found.")
    else:
        print(f"Found {len(df)} matching records.")
        print(df[['recordId', 'polymer', 'voltage', 'fiberDiameter']].head())

if __name__ == "__main__":
    main()
