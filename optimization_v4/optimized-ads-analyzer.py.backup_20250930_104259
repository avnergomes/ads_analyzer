"""Streamlit application for integrated ad and ticket sales analytics - Optimized v4.0"""

from __future__ import annotations
import importlib.util
import io
import re
import warnings
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, Iterable, List, Optional, Tuple
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from public_sheets_connector import PublicSheetsConnector

warnings.filterwarnings("ignore")
HAS_STATSMODELS = importlib.util.find_spec("statsmodels") is not None

# Page config
st.set_page_config(
    page_title="Ads Performance Analyzer v4.0",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better visuals
st.markdown("""
<style>
    .health-indicator {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 8px;
        border-left: 3px solid #667eea;
    }
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e3e3e3;
        border-radius: 8px;
        padding: 12px;
        margin: 4px 0;
    }
    .plot-container {
        background: white;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

@dataclass
class FunnelSummary:
    """Aggregated funnel metrics for a single show."""
    show_id: str
    spend: float
    impressions: float
    clicks: float
    lp_views: float
    add_to_cart: float
    purchases: float

    @property
    def clicks_per_ticket(self) -> float:
        return self.clicks / self.purchases if self.purchases else 0.0

    @property
    def lp_views_per_ticket(self) -> float:
        return self.lp_views / self.purchases if self.purchases else 0.0

    @property
    def add_to_cart_per_ticket(self) -> float:
        return self.add_to_cart / self.purchases if self.purchases else 0.0

class AdsDataProcessor:
    """Handles ad data ingestion, normalization, and enrichment - Enhanced version."""
    
    def __init__(self):
        # Enhanced column detection - position-based fallback
        self.column_positions = {
            'days': {
                0: 'date', 1: 'campaign_name', 2: 'ad_set_name', 3: 'ad_name',
                4: 'impressions', 5: 'reach', 6: 'frequency', 7: 'clicks', 
                8: 'spend', 9: 'ctr', 10: 'cpc', 11: 'cpm'
            },
            'days_placement_device': {
                0: 'date', 1: 'campaign_name', 2: 'ad_set_name', 3: 'placement',
                4: 'device_platform', 5: 'impressions', 6: 'clicks', 7: 'spend'
            },
            'days_time': {
                0: 'date', 1: 'campaign_name', 2: 'ad_set_name', 3: 'time_of_day',
                4: 'impressions', 5: 'clicks', 6: 'spend'
            }
        }
        
        self.standard_column_aliases: Dict[str, List[str]] = {
            "date": ["reporting_starts", "date", "day", "date_start", "created_time"],
            "campaign_name": ["campaign_name", "campaign", "campaign id"],
            "ad_set_name": ["ad_set_name", "ad set name", "adset name"],
            "ad_name": ["ad_name", "ad name"],
            "impressions": ["impressions", "impression"],
            "reach": ["reach", "unique_reach"],
            "frequency": ["frequency"],
            "clicks": ["clicks", "link_clicks", "link clicks", "outbound_clicks"],
            "spend": ["spend", "amount_spent", "amount spent", "amount spent (usd)", "cost"],
            "ctr": ["ctr", "ctr (link)", "click_through_rate", "link_click_through_rate"],
            "cpc": ["cpc", "cost_per_click", "cost per link click"],
            "cpm": ["cpm", "cpm (cost per 1,000 impressions)", "cost per 1,000 impressions"],
            "results": ["results", "result", "conversions", "purchases"],
            "result_indicator": ["result_indicator", "result indicator", "action_type"],
            "placement": ["placement", "publisher_platform"],
            "device_platform": ["device platform", "device_platform", "impression_device"],
            "time_of_day": ["time of day (viewer's time zone)", "time", "hour"]
        }

        # Enhanced funnel column detection - multiple variations
        self.funnel_column_aliases: Dict[str, List[str]] = {
            "lp_views": [
                "f1", "fun1", "lpviews", "lp_views", "lpviews_f1", "lpviews_fun1",
                "landingpageviews", "landing_page_views", "landing page view",
                "actions:landing_page_view", "website_landing_page_views"
            ],
            "add_to_cart": [
                "f2", "fun2", "addtocart", "add_to_cart", "addtocart_f2", "addtocart_fun2",
                "initiated_checkout", "initiate_checkout", "adds_to_cart",
                "actions:offsite_conversion.fb_pixel_add_to_cart", "website_adds_to_cart"
            ],
            "purchases": [
                "f3", "fun3", "conv_addtocart", "conv_f3", "purchases", "purchases_f3",
                "orders", "tickets_sold", "conversions", "website_purchases",
                "actions:offsite_conversion.fb_pixel_purchase", "purchase"
            ]
        }

        # Enhanced legacy naming patterns
        self.legacy_patterns = [
            (r'US-([A-Z]{2,})-Sales-\d{4}\s*-\s*(Interest|Target)\s*-?\s*(\d+)?', 'legacy_full'),
            (r'([A-Z]{2,})-Sales-\d{4}.*?(Interest|Target)', 'legacy_short'),
            (r'Tour[_\s]+([A-Za-z]+)[_\s]+(\d+)', 'tour_format'),
            (r'([A-Z]{2,3})_\d{4}', 'show_id_direct')
        ]

    def detect_and_normalize_columns(self, df: pd.DataFrame, file_type: str = None) -> pd.DataFrame:
        """Enhanced column detection with position-based fallback."""
        if df is None or df.empty:
            return df
            
        normalized_df = df.copy()
        
        # Try position-based detection first if file type is known
        if file_type and file_type in self.column_positions:
            pos_map = self.column_positions[file_type]
            for pos, col_name in pos_map.items():
                if pos < len(normalized_df.columns):
                    current_col = normalized_df.columns[pos]
                    if self._is_likely_column_type(normalized_df.iloc[:, pos], col_name):
                        normalized_df.rename(columns={current_col: col_name}, inplace=True)
        
        # Then apply alias-based detection
        col_map: Dict[str, str] = {}
        normalized_existing = {
            self._normalize_column_name(col): col for col in normalized_df.columns
        }
        
        for standard, aliases in self.standard_column_aliases.items():
            if standard not in normalized_df.columns:
                for alias in aliases:
                    normalized_alias = self._normalize_column_name(alias)
                    if normalized_alias in normalized_existing:
                        col_map[normalized_existing[normalized_alias]] = standard
                        break
        
        if col_map:
            normalized_df.rename(columns=col_map, inplace=True)
            
        return normalized_df

    def _is_likely_column_type(self, series: pd.Series, expected_type: str) -> bool:
        """Check if column data matches expected type."""
        sample = series.dropna().head(10)
        if sample.empty:
            return False
            
        if expected_type == 'date':
            try:
                pd.to_datetime(sample, errors='coerce').notna().sum() > len(sample) * 0.5
                return True
            except:
                return False
                
        elif expected_type in ['impressions', 'clicks', 'spend']:
            try:
                pd.to_numeric(sample, errors='coerce').notna().sum() > len(sample) * 0.5
                return True
            except:
                return False
                
        elif expected_type in ['campaign_name', 'ad_set_name']:
            return sample.astype(str).str.len().mean() > 5
            
        return True

    @staticmethod
    def _normalize_column_name(col: str) -> str:
        return re.sub(r'[^a-z0-9]', '', col.lower())

    def identify_dataset_type(self, df: pd.DataFrame) -> Optional[str]:
        """Enhanced dataset type identification."""
        if df is None or df.empty:
            return None
            
        cols = df.columns.tolist()
        normalized = {self._normalize_column_name(c) for c in cols}
        
        # Check by unique column combinations
        if any(t in normalized for t in ["timeofday", "timeofdayviewerstimezone", "hour"]):
            return "days_time"
        elif any(p in normalized for p in ["placement", "platform", "publisherplatform"]) and \
             any(d in normalized for d in ["deviceplatform", "impressiondevice", "device"]):
            return "days_placement_device"
        elif "date" in normalized or "reportingstarts" in normalized:
            # Check if it's the main days report by exclusion
            if not any(x in normalized for x in ["placement", "timeofday", "hour", "device"]):
                return "days"
                
        # Fallback: check column count and patterns
        if len(cols) > 15:
            return "days"
        elif len(cols) > 10:
            return "days_placement_device"
        else:
            return "days_time"

    def normalize_funnel_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enhanced funnel column normalization with multiple pattern matching."""
        if df is None or df.empty:
            return df
            
        # First check for columns by alias
        normalized_columns = {
            self._normalize_column_name(col): col for col in df.columns
        }
        
        for target, aliases in self.funnel_column_aliases.items():
            found = False
            for alias in aliases:
                normalized_alias = self._normalize_column_name(alias)
                if normalized_alias in normalized_columns:
                    source_col = normalized_columns[normalized_alias]
                    if target not in df.columns:
                        df[target] = pd.to_numeric(df[source_col], errors='coerce').fillna(0)
                    found = True
                    break
                    
            if not found and target not in df.columns:
                df[target] = 0
        
        # Handle result_indicator patterns
        if "result_indicator" in df.columns and "results" in df.columns:
            df["results"] = pd.to_numeric(df["results"], errors='coerce')
            
            for indicator_val in df["result_indicator"].dropna().unique():
                indicator_lower = str(indicator_val).lower()
                
                if any(kw in indicator_lower for kw in ["landing", "lpview", "f1"]):
                    mask = df["result_indicator"] == indicator_val
                    df.loc[mask, "lp_views"] = df.loc[mask, "results"]
                    
                elif any(kw in indicator_lower for kw in ["cart", "checkout", "f2"]):
                    mask = df["result_indicator"] == indicator_val
                    df.loc[mask, "add_to_cart"] = df.loc[mask, "results"]
                    
                elif any(kw in indicator_lower for kw in ["purchase", "conversion", "f3", "order"]):
                    mask = df["result_indicator"] == indicator_val
                    df.loc[mask, "purchases"] = df.loc[mask, "results"]
        
        return df

    def _extract_show_id_enhanced(self, text: str) -> Optional[str]:
        """Enhanced show ID extraction with multiple patterns."""
        if not text:
            return None
            
        text_upper = text.upper()
        
        # Direct show ID patterns
        patterns = [
            r'([A-Z]{2,3}_\d{4}(?:_S\d+)?)',  # WDC_0927_S2
            r'([A-Z]{2,3})\s*_\s*(\d{4})(?:\s*_\s*S(\d+))?',  # WDC _ 0927 _ S2
            r'([A-Z]{2,3})-(\d{4})(?:-S(\d+))?',  # WDC-0927-S2
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_upper)
            if match:
                if len(match.groups()) > 1:
                    # Reconstruct from parts
                    parts = [g for g in match.groups() if g]
                    return '_'.join(parts)
                return match.group(1)
        
        return None

    def _match_show_identifier_enhanced(
        self, row: pd.Series, show_lookup: Dict[str, Dict[int, str]]
    ) -> Optional[str]:
        """Enhanced show matching with fallback strategies."""
        # Try all text fields
        text_candidates = [
            str(row.get("campaign_name", "")),
            str(row.get("ad_set_name", "")),
            str(row.get("ad_name", ""))
        ]
        
        for text in text_candidates:
            if not text or text == "nan":
                continue
                
            # Direct show ID extraction
            show_id = self._extract_show_id_enhanced(text)
            if show_id:
                return show_id
        
        # Legacy format matching
        merged_text = " ".join(text_candidates)
        
        for pattern, pattern_type in self.legacy_patterns:
            match = re.search(pattern, merged_text, re.IGNORECASE)
            if match:
                if pattern_type == 'legacy_full':
                    city = match.group(1)
                    show_num = match.group(3) if len(match.groups()) >= 3 else "1"
                    return self._lookup_by_city_and_sequence(city, show_num, show_lookup)
                    
                elif pattern_type == 'tour_format':
                    city = match.group(1)
                    show_num = match.group(2) if len(match.groups()) >= 2 else "1"
                    return self._lookup_by_city_and_sequence(city, show_num, show_lookup)
        
        # Fallback to fuzzy city matching
        return self._fallback_show_match(merged_text, show_lookup)

    def _lookup_by_city_and_sequence(
        self, city: str, sequence: str, show_lookup: Dict[str, Dict[int, str]]
    ) -> Optional[str]:
        """Lookup show by city and sequence number."""
        if not show_lookup:
            return None
            
        city_normalized = self._normalize_text(city)
        try:
            seq_num = int(sequence) if sequence else 1
        except:
            seq_num = 1
            
        for city_key, sequences in show_lookup.items():
            if city_key and city_normalized in city_key:
                if seq_num in sequences:
                    return sequences[seq_num]
                # Return first available if sequence not found
                return next(iter(sequences.values())) if sequences else None
                
        return None

    def _normalize_text(self, text: str) -> str:
        return re.sub(r'[^a-z0-9]', '', text.lower()) if text else ""

    def _fallback_show_match(
        self, text: str, show_lookup: Dict[str, Dict[int, str]]
    ) -> Optional[str]:
        """Enhanced fallback matching with fuzzy logic."""
        if not show_lookup or not text:
            return None
            
        normalized_text = self._normalize_text(text)
        
        # Extract sequence number from various patterns
        sequence = 1
        seq_patterns = [
            r'#\s*(\d{1,2})',
            r'\b(?:show|s)(\d{1,2})\b',
            r'(?:2nd|second)',  # Map to 2
            r'(?:3rd|third)',   # Map to 3
            r'(?:4th|fourth)',  # Map to 4
        ]
        
        for i, pattern in enumerate(seq_patterns):
            match = re.search(pattern, text.lower())
            if match:
                if i <= 1:
                    sequence = int(match.group(1))
                elif i == 2:
                    sequence = 2
                elif i == 3:
                    sequence = 3
                elif i == 4:
                    sequence = 4
                break
        
        # Try each city in lookup
        best_match = None
        best_score = 0
        
        for city_key, sequences in show_lookup.items():
            if not city_key:
                continue
                
            # Calculate match score
            score = 0
            if city_key in normalized_text:
                score = len(city_key)
                
            if score > best_score:
                best_score = score
                if sequence in sequences:
                    best_match = sequences[sequence]
                else:
                    best_match = next(iter(sequences.values())) if sequences else None
        
        return best_match

    def process_ads_files(
        self, uploaded_files: List, sales_df: pd.DataFrame
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, FunnelSummary]]:
        """Process uploaded ad files with enhanced parsing."""
        data_by_type: Dict[str, pd.DataFrame] = {}
        read_errors: List[str] = []
        
        for uploaded in uploaded_files:
            try:
                content = uploaded.read()
                buffer = io.BytesIO(content)
                
                # Read file
                if uploaded.name.lower().endswith(".csv"):
                    df = pd.read_csv(buffer)
                else:
                    df = pd.read_excel(buffer)
                
                # Identify dataset type first
                dataset_type = self.identify_dataset_type(df)
                
                # Normalize with type hint
                df = self.detect_and_normalize_columns(df, dataset_type)
                df = self.calculate_missing_kpis(df)
                df = self.normalize_funnel_columns(df)
                
                if dataset_type is None:
                    # Try to infer from filename
                    if "time" in uploaded.name.lower():
                        dataset_type = "days_time"
                    elif "placement" in uploaded.name.lower() or "device" in uploaded.name.lower():
                        dataset_type = "days_placement_device"
                    else:
                        dataset_type = "days"
                
                df["source_file"] = uploaded.name
                
                # Store by type
                if dataset_type in data_by_type:
                    # Append if already exists
                    data_by_type[dataset_type] = pd.concat(
                        [data_by_type[dataset_type], df], 
                        ignore_index=True
                    )
                else:
                    data_by_type[dataset_type] = df
                    
            except Exception as exc:
                read_errors.append(f"{uploaded.name}: {exc}")
        
        # Check for required types
        required_types = {"days", "days_placement_device", "days_time"}
        missing_types = required_types - data_by_type.keys()
        
        if missing_types and len(data_by_type) > 0:
            st.warning(f"Missing reports: {', '.join(missing_types)}. Some features may be limited.")
        
        if read_errors:
            st.error("Failed to process: " + ", ".join(read_errors))
        
        # Process main days data
        if "days" in data_by_type:
            enriched_days = self.enrich_ads_dataframe(data_by_type["days"], sales_df)
            data_by_type["days"] = enriched_days
            funnel_summary = self.calculate_funnel_summary(enriched_days)
        else:
            funnel_summary = {}
        
        return data_by_type, funnel_summary

    def calculate_missing_kpis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate missing KPIs from available data."""
        if df is None or df.empty:
            return df
            
        # Convert to numeric
        numeric_cols = [
            "impressions", "reach", "frequency", "clicks", "spend",
            "ctr", "cpc", "cpm", "results", "lp_views", "add_to_cart", "purchases"
        ]
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        
        # Calculate missing metrics
        if "impressions" in df.columns and "clicks" in df.columns:
            if "ctr" not in df.columns or df["ctr"].isna().all():
                df["ctr"] = np.where(
                    df["impressions"] > 0,
                    (df["clicks"] / df["impressions"]) * 100,
                    0
                )
        
        if "spend" in df.columns and "clicks" in df.columns:
            if "cpc" not in df.columns or df["cpc"].isna().all():
                df["cpc"] = np.where(df["clicks"] > 0, df["spend"] / df["clicks"], 0)
        
        if "spend" in df.columns and "impressions" in df.columns:
            if "cpm" not in df.columns or df["cpm"].isna().all():
                df["cpm"] = np.where(
                    df["impressions"] > 0,
                    (df["spend"] / df["impressions"]) * 1000,
                    0
                )
        
        return df

    def enrich_ads_dataframe(
        self, df: pd.DataFrame, sales_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Enrich ads data with show matching."""
        if df is None or df.empty:
            return df
            
        df = df.copy()
        
        # Parse dates
        date_cols = ["date", "reporting_starts", "day", "created_time"]
        for col in date_cols:
            if col in df.columns:
                df["date"] = pd.to_datetime(df[col], errors="coerce")
                break
        
        # Build show lookup
        show_lookup = self._build_show_lookup(sales_df)
        
        # Match shows
        df["matched_show_id"] = df.apply(
            lambda row: self._match_show_identifier_enhanced(row, show_lookup),
            axis=1
        )
        
        # Add match confidence
        df["match_confidence"] = df["matched_show_id"].apply(
            lambda x: "high" if x and "_" in x else "low" if x else "none"
        )
        
        return df

    def _build_show_lookup(self, sales_df: pd.DataFrame) -> Dict[str, Dict[int, str]]:
        """Build lookup dictionary from sales data."""
        lookup: Dict[str, Dict[int, str]] = {}
        
        if sales_df is None or sales_df.empty:
            return lookup
            
        temp = sales_df.copy()
        temp["normalized_city"] = temp["city"].fillna("").apply(self._normalize_text)
        temp["sequence"] = temp["show_sequence"].fillna(1).astype(int)
        
        for _, row in temp.iterrows():
            city_key = row["normalized_city"]
            if not city_key:
                continue
            lookup.setdefault(city_key, {})[row["sequence"]] = row["show_id"]
            
        return lookup

    def calculate_funnel_summary(self, df: pd.DataFrame) -> Dict[str, FunnelSummary]:
        """Calculate funnel summary by show."""
        if df is None or df.empty:
            return {}
            
        # Ensure columns exist
        required_cols = [
            "matched_show_id", "spend", "impressions", "clicks",
            "lp_views", "add_to_cart", "purchases"
        ]
        
        for col in required_cols:
            if col not in df.columns:
                df[col] = 0
        
        # Group by show
        grouped = df.groupby("matched_show_id", dropna=True).agg({
            "spend": "sum",
            "impressions": "sum", 
            "clicks": "sum",
            "lp_views": "sum",
            "add_to_cart": "sum",
            "purchases": "sum"
        })
        
        result: Dict[str, FunnelSummary] = {}
        
        for show_id, row in grouped.iterrows():
            if not show_id:
                continue
            result[show_id] = FunnelSummary(
                show_id=show_id,
                spend=float(row.get("spend", 0) or 0),
                impressions=float(row.get("impressions", 0) or 0),
                clicks=float(row.get("clicks", 0) or 0),
                lp_views=float(row.get("lp_views", 0) or 0),
                add_to_cart=float(row.get("add_to_cart", 0) or 0),
                purchases=float(row.get("purchases", 0) or 0)
            )
            
        return result

class IntegratedDashboard:
    """Enhanced dashboard with improved visualizations."""
    
    def __init__(self):
        self.sales_data: Optional[pd.DataFrame] = None
        self.ads_data_by_type: Dict[str, pd.DataFrame] = {}
        self.funnel_summary: Dict[str, FunnelSummary] = {}

    def render_show_health_indicators(
        self, show_id: str, sales_df: pd.DataFrame, funnel: Optional[FunnelSummary]
    ) -> None:
        """Render 3-5 quick visual health indicators at the top."""
        
        if sales_df is None or sales_df.empty:
            return
            
        show_records = sales_df[sales_df["show_id"] == show_id].sort_values("report_date")
        
        if show_records.empty:
            st.info("No data available for this show.")
            return
            
        latest = show_records.iloc[-1]
        
        # Calculate health metrics
        occupancy = latest.get("occupancy_rate", 0)
        days_to_show = max((latest["show_date"].date() - date.today()).days, 0)
        remaining = latest.get("remaining", 0)
        daily_target = remaining / max(days_to_show, 1)
        avg_sales_7d = latest.get("avg_sales_last_7_days", 0)
        
        # Calculate performance score
        pace_score = min(100, (avg_sales_7d / daily_target * 100)) if daily_target > 0 else 0
        
        # Funnel efficiency
        funnel_efficiency = 0
        if funnel:
            if funnel.clicks > 0:
                funnel_efficiency = (funnel.purchases / funnel.clicks) * 100
        
        # Create visual indicators
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=occupancy,
                title={'text': "Occupancy %"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': self._get_color_by_value(occupancy, [50, 75, 90])},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 75], 'color': "#ffeaa7"},
                        {'range': [75, 90], 'color': "#fdcb6e"},
                        {'range': [90, 100], 'color': "#6c5ce7"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True, key="gauge1")
        
        with col2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=pace_score,
                title={'text': "Sales Pace"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': self._get_color_by_value(pace_score, [50, 75, 100])},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 75], 'color': "#ffeaa7"},
                        {'range': [75, 100], 'color': "#55efc4"}
                    ]
                }
            ))
            fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True, key="gauge2")
        
        with col3:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=funnel_efficiency,
                title={'text': "Funnel Efficiency %"},
                number={'suffix': "%"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [None, 10]},
                    'bar': {'color': self._get_color_by_value(funnel_efficiency, [1, 3, 5])},
                    'steps': [
                        {'range': [0, 1], 'color': "lightgray"},
                        {'range': [1, 3], 'color': "#ffeaa7"},
                        {'range': [3, 5], 'color': "#fdcb6e"},
                        {'range': [5, 10], 'color': "#00b894"}
                    ]
                }
            ))
            fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True, key="gauge3")
        
        with col4:
            # Days countdown
            color = "red" if days_to_show < 7 else "orange" if days_to_show < 14 else "green"
            fig = go.Figure(go.Indicator(
                mode="number+delta",
                value=days_to_show,
                title={'text': "Days to Show"},
                delta={'reference': 30, 'relative': False},
                domain={'x': [0, 1], 'y': [0, 1]}
            ))
            fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True, key="gauge4")
        
        with col5:
            # ROAS indicator
            roas = 0
            if funnel and funnel.spend > 0:
                revenue = latest.get("sales_to_date", 0)
                roas = revenue / funnel.spend
            
            fig = go.Figure(go.Indicator(
                mode="number",
                value=roas,
                title={'text': "ROAS"},
                number={'prefix': "", 'valueformat': ".2f"},
                domain={'x': [0, 1], 'y': [0, 1]}
            ))
            fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True, key="gauge5")

    def _get_color_by_value(self, value: float, thresholds: List[float]) -> str:
        """Get color based on value and thresholds."""
        colors = ["#e74c3c", "#f39c12", "#f1c40f", "#27ae60"]
        for i, threshold in enumerate(thresholds):
            if value <= threshold:
                return colors[i]
        return colors[-1]

    def render_show_health(
        self, df: pd.DataFrame, funnel_summary: Dict[str, FunnelSummary]
    ) -> None:
        """Enhanced show health dashboard with visual indicators."""
        
        if df is None or df.empty:
            return
            
        st.subheader("🩺 Show Health Dashboard")
        
        shows = df.sort_values(["show_date", "show_id"])["show_id"].unique()
        if len(shows) == 0:
            return
            
        selected_show = st.selectbox("Select a show", shows, key="show_selector")
        
        # Render health indicators at the top
        self.render_show_health_indicators(selected_show, df, funnel_summary.get(selected_show))
        
        st.markdown("---")
        
        # Get show data
        show_records = df[df["show_id"] == selected_show].sort_values("report_date")
        if show_records.empty:
            return
            
        latest = show_records.iloc[-1]
        funnel = funnel_summary.get(selected_show)
        
        # Key metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Capacity",
                f"{int(latest.get('capacity', 0)):,}",
                delta=f"{int(latest.get('remaining', 0)):,} remaining"
            )
            
        with col2:
            st.metric(
                "Tickets Sold",
                f"{int(latest.get('total_sold', 0)):,}",
                delta=f"{int(latest.get('today_sold', 0)):,} today"
            )
            
        with col3:
            st.metric(
                "Revenue",
                f"${latest.get('sales_to_date', 0):,.0f}",
                delta=f"${latest.get('avg_ticket_price', 0):.0f} avg ticket"
            )
            
        with col4:
            daily_target = latest.get('remaining', 0) / max(latest.get('days_to_show', 1), 1)
            st.metric(
                "Daily Target",
                f"{daily_target:.0f}",
                delta=f"{latest.get('avg_sales_last_7_days', 0):.0f} avg 7d"
            )
        
        # Budget input for ticket cost calculation
        st.markdown("### 💰 Budget & Cost Analysis")
        col1, col2 = st.columns([1, 3])
        
        with col1:
            session_key = "show_budgets"
            st.session_state.setdefault(session_key, {})
            existing_budget = st.session_state[session_key].get(
                selected_show, 
                float(funnel.spend if funnel else 0)
            )
            
            budget_input = st.number_input(
                "Show Budget ($)",
                min_value=0.0,
                value=float(existing_budget or 0.0),
                step=1000.0,
                help="Enter total budget for this show to calculate ticket cost"
            )
            st.session_state[session_key][selected_show] = budget_input
        
        with col2:
            if budget_input > 0 and latest.get('total_sold', 0) > 0:
                ticket_cost = budget_input / latest['total_sold']
                col2_1, col2_2, col2_3 = st.columns(3)
                
                with col2_1:
                    st.metric("Ticket Cost", f"${ticket_cost:.2f}")
                
                with col2_2:
                    if funnel and funnel.spend > 0:
                        daily_cpa = funnel.spend / latest['total_sold']
                        st.metric("Daily Sales CPA", f"${daily_cpa:.2f}")
                    
                with col2_3:
                    if funnel:
                        st.metric("Total Ad Spend", f"${funnel.spend:,.0f}")
        
        # Funnel metrics
        if funnel:
            st.markdown("### 🔄 Funnel Performance")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Clicks per Ticket",
                    f"{funnel.clicks_per_ticket:.1f}" if funnel.clicks_per_ticket else "—"
                )
                
            with col2:
                st.metric(
                    "LP Views per Ticket",
                    f"{funnel.lp_views_per_ticket:.1f}" if funnel.lp_views_per_ticket else "—"
                )
                
            with col3:
                st.metric(
                    "Add to Cart per Ticket",
                    f"{funnel.add_to_cart_per_ticket:.1f}" if funnel.add_to_cart_per_ticket else "—"
                )
                
            with col4:
                conv_rate = (funnel.purchases / funnel.clicks * 100) if funnel.clicks > 0 else 0
                st.metric(
                    "Conversion Rate",
                    f"{conv_rate:.2f}%" if conv_rate else "—"
                )
        
        # Visualizations
        st.markdown("### 📊 Performance Trends")
        
        tab1, tab2, tab3 = st.tabs(["Sales Trajectory", "Funnel Analysis", "Daily Rhythm"])
        
        with tab1:
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=("Revenue & Tickets Trend", "Daily Sales Pattern"),
                row_heights=[0.6, 0.4],
                specs=[[{"secondary_y": True}], [{"secondary_y": False}]]
            )
            
            # Revenue and tickets
            fig.add_trace(
                go.Scatter(
                    x=show_records["report_date"],
                    y=show_records["sales_to_date"],
                    mode="lines+markers",
                    name="Revenue",
                    line=dict(color="#3498db", width=3),
                    marker=dict(size=8)
                ),
                row=1, col=1, secondary_y=False
            )
            
            fig.add_trace(
                go.Scatter(
                    x=show_records["report_date"],
                    y=show_records["total_sold"],
                    mode="lines+markers",
                    name="Tickets Sold",
                    line=dict(color="#e74c3c", width=3),
                    marker=dict(size=8)
                ),
                row=1, col=1, secondary_y=True
            )
            
            # Daily sales
            fig.add_trace(
                go.Bar(
                    x=show_records.tail(14)["report_date"],
                    y=show_records.tail(14)["today_sold"],
                    name="Daily Sales",
                    marker_color=show_records.tail(14)["today_sold"].apply(
                        lambda x: "#27ae60" if x > daily_target else "#e74c3c"
                    )
                ),
                row=2, col=1
            )
            
            # Add target line
            fig.add_hline(
                y=daily_target, 
                line_dash="dash",
                line_color="orange",
                annotation_text="Daily Target",
                row=2, col=1
            )
            
            fig.update_layout(height=600, showlegend=True, hovermode='x unified')
            fig.update_yaxes(title_text="Revenue ($)", row=1, col=1, secondary_y=False)
            fig.update_yaxes(title_text="Tickets", row=1, col=1, secondary_y=True)
            fig.update_yaxes(title_text="Daily Sales", row=2, col=1)
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            if funnel:
                # Enhanced funnel visualization
                funnel_data = pd.DataFrame({
                    "Stage": ["Impressions", "Clicks", "LP Views", "Add to Cart", "Purchases"],
                    "Count": [
                        funnel.impressions,
                        funnel.clicks,
                        funnel.lp_views,
                        funnel.add_to_cart,
                        funnel.purchases
                    ]
                })
                
                funnel_data["Conversion %"] = [
                    100,
                    (funnel.clicks/funnel.impressions*100) if funnel.impressions > 0 else 0,
                    (funnel.lp_views/funnel.clicks*100) if funnel.clicks > 0 else 0,
                    (funnel.add_to_cart/funnel.lp_views*100) if funnel.lp_views > 0 else 0,
                    (funnel.purchases/funnel.add_to_cart*100) if funnel.add_to_cart > 0 else 0
                ]
                
                fig = go.Figure()
                
                fig.add_trace(go.Funnel(
                    y=funnel_data["Stage"],
                    x=funnel_data["Count"],
                    textposition="inside",
                    textinfo="value+percent previous",
                    opacity=0.8,
                    marker={
                        "color": ["#3498db", "#9b59b6", "#e74c3c", "#f39c12", "#27ae60"],
                        "line": {"width": 2, "color": "white"}
                    },
                    connector={"line": {"color": "royalblue", "dash": "dot", "width": 3}}
                ))
                
                fig.update_layout(
                    height=500,
                    title="Conversion Funnel",
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Conversion rates table
                st.markdown("#### Stage-to-Stage Conversion Rates")
                conv_df = pd.DataFrame({
                    "From → To": [
                        "Impressions → Clicks",
                        "Clicks → LP Views",
                        "LP Views → Add to Cart",
                        "Add to Cart → Purchase"
                    ],
                    "Rate": [
                        f"{(funnel.clicks/funnel.impressions*100):.2f}%" if funnel.impressions > 0 else "—",
                        f"{(funnel.lp_views/funnel.clicks*100):.2f}%" if funnel.clicks > 0 else "—",
                        f"{(funnel.add_to_cart/funnel.lp_views*100):.2f}%" if funnel.lp_views > 0 else "—",
                        f"{(funnel.purchases/funnel.add_to_cart*100):.2f}%" if funnel.add_to_cart > 0 else "—"
                    ]
                })
                st.dataframe(conv_df, use_container_width=True, hide_index=True)
            else:
                st.info("Upload advertising data to see funnel analysis")
        
        with tab3:
            # Weekly pattern
            if len(show_records) >= 7:
                st.markdown("#### 7-Day Sales Pattern")
                
                recent = show_records.tail(7).copy()
                recent["day_of_week"] = pd.to_datetime(recent["report_date"]).dt.day_name()
                
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=recent["day_of_week"],
                    y=recent["today_sold"],
                    marker_color=recent["today_sold"].apply(
                        lambda x: "#27ae60" if x > daily_target else "#e67e22" if x > daily_target*0.5 else "#e74c3c"
                    ),
                    text=recent["today_sold"],
                    textposition='outside'
                ))
                
                fig.add_hline(
                    y=daily_target,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Target: {daily_target:.0f}"
                )
                
                fig.update_layout(
                    height=400,
                    title="Last 7 Days Performance",
                    xaxis_title="Day",
                    yaxis_title="Tickets Sold",
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)

    def create_sales_overview(self, df: pd.DataFrame) -> None:
        """Create enhanced sales overview."""
        if df is None or df.empty:
            st.warning("No ticket sales data available.")
            return
            
        st.subheader("🎫 Ticket Sales Overview")
        
        # Summary metrics
        total_shows = len(df["show_id"].unique())
        total_capacity = df["capacity"].sum()
        total_sold = df["total_sold"].sum()
        total_revenue = df["sales_to_date"].sum()
        avg_occupancy = df["occupancy_rate"].mean()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        col1.metric(
            "Active Shows",
            f"{total_shows:,}",
            delta=f"{df['city'].nunique()} cities"
        )
        
        col2.metric(
            "Total Capacity",
            f"{int(total_capacity):,}",
            delta=f"{(total_sold/total_capacity*100):.1f}% sold"
        )
        
        col3.metric(
            "Tickets Sold",
            f"{int(total_sold):,}",
            delta=f"{int(total_capacity - total_sold):,} remaining"
        )
        
        col4.metric(
            "Revenue",
            f"${total_revenue/1e6:.1f}M" if total_revenue > 1e6 else f"${total_revenue:,.0f}"
        )
        
        col5.metric(
            "Avg Occupancy",
            f"{avg_occupancy:.1f}%",
            delta="🟢" if avg_occupancy > 75 else "🟡" if avg_occupancy > 50 else "🔴"
        )

    def create_sales_charts(self, df: pd.DataFrame) -> None:
        """Create enhanced sales visualizations."""
        if df is None or df.empty:
            return
            
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**City Performance**")
            city_data = df.groupby("city").agg({
                "total_sold": "sum",
                "capacity": "sum",
                "sales_to_date": "sum"
            }).reset_index()
            
            city_data["occupancy"] = (city_data["total_sold"] / city_data["capacity"] * 100)
            city_data = city_data.sort_values("total_sold", ascending=False).head(10)
            
            fig = px.bar(
                city_data,
                x="total_sold",
                y="city",
                orientation='h',
                color="occupancy",
                color_continuous_scale="RdYlGn",
                range_color=[0, 100],
                labels={
                    "total_sold": "Tickets Sold",
                    "city": "City",
                    "occupancy": "Occupancy %"
                },
                hover_data=["sales_to_date"]
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**Occupancy Distribution**")
            
            fig = go.Figure()
            
            # Add histogram
            fig.add_trace(go.Histogram(
                x=df["occupancy_rate"],
                nbinsx=20,
                name="Shows",
                marker_color="#3498db",
                opacity=0.7
            ))
            
            # Add average line
            fig.add_vline(
                x=df["occupancy_rate"].mean(),
                line_dash="dash",
                line_color="red",
                annotation_text=f"Avg: {df['occupancy_rate'].mean():.1f}%"
            )
            
            fig.update_layout(
                height=400,
                xaxis_title="Occupancy %",
                yaxis_title="Number of Shows",
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)

    def create_ads_overview(self, df: pd.DataFrame) -> None:
        """Create enhanced ads overview."""
        if df is None or df.empty:
            st.warning("No advertising data available.")
            return
            
        st.subheader("📈 Advertising Performance")
        
        # Calculate metrics
        total_spend = df["spend"].sum()
        total_impressions = df["impressions"].sum()
        total_clicks = df["clicks"].sum()
        total_purchases = df.get("purchases", pd.Series([0])).sum()
        
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_cpc = total_spend / total_clicks if total_clicks > 0 else 0
        avg_cpa = total_spend / total_purchases if total_purchases > 0 else 0
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        col1.metric(
            "Total Spend",
            f"${total_spend:,.0f}",
            delta=f"${total_spend/30:.0f}/day" if len(df) > 0 else None
        )
        
        col2.metric(
            "Impressions",
            f"{int(total_impressions/1000):.0f}K" if total_impressions > 1000 else f"{int(total_impressions)}"
        )
        
        col3.metric(
            "Clicks",
            f"{int(total_clicks):,}",
            delta=f"{avg_ctr:.2f}% CTR"
        )
        
        col4.metric(
            "Avg CPC",
            f"${avg_cpc:.2f}"
        )
        
        col5.metric(
            "Purchases",
            f"{int(total_purchases):,}",
            delta=f"${avg_cpa:.2f} CPA" if total_purchases > 0 else None
        )

    def create_ads_charts(self, df: pd.DataFrame) -> None:
        """Create enhanced advertising charts."""
        if df is None or df.empty:
            return
            
        # Performance over time
        st.markdown("**Campaign Performance Trends**")
        
        if "date" in df.columns:
            daily = df.groupby("date").agg({
                "impressions": "sum",
                "clicks": "sum",
                "spend": "sum",
                "purchases": "sum"
            }).reset_index()
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=("Impressions", "Clicks", "Spend", "Purchases"),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Impressions
            fig.add_trace(
                go.Scatter(
                    x=daily["date"],
                    y=daily["impressions"],
                    mode='lines+markers',
                    name='Impressions',
                    line=dict(color='#3498db', width=2)
                ),
                row=1, col=1
            )
            
            # Clicks
            fig.add_trace(
                go.Scatter(
                    x=daily["date"],
                    y=daily["clicks"],
                    mode='lines+markers',
                    name='Clicks',
                    line=dict(color='#9b59b6', width=2)
                ),
                row=1, col=2
            )
            
            # Spend
            fig.add_trace(
                go.Scatter(
                    x=daily["date"],
                    y=daily["spend"],
                    mode='lines+markers',
                    name='Spend',
                    line=dict(color='#e74c3c', width=2)
                ),
                row=2, col=1
            )
            
            # Purchases
            fig.add_trace(
                go.Scatter(
                    x=daily["date"],
                    y=daily["purchases"],
                    mode='lines+markers',
                    name='Purchases',
                    line=dict(color='#27ae60', width=2)
                ),
                row=2, col=2
            )
            
            fig.update_layout(
                height=500,
                showlegend=False,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)

    def create_integration_analysis(
        self, sales_df: pd.DataFrame, ads_df: pd.DataFrame
    ) -> None:
        """Create enhanced integration analysis."""
        if sales_df is None or ads_df is None or sales_df.empty or ads_df.empty:
            st.info("Upload both sales and advertising data to see integrated analysis.")
            return
            
        st.subheader("🔗 Integrated Performance Analysis")
        
        # Prepare data for correlation
        if "date" in ads_df.columns:
            ads_df["integration_date"] = pd.to_datetime(ads_df["date"]).dt.date
        
        if "show_date" in sales_df.columns:
            sales_df["integration_date"] = pd.to_datetime(sales_df["show_date"]).dt.date
        
        # Find overlapping dates
        if "integration_date" in ads_df.columns and "integration_date" in sales_df.columns:
            sales_by_date = sales_df.groupby("integration_date").agg({
                "total_sold": "sum",
                "sales_to_date": "sum"
            }).reset_index()
            
            ads_by_date = ads_df.groupby("integration_date").agg({
                "impressions": "sum",
                "clicks": "sum",
                "spend": "sum",
                "purchases": "sum"
            }).reset_index()
            
            merged = pd.merge(sales_by_date, ads_by_date, on="integration_date", how="inner")
            
            if not merged.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Spend vs Tickets Sold**")
                    fig = px.scatter(
                        merged,
                        x="spend",
                        y="total_sold",
                        size="clicks",
                        color="purchases",
                        trendline="ols" if HAS_STATSMODELS else None,
                        labels={
                            "spend": "Ad Spend ($)",
                            "total_sold": "Tickets Sold",
                            "purchases": "Online Purchases"
                        }
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("**Clicks vs Revenue**")
                    fig = px.scatter(
                        merged,
                        x="clicks",
                        y="sales_to_date",
                        size="spend",
                        color="total_sold",
                        trendline="ols" if HAS_STATSMODELS else None,
                        labels={
                            "clicks": "Clicks",
                            "sales_to_date": "Revenue ($)",
                            "total_sold": "Tickets"
                        }
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Correlation matrix
                st.markdown("**Correlation Analysis**")
                
                corr_metrics = ["spend", "clicks", "impressions", "purchases", "total_sold", "sales_to_date"]
                corr_data = merged[corr_metrics].corr()
                
                fig = px.imshow(
                    corr_data,
                    text_auto=".2f",
                    color_continuous_scale="RdBu",
                    aspect="auto"
                )
                
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

def main():
    """Main application entry point."""
    
    st.title("🎭 Ads Performance Analyzer v4.0")
    st.caption("Integrated analytics for Meta ads and ticket sales - Enhanced with visual health indicators")
    
    # Initialize components
    sheets_connector = PublicSheetsConnector()
    ads_processor = AdsDataProcessor()
    dashboard = IntegratedDashboard()
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Data Sources")
        
        # Load sales data
        if "sales_data" not in st.session_state:
            with st.spinner("Loading ticket sales..."):
                sales_data = sheets_connector.load_data()
                st.session_state["sales_data"] = sales_data
                
                if sales_data is not None:
                    summary = sheets_connector.get_data_summary(sales_data)
                    st.success(f"✅ {summary.get('total_shows', 0)} shows loaded")
                else:
                    st.error("❌ Failed to load sales data")
        
        if st.button("🔄 Refresh Sales Data"):
            with st.spinner("Refreshing..."):
                st.session_state["sales_data"] = sheets_connector.load_data()
                st.rerun()
        
        st.markdown("---")
        
        # Upload ads data
        st.subheader("📤 Upload Ad Reports")
        st.caption("Upload 3 Meta export files:")
        st.caption("• Days report")
        st.caption("• Days + Placement + Device")
        st.caption("• Days + Time")
        
        uploaded_files = st.file_uploader(
            "Select files",
            type=["csv", "xlsx", "xls"],
            accept_multiple_files=True,
            help="Upload all 3 Meta reports for complete analysis"
        )
        
        if uploaded_files:
            try:
                ads_data_by_type, funnel_summary = ads_processor.process_ads_files(
                    uploaded_files, st.session_state.get("sales_data")
                )
                dashboard.ads_data_by_type = ads_data_by_type
                dashboard.funnel_summary = funnel_summary
                st.success(f"✅ Processed {len(ads_data_by_type)} report types")
            except Exception as exc:
                st.error(f"❌ Error: {exc}")
    
    # Main content area
    dashboard.sales_data = st.session_state.get("sales_data")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🩺 Show Health",
        "🎫 Ticket Sales", 
        "📈 Advertising",
        "🔗 Integration"
    ])
    
    with tab1:
        dashboard.render_show_health(
            dashboard.sales_data,
            dashboard.funnel_summary
        )
    
    with tab2:
        dashboard.create_sales_overview(dashboard.sales_data)
        st.markdown("---")
        dashboard.create_sales_charts(dashboard.sales_data)
    
    with tab3:
        days_df = dashboard.ads_data_by_type.get("days") if dashboard.ads_data_by_type else None
        dashboard.create_ads_overview(days_df)
        st.markdown("---")
        dashboard.create_ads_charts(days_df)
    
    with tab4:
        days_df = dashboard.ads_data_by_type.get("days") if dashboard.ads_data_by_type else None
        dashboard.create_integration_analysis(dashboard.sales_data, days_df)
    
    # Footer
    st.markdown("---")
    st.caption("Built with Streamlit • Ads Performance Analyzer v4.0 • © 2025 Avner Gomes")

if __name__ == "__main__":
    main()