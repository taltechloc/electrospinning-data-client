"""
Example script to download and print the dataset as a DataFrame.
"""
import electrospinning_data_client as ed

def main():
    # 1. Initialize client
    client = ed.ElectrospinningDataClient()
    
    print("Downloading dataset...")
    
    # 2. Download latest dataset
    # This return a validated pandas DataFrame
    df = client.download_latest()
    
    # 3. Print the results
    print("\n--- Dataset Preview ---")
    
    # Configure pandas to show all columns
    import pandas as pd
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    print(df.head(10))
    
    print(f"\nTotal records: {len(df)}")
    
    # 4. Save to CSV
    csv_filename = "electrospinning_data_clientset.csv"
    df.to_csv(csv_filename, index=False)
    print(f"Dataset successfully saved to {csv_filename}")

    print("\n--- Column Information ---")
    print(df.dtypes)

if __name__ == "__main__":
    main()
