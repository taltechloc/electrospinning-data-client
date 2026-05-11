"""
Basic example showing how to download the latest dataset.
"""
import electrospinning_data_client as ed

def main():
    print("Fetching latest dataset...")
    
    # download_latest returns a pandas DataFrame
    df = ed.load_latest_dataset()
    
    print(f"Success! Retrieved {len(df)} records.")
    print("\nFirst 5 records:")
    print(df.head())
    
    # basic column info
    print("\nColumns available:")
    print(df.columns.tolist())

if __name__ == "__main__":
    main()
