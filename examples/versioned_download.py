"""
Example showing how to work with versioned dataset snapshots.
"""
import electrospinning_data_client as ed

def main():
    client = ed.ElectrospinningDataClient()
    
    # 1. Get available versions
    print("Checking available versions...")
    versions = client.get_versions()
    
    if not versions:
        print("No version snapshots found.")
        return
        
    for v in versions:
        print(f"- {v['versionIdentifier']} (created: {v['createdAt']}, records: {v['recordCount']})")
    
    # 2. Download the first available version
    target_version = versions[0]['versionIdentifier']
    print(f"\nDownloading version: {target_version}...")
    
    df = ed.load_versioned_dataset(target_version)
    
    print(f"Retrieved {len(df)} records from version {target_version}.")

if __name__ == "__main__":
    main()
