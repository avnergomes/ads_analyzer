"""
DataMapper - Usage Examples
============================

This file contains practical examples of using the DataMapper class
for integrating sales and ads data.
"""

import pandas as pd
from data_mapper import DataMapper, integrate_sales_and_ads_data, safe_numeric

# ============================================================================
# EXAMPLE 1: Basic CSV Normalization
# ============================================================================

print("=" * 70)
print("EXAMPLE 1: Normalizing a Days CSV")
print("=" * 70)

# Create DataMapper instance
mapper = DataMapper()

# Load your CSV
days_df = pd.read_csv('Days.csv')

# Normalize the data
days_normalized = mapper.normalize_csv_data(days_df, csv_type='days')

print(f"Original columns: {list(days_df.columns)}")
print(f"Normalized columns: {list(days_normalized.columns)}")
print(f"\nFirst row:\n{days_normalized.iloc[0]}")


# ============================================================================
# EXAMPLE 2: Extracting show_id from Campaign Names
# ============================================================================

print("\n" + "=" * 70)
print("EXAMPLE 2: Extracting show_id from Campaign Names")
print("=" * 70)

# Sample campaign names
campaign_names = [
    "US-WDC-Sales-0927-Interest-12",
    "NYC_1015_S2",
    "LAX-Sales-0801",
    "Tour_Chicago_15",
    "WashingtonDC_0927"
]

for campaign in campaign_names:
    show_id = mapper.extract_show_id_from_campaign(campaign)
    print(f"{campaign:40} → {show_id}")


# ============================================================================
# EXAMPLE 3: Creating Campaign Names from show_id
# ============================================================================

print("\n" + "=" * 70)
print("EXAMPLE 3: Creating Campaign Names from show_id")
print("=" * 70)

# Sample show IDs
show_ids = [
    "WDC_0927_S2",
    "NYC_1015_S1",
    "LAX_0801"
]

for show_id in show_ids:
    campaign_name = mapper.create_campaign_name_from_show_id(show_id)
    print(f"{show_id:15} → {campaign_name}")


# ============================================================================
# EXAMPLE 4: Data Quality Validation
# ============================================================================

print("\n" + "=" * 70)
print("EXAMPLE 4: Validating Data Quality")
print("=" * 70)

# Validate sales data
sales_df = pd.read_csv('sales_data.csv')
sales_quality = mapper.validate_data_quality(sales_df, data_type='sales')

print(f"\nSales Data Quality Report:")
print(f"Valid: {sales_quality['valid']}")
print(f"Rows: {sales_quality['row_count']}")
print(f"Columns: {sales_quality['column_count']}")

if sales_quality['warnings']:
    print(f"\nWarnings:")
    for warning in sales_quality['warnings']:
        print(f"  - {warning}")

if sales_quality['missing_values']:
    print(f"\nMissing Values:")
    for col, info in sales_quality['missing_values'].items():
        print(f"  - {col}: {info['count']} ({info['percentage']:.1f}%)")


# ============================================================================
# EXAMPLE 5: Merging Sales and Ads Data
# ============================================================================

print("\n" + "=" * 70)
print("EXAMPLE 5: Merging Sales and Ads Data")
print("=" * 70)

# Load data
sales_df = pd.read_csv('sales_data.csv')
ads_df = pd.read_csv('Days.csv')

# Normalize ads data
ads_normalized = mapper.normalize_csv_data(ads_df, csv_type='days')

# Merge
merged_df = mapper.merge_sales_and_ads(sales_df, ads_normalized, how='left')

print(f"\nMerged data shape: {merged_df.shape}")
print(f"Columns: {list(merged_df.columns)}")

# Show calculated metrics
if 'roas' in merged_df.columns:
    print(f"\nAverage ROAS: {merged_df['roas'].mean():.2f}")
if 'cpa' in merged_df.columns:
    print(f"Average CPA: ${merged_df['cpa'].mean():.2f}")
