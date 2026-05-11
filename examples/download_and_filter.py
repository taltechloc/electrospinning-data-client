"""
Electrospinning Data - Filtered Download Example
This script demonstrates how to build filters, download the dataset,
and load it into a pandas DataFrame using the advanced Python client.
"""
import electrospinning_data_client as ed
from electrospinning_data_client.filters import FilterBuilder

def main():
    print("--- Electrospinning Data Explorer ---")
    
    # 1. Initialize the client
    client = ed.ElectrospinningDataClient()
    
    # 2. Build a complex filter using the fluent API
    # We want PAN produced between 15kV and 25kV
    filters = FilterBuilder() \
        .polymer("PAN") \
        .voltage(min_val=15, max_val=25)
        
    print(f"Applying filters: {filters.build()}")
    
    # 3. Download the latest data as a pandas DataFrame
    # Under the hood, this uses the DatasetService and Domain Models
    try:
        print("Downloading dataset...")
        df = client.download_latest(filters=filters)
        
        if df.empty:
            print("No matching records found for the given criteria.")
            return

        print(f"Success! Retrieved {len(df)} records.")

        # 4. Analyze results with pandas
        print("\n--- Data Summary ---")
        print(df[['recordId', 'polymer', 'voltage', 'fiberDiameter']].head())
        
        print("\n--- Statistics ---")
        print(df['fiberDiameter'].describe())

        # 5. (Optional) Export to Excel
        output_file = "filtered_data.xlsx"
        client.export_file(output_file, export_format="xlsx", filters=filters)
        print(f"\nResults successfully exported to {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
