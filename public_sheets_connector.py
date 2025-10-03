"""Utilities to pull the public Google Sheet with detailed ticket sales data."""

import pandas as pd
import numpy as np
import requests
import csv
from io import StringIO
from datetime import datetime
from typing import Optional
import re
import logging

logger = logging.getLogger(__name__)

class PublicSheetsConnector:
    """Connector responsible for downloading and parsing the public ticket sheet."""
    
    def __init__(self):
        # Public sheet URL (CSV export format)
        self.sheet_id = "1hVm1OALKQ244zuJBQV0SsQT08A2_JTDlPytUNULRofA"
        self.csv_url = f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/export?format=csv&gid=0"

        # Currency handling helpers
        self.currency_symbol_map = {
            "R$": "BRL",
            "€": "EUR",
            "£": "GBP",
            "¥": "JPY",
            "₡": "CRC",
            "C$": "CAD",
            "A$": "AUD",
            "MX$": "MXN",
            "COP$": "COP",
            "CLP$": "CLP",
        }
        self.default_exchange_rates = {
            "USD": 1.0,
            "BRL": 5.0,
            "EUR": 0.92,
            "GBP": 0.79,
            "CAD": 1.36,
            "AUD": 1.5,
            "MXN": 16.8,
            "CRC": 515.0,
            "JPY": 151.0,
            "COP": 3920.0,
            "CLP": 925.0,
        }
        self.exchange_rates = None
        self.exchange_rates_last_updated = None

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

        # Patterns used to classify each row in the CSV export
        self.patterns = {
            'month_header': r'^(September|October|November|December)$',
            'month_asterisk': r'^\*(September|October|November|December)\*$',
            'show_id': r'^[A-Z]{2,3}_\d{4}(_S\d+)?$',  # Ex: WDC_0927, WDC_0927_S3
            'end_row': r'^endRow$',
            'summary_line': r'^\d+\s*\(\+\d+\)\s*\d+',  # Ex: "1371 (+8) 1379"
            'date_format': r'^\d{4}-\d{2}-\d{2}$'
        }
    
    def load_data(self):
        """Download the public sheet and return a cleaned DataFrame."""
        try:
            # Download CSV content
            response = requests.get(self.csv_url, timeout=30)
            response.raise_for_status()

            self._ensure_exchange_rates()

            # Parse CSV
            csv_data = StringIO(response.text)
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

            elif line_type in ["month_asterisk", "end_row", "header"]:
                if line_type == "end_row":
                    logger.info("Encountered endRow marker at row %s. Stopping parse.", row_idx)
                    break
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
        """Verifica se valor parece uma data"""
        if not value:
            return False
        try:
            # Tentar converter para data
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

        if field_name in ['sales_to_date']:
            amount = self._parse_numeric_amount(str_value)
            if amount is None:
                return None
            currency_code = self._detect_currency_code(str_value)
            return self._convert_to_usd(amount, currency_code)

        if field_name in ['capacity', 'venue_holds', 'wheelchair_companions', 'camera',
                         'artists_hold', 'kills', 'yesterday_sales', 'today_sold',
                         'total_sold', 'remaining', 'sold_percentage', 'atp']:
            return self._parse_numeric_amount(str_value)

        if field_name in ['show_date', 'report_date']:
            try:
                return pd.to_datetime(str_value)
            except:
                return None

        return str_value if str_value else None
    
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
                       'total_sold', 'remaining', 'sold_percentage', 'atp', 'sales_to_date']
        
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

        report_rank = (
            df['report_date']
            .fillna(pd.Timestamp.min)
            .groupby(df['show_id'])
            .rank(method='first')
        )
        df['is_latest_snapshot'] = report_rank.groupby(df['show_id']).transform(
            lambda s: s == s.max()
        )

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

        df['is_multi_show'] = df['show_id'].str.contains('_S\d+', na=False)
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

        latest = self._latest_snapshots(df)

        summary = {
            "total_shows": len(latest),
            "unique_cities": latest['city'].nunique() if 'city' in latest.columns else 0,
            "total_capacity": latest['capacity'].sum(),
            "total_sold": latest['total_sold'].sum(),
            "total_revenue": latest['sales_to_date'].sum(),
            "avg_occupancy": latest['occupancy_rate'].mean(),
            "date_range": {
                "start": latest['show_date'].min(),
                "end": latest['show_date'].max()
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

    def _ensure_exchange_rates(self):
        """Fetch exchange rates (USD base) with caching and fallbacks."""
        if (
            self.exchange_rates is not None
            and self.exchange_rates_last_updated is not None
            and (datetime.utcnow() - self.exchange_rates_last_updated).total_seconds() < 6 * 3600
        ):
            return

        try:
            response = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10)
            response.raise_for_status()
            payload = response.json()
            if payload.get("result") == "success" and "rates" in payload:
                self.exchange_rates = payload["rates"]
                self.exchange_rates_last_updated = datetime.utcnow()
                logger.info("Exchange rates refreshed from remote API.")
                return
            else:
                logger.warning("Unexpected exchange rate payload structure: %s", payload)
        except Exception as exc:
            logger.warning("Failed to refresh exchange rates: %s", exc)

        if self.exchange_rates is None:
            self.exchange_rates = self.default_exchange_rates.copy()
            self.exchange_rates_last_updated = datetime.utcnow()
            logger.info("Using default exchange rates fallback.")

    def _detect_currency_code(self, raw_value: str) -> str:
        """Identify the currency code based on symbols or explicit codes."""
        for symbol, code in self.currency_symbol_map.items():
            if symbol in raw_value:
                return code

        match = re.search(r"([A-Z]{3})", raw_value)
        if match:
            code = match.group(1).upper()
            if code in self.default_exchange_rates:
                return code

        return "USD"

    def _parse_numeric_amount(self, raw_value: str) -> float:
        """Parse a numeric string handling thousands separators and decimals."""
        if raw_value is None:
            return None

        value = str(raw_value).strip().replace("\u00a0", "").replace("\u202f", "")
        cleaned = re.sub(r"[^0-9,.-]", "", value)

        if cleaned.count(",") and cleaned.count("."):
            if cleaned.rfind(".") > cleaned.rfind(","):
                cleaned = cleaned.replace(",", "")
            else:
                cleaned = cleaned.replace(".", "").replace(",", ".")
        elif cleaned.count(",") == 1 and cleaned.count(".") == 0:
            integer_part, fractional_part = cleaned.split(",")
            if len(fractional_part) in {1, 2}:
                cleaned = f"{integer_part.replace(',', '')}.{fractional_part}"
            else:
                cleaned = cleaned.replace(",", "")
        else:
            cleaned = cleaned.replace(",", "")

        try:
            return float(cleaned)
        except (TypeError, ValueError):
            logger.debug("Failed to parse numeric amount from '%s'", raw_value)
            return None

    def _convert_to_usd(self, amount: float, currency_code: str) -> Optional[float]:
        """Convert the provided amount into USD using cached exchange rates."""
        if amount is None:
            return None

        currency_code = (currency_code or "USD").upper()
        if currency_code == "USD":
            return amount

        self._ensure_exchange_rates()
        rates = self.exchange_rates or {}
        rate = rates.get(currency_code)
        if not rate:
            rate = self.default_exchange_rates.get(currency_code)

        if not rate or rate == 0:
            logger.warning("Missing exchange rate for %s. Leaving amount unchanged.", currency_code)
            return amount

        return amount / rate

    def _latest_snapshots(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return one record per show using the most recent snapshot."""
        if df is None or df.empty:
            return df

        sort_columns = [col for col in ["show_id", "report_date", "extraction_date"] if col in df.columns]
        if not sort_columns:
            return df.drop_duplicates("show_id", keep="last")

        sorted_df = df.sort_values(sort_columns)
        latest = sorted_df.drop_duplicates("show_id", keep="last")
        return latest.reset_index(drop=True)

    def create_sample_ads_data_mapping(self, df):
        """Create helper mappings to connect sales data with sample ad structures."""
        if df is None or df.empty:
            return {}

        mapping = {
            "campaign_mapping": {
                city: {
                    "campaign_name": f"Tour_{city}_2025",
                    "shows": df[df['city'] == city]['show_id'].tolist(),
                    "total_capacity": df[df['city'] == city]['capacity'].sum(),
                    "total_sold": df[df['city'] == city]['total_sold'].sum(),
                    "revenue": df[df['city'] == city]['sales_to_date'].sum(),
                    "occupancy_rate": df[df['city'] == city]['occupancy_rate'].mean()
                }
                for city in df['city'].dropna().unique()
            },
            "date_mapping": {
                date.strftime('%Y-%m-%d'): {
                    "shows_count": len(group),
                    "total_sold": group['today_sold'].sum(),
                    "revenue": group['sales_to_date'].sum()
                }
                for date, group in df.groupby('show_date') if pd.notna(date)
            },
            "join_keys": {
                "by_city": "city",
                "by_date": "show_date", 
                "by_campaign": "campaign_name",
                "by_show_id": "show_id"
            },
            "sample_ads_structure": {
                "expected_columns": [
                    "date", "campaign_name", "impressions", "clicks", 
                    "spend", "conversions", "ctr", "cpc", "cpa"
                ],
                "date_format": "YYYY-MM-DD",
                "campaign_pattern": "Tour_{city}_2025"
            }
        }
        
        return mapping