if 'click_to_purchase_rate' in merged_df.columns:
    print(f"Average Click-to-Purchase: {merged_df['click_to_purchase_rate'].mean():.2f}%")


# ============================================================================
# EXAMPLE 6: Complete Integration Workflow
# ============================================================================

print("\n" + "=" * 70)
print("EXAMPLE 6: Complete Integration Workflow")
print("=" * 70)

# Load all data
sales_df = pd.read_csv('sales_data.csv')
ads_days_df = pd.read_csv('Days.csv')
ads_placement_df = pd.read_csv('Days_Placement_Device.csv')
ads_time_df = pd.read_csv('Days_Time.csv')

# Integrate everything
integrated_df, stats = integrate_sales_and_ads_data(
    sales_df=sales_df,
    ads_days_df=ads_days_df,
    ads_placement_df=ads_placement_df,
    ads_time_df=ads_time_df
)

print(f"\nIntegration Statistics:")
print(f"Total Shows: {stats['total_shows']}")
print(f"Matched Shows: {stats['matched_shows']}")
print(f"Unmatched Shows: {stats['unmatched_shows']}")
if stats['total_shows'] > 0:
    match_rate = (stats['matched_shows'] / stats['total_shows']) * 100
    print(f"Match Rate: {match_rate:.1f}%")

# Save integrated data
integrated_df.to_csv('integrated_data.csv', index=False)
print(f"\n✅ Integrated data saved to 'integrated_data.csv'")


# ============================================================================
# EXAMPLE 7: Safe Numeric Conversion
# ============================================================================

print("\n" + "=" * 70)
print("EXAMPLE 7: Safe Numeric Conversion")
print("=" * 70)

# Sample values that might cause errors
test_values = [
    (123.45, "Normal float"),
    ("456", "String number"),
    (None, "None value"),
    (float('nan'), "NaN value"),
    ("not a number", "Invalid string"),
    ("", "Empty string")
]

for value, description in test_values:
    result = safe_numeric(value, default=0)
    print(f"{description:20} | Input: {str(value):15} | Output: {result}")


# ============================================================================
# EXAMPLE 8: Batch Processing Multiple Files
# ============================================================================

print("\n" + "=" * 70)
print("EXAMPLE 8: Batch Processing Multiple CSV Files")
print("=" * 70)

import glob

# Find all Days CSV files
csv_files = glob.glob('Days*.csv')

all_data = []
for csv_file in csv_files:
    print(f"Processing: {csv_file}")
    
    # Load and normalize
    df = pd.read_csv(csv_file)
    
    # Determine type from filename
    if 'Placement' in csv_file or 'Device' in csv_file:
        csv_type = 'days_placement_device'
    elif 'Time' in csv_file:
        csv_type = 'days_time'
    else:
        csv_type = 'days'
    
    # Normalize
    df_normalized = mapper.normalize_csv_data(df, csv_type=csv_type)
    all_data.append(df_normalized)
    
    print(f"  ✓ Rows: {len(df_normalized)}, Columns: {len(df_normalized.columns)}")

# Combine all data
if all_data:
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"\n✅ Combined {len(all_data)} files into {len(combined_df)} total rows")


# ============================================================================
# EXAMPLE 9: Custom Campaign Pattern Matching
# ============================================================================

print("\n" + "=" * 70)
print("EXAMPLE 9: Testing Campaign Pattern Matching")
print("=" * 70)

# Test various campaign name formats
test_campaigns = [
    # Standard formats
    "WDC_0927_S2",
    "NYC_1015_S1",
    "LAX_0801",
    
    # Legacy formats
    "US-WDC-Sales-0927",
    "US-NYC-Sales-1015-S2",
    
    # City name formats
    "WashingtonDC_0927",
    "NewYorkCity_1015",
    
    # Tour formats
    "Tour_Washington_27",
    "Tour_Chicago_15",
    
    # Extended formats
    "WDC-Sales-0927-Interest-12",
    "NYC-Sales-1015-S2-Target-45",
    
    # Edge cases
    "WDC 0927 S2",  # With spaces
    "wdc_0927_s2",  # Lowercase
]

