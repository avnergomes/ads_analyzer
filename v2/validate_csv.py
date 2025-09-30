"""
Validation script to check if CSV files match expected structure
"""

import pandas as pd
import sys
from typing import Dict, List, Tuple

class CSVValidator:
    """Validates uploaded CSV files against expected structures"""
    
    def __init__(self):
        # Expected column patterns for each dataset type
        self.expected_structures = {
            "days": {
                "required_columns": [
                    "reporting starts", "campaign name", "amount spent (usd)",
                    "impressions", "link clicks", "results"
                ],
                "optional_columns": [
                    "reporting ends", "campaign delivery", "ad set budget",
                    "attribution setting", "cpm", "frequency", "reach",
                    "ctr (link)", "result indicator", "cost per results", "ends"
                ],
                "total_expected": 18
            },
            "days_placement_device": {
                "required_columns": [
                    "reporting starts", "campaign name", "platform", 
                    "placement", "device platform", "impression device"
                ],
                "optional_columns": [
                    "reporting ends", "campaign delivery", "ad set budget",
                    "amount spent (usd)", "attribution setting", "cpm",
                    "impressions", "frequency", "reach", "ctr (link)",
                    "link clicks", "results", "result indicator",
                    "cost per results", "ends"
                ],
                "total_expected": 22
            },
            "days_time": {
                "required_columns": [
                    "reporting starts", "campaign name", 
                    "time of day (viewer's time zone)"
                ],
                "optional_columns": [
                    "reporting ends", "campaign delivery", "ad set budget",
                    "amount spent (usd)", "attribution setting", "cpm",
                    "impressions", "frequency", "reach", "ctr (link)",
                    "link clicks", "results", "result indicator",
                    "cost per results", "ends"
                ],
                "total_expected": 19
            }
        }
    
    def normalize_column_name(self, col: str) -> str:
        """Normalize column name to lowercase without special chars"""
        import re
        return re.sub(r'[^a-z0-9]', '', col.lower())
    
    def validate_file(self, filepath: str) -> Tuple[bool, str, Dict]:
        """Validate a single CSV file"""
        try:
            # Read CSV
            df = pd.read_csv(filepath)
            
            # Get normalized column names
            actual_columns = [self.normalize_column_name(col) for col in df.columns]
            
            # Try to identify file type
            file_type = self._identify_file_type(actual_columns)
            
            if not file_type:
                return False, "unknown", {
                    "error": "Could not identify file type",
                    "columns_found": list(df.columns),
                    "total_columns": len(df.columns)
                }
            
            # Get expected structure
            expected = self.expected_structures[file_type]
            
            # Check required columns
            required_normalized = [
                self.normalize_column_name(col) 
                for col in expected["required_columns"]
            ]
            
            missing_required = [
                col for col in required_normalized 
                if col not in actual_columns
            ]
            
            # Prepare report
            report = {
                "file_type": file_type,
                "total_columns": len(df.columns),
                "expected_columns": expected["total_expected"],
                "columns_match": len(df.columns) == expected["total_expected"],
                "missing_required": missing_required,
                "all_columns": list(df.columns),
                "rows": len(df)
            }
            
            is_valid = len(missing_required) == 0
            
            return is_valid, file_type, report
            
        except Exception as e:
            return False, "error", {"error": str(e)}
    
    def _identify_file_type(self, normalized_columns: List[str]) -> str:
        """Identify file type based on columns"""
        # Check for time dataset
        if "timeofdayviewerstimezone" in normalized_columns or "timeofday" in normalized_columns:
            return "days_time"
        
        # Check for placement/device dataset
        if any(col in normalized_columns for col in ["placement", "platform", "deviceplatform"]):
            return "days_placement_device"
        
        # Check for basic days dataset
        has_date = "reportingstarts" in normalized_columns
        has_campaign = "campaignname" in normalized_columns or "campaign" in normalized_columns
        
        if has_date and has_campaign:
            return "days"
        
        return None
    
    def print_report(self, filepath: str, is_valid: bool, file_type: str, report: Dict):
        """Print validation report"""
        print(f"\n{'='*80}")
        print(f"File: {filepath}")
        print(f"{'='*80}")
        
        if file_type == "error":
            print(f"❌ ERROR: {report.get('error', 'Unknown error')}")
            return
        
        if file_type == "unknown":
            print(f"❌ UNKNOWN FILE TYPE")
            print(f"   Columns found: {report['total_columns']}")
            print(f"   Columns: {', '.join(report['columns_found'][:5])}...")
            return
        
        status = "✅ VALID" if is_valid else "⚠️  INVALID"
        print(f"Status: {status}")
        print(f"Type: {file_type.replace('_', ' ').title()}")
        print(f"Rows: {report['rows']:,}")
        print(f"Columns: {report['total_columns']} (expected: {report['expected_columns']})")
        
        if not report['columns_match']:
            print(f"⚠️  Column count mismatch!")
        
        if report['missing_required']:
            print(f"\n❌ Missing required columns:")
            for col in report['missing_required']:
                print(f"   - {col}")
        
        print(f"\n📋 All columns in file:")
        for i, col in enumerate(report['all_columns'], 1):
            print(f"   {i:2d}. {col}")


def main():
    """Main validation function"""
    if len(sys.argv) < 2:
        print("Usage: python validate_csv.py <file1.csv> [file2.csv] [file3.csv]")
        print("\nExample:")
        print("  python validate_csv.py Days.csv")
        print("  python validate_csv.py Days.csv 'Days Placement Device.csv' 'Days Time.csv'")
        return
    
    validator = CSVValidator()
    
    print("\n" + "="*80)
    print("CSV FILE VALIDATOR FOR ADS ANALYZER v2.0")
    print("="*80)
    
    results = []
    
    for filepath in sys.argv[1:]:
        is_valid, file_type, report = validator.validate_file(filepath)
        results.append((filepath, is_valid, file_type))
        validator.print_report(filepath, is_valid, file_type, report)
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    types_found = {
        "days": False,
        "days_placement_device": False,
        "days_time": False
    }
    
    for filepath, is_valid, file_type in results:
        status = "✅" if is_valid else "❌"
        print(f"{status} {filepath}: {file_type}")
        if file_type in types_found:
            types_found[file_type] = True
    
    print("\n" + "-"*80)
    print("Required file types:")
    for file_type, found in types_found.items():
        status = "✅" if found else "❌"
        print(f"  {status} {file_type.replace('_', ' ').title()}")
    
    all_found = all(types_found.values())
    
    if all_found:
        print("\n✅ All required file types are present!")
    else:
        print("\n⚠️  Some required file types are missing.")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
