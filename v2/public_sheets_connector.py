"""Utilities to pull the public Google Sheet with detailed ticket sales data."""

import pandas as pd
import numpy as np
import requests
import csv
from io import StringIO
from datetime import datetime
from typing import Optional, Union
import re
import logging

logger = logging.getLogger(__name__)

class PublicSheetsConnector:
    """Connector responsible for downloading and parsing the public ticket sheet."""
    
    def __init__(self):
        # Public sheet URL (CSV export format)
        self.sheet_id = "1hVm1OALKQ244zuJBQV0SsQT08A2_JTDlPytUNULRofA"
        self.csv_url = f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/export?format=csv&gid=0"
        
        # Column mapping derived from the sheet structure
        self.column_mapping = {
            0: 'show_id',           # Show identifier (e.g. WDC_0927)
            1: 'show_date',         # Performance date
            2: 'report_date',       # Report creation date
            3: 'show_name',         # Friendly show description
            4: 'capacity',          # Total capacity
            5: 'venue_holds',       # Seats held by venue
            6: 'wheelchair_companions', # Wheelchair & companion holds
            7: 'camera',            # Camera holds
            8: 'artists_hold',      # Artist holds
            9: 'kills',             # Kills
            10: 'yesterday_sales',  # Tickets sold yesterday
            11: 'today_sold',       # Tickets sold in the last day
            12: 'sales_to_date',    # Revenue to date
            13: 'total_sold',       # Total tickets sold
            14: 'remaining',        # Tickets remaining
            15: 'sold_percentage',  # % of capacity sold
            16: 'atp',              # Average ticket price
            17: 'report_message'    # Additional notes
        }

        # Known currency aliases and approximate USD conversion rates
        self.currency_aliases = {
            "": "USD",
            "$": "USD",
            "US$": "USD",
            "USD": "USD",
            "R$": "BRL",
            "BRL": "BRL",
            "MX$": "MXN",
            "MXN": "MXN",
            "MXN$": "MXN",
            "CA$": "CAD",
            "CAD": "CAD",
            "C$": "CAD",
            "A$": "AUD",
            "AUD": "AUD",
            "£": "GBP",
            "GBP": "GBP",
            "€": "EUR",
            "EUR": "EUR",
            "COP": "COP",
            "COP$": "COP",
            "CLP": "CLP",
            "CLP$": "CLP",
            "ARS": "ARS",
            "ARS$": "ARS",
            "PEN": "PEN",
            "PEN$": "PEN",
            "S/": "PEN",
        }

        # Static FX reference table (can be refreshed periodically)
        self.currency_to_usd = {
            "USD": 1.0,
            "BRL": 0.20,
            "MXN": 0.055,
            "CAD": 0.74,
            "AUD": 0.66,
            "GBP": 1.27,
            "EUR": 1.08,
            "COP": 0.00026,
            "CLP": 0.0011,
            "ARS": 0.0012,
            "PEN": 0.27,
        }

        # Patterns used to classify each row in the CSV export
        self.patterns = {
            'month_header': r'^(September|October|November|December)$',
            'month_asterisk': r'^\*(September|October|November|December)\*$',
            'show_id': r'^[A-Z]{2,3}_\d{4}(_S\d+)?$',  # Ex: WDC_0927, WDC_0927_S3
            'end_row': r'^endRow$',
            'summary_line': r'^\d+\s*\(\+\d+\)\s*\d+',  # Ex: "1371 (+8) 1379"
            'date_format': r'^\d{4}-\d{2}-\d{2}$'
        }
    
    def load_data(self, csv_payload: Optional[Union[str, bytes]] = None):
        """Download or parse the ticket sheet and return a cleaned DataFrame."""
        try:
            if csv_payload is None:
                response = requests.get(self.csv_url, timeout=30)
                response.raise_for_status()
                csv_text = response.text
            else:
                if isinstance(csv_payload, bytes):
                    csv_text = csv_payload.decode("utf-8-sig")
                else:
                    csv_text = csv_payload

            csv_data = StringIO(csv_text)
            reader = csv.reader(csv_data)

            # Row-by-row analysis
            raw_data = list(reader)
            processed_data = self._analyze_rows_minutely(raw_data)

            # Convert to DataFrame
            df = pd.DataFrame(processed_data)

            # Apply cleaning and enrichments
            df = self._clean_and_transform(df)

            logger.info("Loaded %s show records from the public sheet", len(df))
            return df

        except Exception as e:
            logger.error("Failed to load sheet: %s", e)
            return None

    def load_from_uploaded_file(self, uploaded_file) -> Optional[pd.DataFrame]:
        """Parse a Streamlit uploaded file containing the ticket sheet export."""
        if uploaded_file is None:
            return None

        try:
            file_bytes = uploaded_file.getvalue()
            if not file_bytes:
                logger.warning("Uploaded ticket sales file is empty: %s", uploaded_file.name)
                return None

            return self.load_data(file_bytes)

        except Exception as exc:
            logger.error("Failed to parse uploaded ticket sheet %s: %s", uploaded_file.name, exc)
            return None
    
    def _analyze_rows_minutely(self, raw_data):
        """Iterate through raw rows and keep only valid show entries."""
        processed_shows = []
        current_month = None

        logger.info("Parsing %s rows from the sheet export", len(raw_data))

        for row_idx, row in enumerate(raw_data):
            if not row or len(row) == 0:
                continue

            # Determine the row type using the first cell
            first_cell = str(row[0]).strip() if row[0] else ""

            logger.debug("Row %s: '%s' | Columns: %s", row_idx, first_cell, len(row))

            # Identify row type
            line_type = self._identify_line_type(first_cell, row)

            if line_type == "month_header":
                current_month = first_cell
                logger.info("Found month header: %s", current_month)
                continue

            elif line_type == "show_data":
                # Extract show data
                show_data = self._extract_show_data(row, row_idx, current_month)
                if show_data:
                    processed_shows.append(show_data)
                    logger.debug(
                        "Captured show %s - %s", show_data["show_id"], show_data["show_name"]
                    )

            elif line_type == "summary_line":
                logger.debug("Skipping summary line: %s", first_cell)
                continue

            elif line_type == "end_row":
                logger.debug("Reached endRow marker at row %s", row_idx)
                break

            elif line_type in ["month_asterisk", "header"]:
                logger.debug("Skipping helper row (%s): %s", line_type, first_cell)
                continue

            else:
                logger.debug("Unrecognised row: %s", first_cell)

        logger.info("Total shows processed: %s", len(processed_shows))
        return processed_shows

    def _identify_line_type(self, first_cell, row):
        """Classify the row based on known patterns."""
        # Check known patterns
        if re.match(self.patterns['month_header'], first_cell):
            return "month_header"

        if re.match(self.patterns['month_asterisk'], first_cell):
            return "month_asterisk"
            
        if re.match(self.patterns['show_id'], first_cell):
            return "show_data"
            
        if re.match(self.patterns['end_row'], first_cell):
            return "end_row"
            
        if re.match(self.patterns['summary_line'], first_cell):
            return "summary_line"
            
        # Header row detection
        if "Show ID" in first_cell or "Show Date" in first_cell:
            return "header"

        # If there are many columns and the second looks like a date, assume show data
        if len(row) > 10 and self._is_date_like(row[1]):
            return "show_data"

        return "unknown"
    
    def _is_date_like(self, value):
        """Check if value looks like a date"""
        if not value:
            return False
        try:
            # Try to convert to date
            pd.to_datetime(str(value))
            return True
        except:
            return False
    
    def _extract_show_data(self, row, row_idx, current_month):
        """Extract a structured dictionary for a single show row."""
        try:
            if len(row) < 18:
                logger.warning(
                    "Row %s has %s columns, expected at least 18", row_idx, len(row)
                )
                return None

            show_data = {}

            for col_idx, field_name in self.column_mapping.items():
                try:
                    value = row[col_idx] if col_idx < len(row) else None
                    if field_name == 'sales_to_date':
                        usd_value, currency_code, original_value = self._parse_currency_value(value)
                        show_data['sales_currency'] = currency_code
                        show_data['sales_to_date_local'] = original_value
                        show_data[field_name] = usd_value
                    else:
                        show_data[field_name] = self._clean_cell_value(value, field_name)
                except Exception as e:
                    logger.warning(
                        "Failed to read field %s in row %s: %s", field_name, row_idx, e
                    )
                    show_data[field_name] = None

            show_data['source_row'] = row_idx
            show_data['current_month'] = current_month
            show_data['extraction_date'] = datetime.now().isoformat()

            if not show_data.get('show_id') or not show_data.get('show_name'):
                logger.warning("Row %s missing critical identifiers", row_idx)
                return None

            return show_data

        except Exception as e:
            logger.error("Unexpected error parsing row %s: %s", row_idx, e)
            return None

    def _clean_cell_value(self, value, field_name):
        """Normalise a single cell according to the expected data type."""
        if value is None or value == "":
            return None

        str_value = str(value).strip()

        if field_name in ['capacity', 'venue_holds', 'wheelchair_companions', 'camera',
                         'artists_hold', 'kills', 'yesterday_sales', 'today_sold',
                         'total_sold', 'remaining', 'sold_percentage', 'atp']:
            try:
                cleaned = re.sub(r'[,\s]', '', str_value)
                return float(cleaned) if cleaned else None
            except:
                return None

        if field_name in ['show_date', 'report_date']:
            try:
                return pd.to_datetime(str_value)
            except:
                return None

        return str_value if str_value else None

    def _parse_currency_value(self, value):
        """Convert a currency string into USD using static FX rates."""
        if value is None:
            return None, None, None

        str_value = str(value).strip()
        if not str_value:
            return None, None, None

        # Extract non-numeric characters to infer currency code
        currency_hint = re.sub(r'[0-9.,\-]', '', str_value)
        currency_hint = currency_hint.replace(' ', '').upper()
        currency_code = self.currency_aliases.get(currency_hint)

        if currency_code is None and currency_hint:
            for alias, code in self.currency_aliases.items():
                if alias and alias in currency_hint:
                    currency_code = code
                    break

        if currency_code is None:
            currency_code = 'USD'

        # Remove any non-numeric characters for amount parsing
        numeric_portion = re.sub(r'[^0-9,\.\-]', '', str_value)
        amount = self._parse_numeric_value(numeric_portion)

        if amount is None:
            return None, currency_code, None

        fx_rate = self.currency_to_usd.get(currency_code, 1.0)
        usd_value = amount * fx_rate
        return usd_value, currency_code, amount

    @staticmethod
    def _parse_numeric_value(value: str) -> Optional[float]:
        """Convert a locale-agnostic numeric string into a float."""
        if value is None:
            return None

        text = value.strip()
        if not text:
            return None

        # Handle thousands/decimal separators
        if text.count(',') > 0 and text.count('.') > 0:
            if text.rfind('.') > text.rfind(','):
                text = text.replace(',', '')
            else:
                text = text.replace('.', '').replace(',', '.')
        elif text.count(',') > 0 and text.count('.') == 0:
            text = text.replace('.', '').replace(',', '.')
        else:
            text = text.replace(',', '')

        # Ensure only the first minus is kept
        if text.count('-') > 1:
            text = text.replace('-', '')
        if text.endswith('-'):
            text = '-' + text[:-1]

        try:
            return float(text)
        except ValueError:
            return None

    @staticmethod
    def _latest_per_show(df: pd.DataFrame) -> pd.DataFrame:
        """Return the most recent record for each show based on report_date."""
        if df is None or df.empty:
            return df

        sort_columns = ['show_id']
        if 'report_date' in df.columns:
            sort_columns.append('report_date')

        latest = (
            df.sort_values(sort_columns)
            .drop_duplicates(subset='show_id', keep='last')
        )
        return latest

    def _clean_and_transform(self, df):
        """Apply type conversions, calculated fields, and additional metadata."""
        if df.empty:
            return df

        df = df[df['show_id'].notna() & (df['show_id'] != '')]

        df = self._convert_data_types(df)

        df = self._add_calculated_fields(df)

        df = self._extract_additional_info(df)

        return df.reset_index(drop=True)

    def _convert_data_types(self, df):
        """Coerce raw strings into the correct data types."""
        for col in ['show_date', 'report_date']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        numeric_cols = ['capacity', 'venue_holds', 'wheelchair_companions', 'camera',
                       'artists_hold', 'kills', 'yesterday_sales', 'today_sold',
                       'total_sold', 'remaining', 'sold_percentage', 'atp',
                       'sales_to_date', 'sales_to_date_local']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def _add_calculated_fields(self, df):
        """Add helper columns used throughout the application."""
        df = df.copy()

        df['occupancy_rate'] = np.where(
            df['capacity'] > 0,
            (df['total_sold'] / df['capacity']) * 100,
            0
        )

        df['avg_ticket_price'] = np.where(
            df['total_sold'] > 0,
            df['sales_to_date'] / df['total_sold'],
            0
        )

        df['potential_revenue'] = df['capacity'] * df['avg_ticket_price']
        df['lost_revenue'] = (df['capacity'] - df['total_sold']) * df['avg_ticket_price']

        hold_columns = [
            'venue_holds',
            'wheelchair_companions',
            'camera',
            'artists_hold',
            'kills',
        ]
        df['total_holds'] = df[hold_columns].fillna(0).sum(axis=1)
        df['effective_capacity'] = df['capacity'] - df['total_holds']

        today = pd.Timestamp.today().normalize()
        df['days_to_show'] = np.where(
            df['show_date'].notna(),
            (df['show_date'].dt.normalize() - today).dt.days,
            np.nan,
        )
        df['days_to_show'] = df['days_to_show'].clip(lower=0)

        df['daily_sales_target'] = np.where(
            df['days_to_show'] > 0,
            df['remaining'] / df['days_to_show'],
            df['remaining'],
        )
        df['daily_sales_target'] = df['daily_sales_target'].replace([np.inf, -np.inf], 0)

        df = df.sort_values(['show_id', 'report_date']).reset_index()
        today_sold_filled = df['today_sold'].fillna(0)
        df['sales_last_7_days'] = today_sold_filled.groupby(df['show_id']).transform(
            lambda s: s.rolling(window=7, min_periods=1).sum()
        )
        df['avg_sales_last_7_days'] = today_sold_filled.groupby(df['show_id']).transform(
            lambda s: s.rolling(window=7, min_periods=1).mean()
        )
        df = df.set_index('index').sort_index()

        df['performance_category'] = pd.cut(
            df['occupancy_rate'],
            bins=[0, 50, 75, 90, 100],
            labels=['Underperforming', 'Developing', 'Strong', 'Sold Out'],
            include_lowest=True
        )

        return df
    
    def _extract_additional_info(self, df):
        """Derive helper attributes for show grouping and matching."""
        df['city'] = df['show_name'].str.extract(r'\.([A-Za-z\s]+)', expand=False)
        df['city'] = df['city'].str.strip()

        df['is_multi_show'] = df['show_id'].str.contains(r'_S\d+', na=False)
        df['show_sequence'] = df['show_id'].str.extract(r'_S(\d+)', expand=False)
        df['show_sequence'] = pd.to_numeric(df['show_sequence'], errors='coerce')

        df['city_code'] = df['show_id'].str.extract(r'^([A-Z]{2,3})_', expand=False)

        df['show_date_from_id'] = df['show_id'].str.extract(r'_(\d{4})', expand=False)

        df['normalized_city'] = df['city'].fillna('').str.lower().str.replace(r'[^a-z0-9]', '', regex=True)

        return df

    def get_data_summary(self, df):
        """Return a quick summary used in the sidebar."""
        if df is None or df.empty:
            return {"error": "No data available"}

        latest = self._latest_per_show(df)

        summary = {
            "total_shows": len(latest['show_id'].unique()),
            "unique_cities": latest['city'].nunique() if 'city' in latest.columns else 0,
            "total_capacity": latest['capacity'].sum(),
            "total_sold": latest['total_sold'].sum(),
            "total_revenue": latest['sales_to_date'].sum(),
            "avg_occupancy": latest['occupancy_rate'].mean(),
            "date_range": {
                "start": df['show_date'].min(),
                "end": df['show_date'].max()
            },
            "cities": latest['city'].value_counts().to_dict() if 'city' in latest.columns else {},
            "performance_distribution": latest['performance_category'].value_counts().to_dict() if 'performance_category' in latest.columns else {},
            "data_quality": {
                "complete_records": latest.dropna().shape[0],
                "missing_revenue": latest['sales_to_date'].isnull().sum(),
                "missing_dates": latest['show_date'].isnull().sum()
            },
            "avg_daily_sales_target": latest['daily_sales_target'].mean(skipna=True),
            "avg_sales_last_7_days": latest['avg_sales_last_7_days'].mean(skipna=True),
        }

        return summary