print("\nPattern Matching Results:")
print("-" * 70)
for campaign in test_campaigns:
    show_id = mapper.extract_show_id_from_campaign(campaign)
    status = "✓" if show_id else "✗"
    print(f"{status} {campaign:45} → {show_id if show_id else 'NO MATCH'}")


# ============================================================================
# EXAMPLE 10: Performance Metrics Calculation
# ============================================================================

print("\n" + "=" * 70)
print("EXAMPLE 10: Calculating Performance Metrics")
print("=" * 70)

# Sample data
show_data = {
    'show_id': 'WDC_0927_S2',
    'total_sold': 4250,
    'revenue': 425000,
    'ad_spend': 15000,
    'clicks': 3500,
    'impressions': 450000
}

# Calculate metrics
metrics = {
    'ROAS': show_data['revenue'] / show_data['ad_spend'],
    'CPA': show_data['ad_spend'] / show_data['total_sold'],
    'CPM': (show_data['ad_spend'] / show_data['impressions']) * 1000,
    'CPC': show_data['ad_spend'] / show_data['clicks'],
    'Click-to-Purchase': (show_data['total_sold'] / show_data['clicks']) * 100,
    'Avg Ticket Price': show_data['revenue'] / show_data['total_sold']
}

print(f"\nShow: {show_data['show_id']}")
print("-" * 70)
for metric_name, value in metrics.items():
    if metric_name in ['ROAS', 'Click-to-Purchase']:
        print(f"{metric_name:20} : {value:.2f}")
    else:
        print(f"{metric_name:20} : ${value:.2f}")


# ============================================================================
# EXAMPLE 11: Error Handling and Validation
# ============================================================================

print("\n" + "=" * 70)
print("EXAMPLE 11: Error Handling Best Practices")
print("=" * 70)

def safe_process_ads_data(csv_path):
    """Safely process ads data with comprehensive error handling."""
    try:
        # Load data
        df = pd.read_csv(csv_path)
        print(f"✓ Loaded {csv_path}: {len(df)} rows")
        
        # Validate required columns
        required_cols = ['Campaign name', 'Amount spent (USD)', 'Impressions']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"✗ Missing required columns: {missing_cols}")
            return None
        
        # Normalize
        mapper = DataMapper()
        df_normalized = mapper.normalize_csv_data(df, csv_type='days')
        print(f"✓ Normalized data")
        
        # Validate quality
        quality = mapper.validate_data_quality(df_normalized, data_type='ads')
        
        if not quality['valid']:
            print(f"✗ Data quality issues:")
            for warning in quality['warnings']:
                print(f"  - {warning}")
            return None
        
        print(f"✓ Data quality validated")
        return df_normalized
        
    except FileNotFoundError:
        print(f"✗ File not found: {csv_path}")
        return None
    except pd.errors.EmptyDataError:
        print(f"✗ Empty CSV file: {csv_path}")
        return None
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return None

# Test with sample file
result = safe_process_ads_data('Days.csv')
if result is not None:
    print(f"\n✅ Successfully processed data: {len(result)} rows")
else:
    print(f"\n❌ Failed to process data")


# ============================================================================
# Summary
# ============================================================================

print("\n" + "=" * 70)
print("EXAMPLES COMPLETE")
print("=" * 70)
print("""
These examples demonstrate:
1. CSV normalization
2. show_id extraction from campaign names
3. Campaign name generation
4. Data quality validation
5. Sales and ads data merging
6. Complete integration workflow
7. Safe numeric conversion
8. Batch file processing
9. Campaign pattern matching
10. Performance metrics calculation
11. Error handling best practices

For more information, see:
- USAGE_GUIDE.txt: Complete usage guide
- README.md: Full documentation
- data_mapper.py: Source code with inline documentation
""")
