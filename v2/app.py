"""Streamlit application for integrated ad and ticket sales analytics - Version 2.0"""

from __future__ import annotations

import importlib.util
import io
import re
import warnings
from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

HAS_STATSMODELS = importlib.util.find_spec("statsmodels") is not None

from public_sheets_connector import PublicSheetsConnector

warnings.filterwarnings("ignore")


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
    """Handles ad data ingestion, normalization, and enrichment - Enhanced Version 2.0"""

    def __init__(self):
        # Enhanced column aliases to support various naming conventions
        self.standard_column_aliases: Dict[str, List[str]] = {
            "date": [
                "reporting_starts",
                "reporting starts",
                "date",
                "day",
                "date_start",
                "created_time",
                "reportingstarts",
            ],
            "reporting_ends": [
                "reporting_ends",
                "reporting ends",
                "reportingends",
                "date_stop",
            ],
            "campaign_name": [
                "campaign_name", 
                "campaign name", 
                "campaign", 
                "campaign id",
                "campaignname",
            ],
            "campaign_delivery": [
                "campaign_delivery",
                "campaign delivery",
                "campaigndelivery",
            ],
            "ad_set_name": [
                "ad_set_name", 
                "ad set name",
                "adsetname",
            ],
            "ad_set_budget": [
                "ad_set_budget",
                "ad set budget",
                "adsetbudget",
            ],
            "ad_set_budget_type": [
                "ad_set_budget_type",
                "ad set budget type",
                "adsetbudgettype",
            ],
            "ad_name": [
                "ad_name", 
                "ad name",
                "adname",
            ],
            "impressions": [
                "impressions",
                "impression",
            ],
            "reach": [
                "reach",
            ],
            "frequency": [
                "frequency",
            ],
            "clicks": [
                "clicks", 
                "link_clicks", 
                "link clicks",
                "linkclicks",
            ],
            "spend": [
                "spend",
                "amount_spent",
                "amount spent",
                "amount spent (usd)",
                "amountspent",
                "amountspent(usd)",
                "amountspent usd",
            ],
            "ctr": [
                "ctr", 
                "ctr (link)", 
                "ctr(link)",
                "ctrlink",
                "click_through_rate",
            ],
            "cpc": [
                "cpc", 
                "cost_per_click",
                "costperclick",
            ],
            "cpm": [
                "cpm",
                "cpm (cost per 1,000 impressions)",
                "cpm (cost per 1,000 impressions) (usd)",
                "cpmcostper1000impressions",
                "cpmcostper1000impressionsusd",
            ],
            "results": [
                "results",
                "result",
            ],
            "result_indicator": [
                "result_indicator", 
                "result indicator",
                "resultindicator",
            ],
            "cost_per_results": [
                "cost_per_results",
                "cost per results",
                "costperresults",
            ],
            "attribution_setting": [
                "attribution_setting",
                "attribution setting",
                "attributionsetting",
            ],
            "ends": [
                "ends",
            ],
            "starts": [
                "starts",
            ],
            # Placement & Device columns
            "placement": [
                "placement",
            ],
            "platform": [
                "platform",
            ],
            "device_platform": [
                "device platform", 
                "device_platform",
                "deviceplatform",
            ],
            "impression_device": [
                "impression device",
                "impression_device",
                "impressiondevice",
            ],
            # Time columns
            "time_of_day": [
                "time of day (viewer's time zone)", 
                "time of day",
                "time",
                "timeofdayviewerstimezone",
                "timeofday",
            ],
        }

        self.funnel_column_aliases: Dict[str, Iterable[str]] = {
            "lp_views": [
                "f1",
                "fun1",
                "lpviews",
                "lp_views",
                "lpviewsf1",
                "lpviewsfun1",
                "landingpageviews",
                "landing_page_views",
            ],
            "add_to_cart": [
                "f2",
                "fun2",
                "addtocart",
                "add_to_cart",
                "addtocartf2",
                "addtocart_fun2",
                "initiated_checkout",
            ],
            "purchases": [
                "f3",
                "fun3",
                "conv_addtocart",
                "conv_f3",
                "purchases",
                "purchases_f3",
                "orders",
                "tickets_sold",
            ],
        }

        self.funnel_indicator_aliases: Dict[str, str] = {
            "actions:landing_page_view": "lp_views",
            "landing_page_view": "lp_views",
            "landing_page_views": "lp_views",
            "lpviews": "lp_views",
            "actions:link_click": "clicks",
            "link_clicks": "clicks",
            "actions:offsite_conversion.fb_pixel_add_to_cart": "add_to_cart",
            "offsite_conversion.fb_pixel_add_to_cart": "add_to_cart",
            "add_to_cart": "add_to_cart",
            "initiate_checkout": "add_to_cart",
            "actions:offsite_conversion.fb_pixel_purchase": "purchases",
            "offsite_conversion.fb_pixel_purchase": "purchases",
            "purchases": "purchases",
            "purchase": "purchases",
            "onsite_conversion.purchase": "purchases",
        }

    @staticmethod
    def _normalize_column_name(col: str) -> str:
        """Normalize column name by removing special characters and converting to lowercase"""
        return re.sub(r"[^a-z0-9]", "", col.lower())

    def detect_and_normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect and normalize column names based on aliases"""
        if df is None or df.empty:
            return df

        normalized_df = df.copy()

        # Create a mapping of normalized existing columns
        col_map: Dict[str, str] = {}
        normalized_existing = {
            self._normalize_column_name(col): col for col in normalized_df.columns
        }

        # Match aliases to existing columns
        for standard, aliases in self.standard_column_aliases.items():
            for alias in aliases:
                normalized_alias = self._normalize_column_name(alias)
                if normalized_alias in normalized_existing:
                    current_name = normalized_existing[normalized_alias]
                    if standard not in normalized_df.columns:
                        col_map[current_name] = standard
                    break

        # Apply the mapping
        if col_map:
            normalized_df = normalized_df.rename(columns=col_map)

        return normalized_df

    def identify_dataset_type(self, df: pd.DataFrame) -> Optional[str]:
        """Identify which type of dataset this is based on columns"""
        if df is None:
            return None

        normalized_columns = {self._normalize_column_name(col) for col in df.columns}

        # Check for time dataset
        if "timeofdayviewerstimezone" in normalized_columns or "timeofday" in normalized_columns:
            return "days_time"
        
        # Check for placement/device dataset
        if "placement" in normalized_columns or "platform" in normalized_columns or "deviceplatform" in normalized_columns:
            return "days_placement_device"
        
        # Check for basic days dataset
        # Must have date and campaign info
        has_date = any(col in normalized_columns for col in ["date", "reportingstarts", "reportingends"])
        has_campaign = any(col in normalized_columns for col in ["campaignname", "campaign"])
        
        if has_date and has_campaign:
            return "days"
            
        return None

    def calculate_missing_kpis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate missing KPIs from existing data"""
        if df is None or df.empty:
            return df

        numeric_cols = [
            "impressions",
            "reach",
            "frequency",
            "clicks",
            "spend",
            "ctr",
            "cpc",
            "cpm",
            "results",
            "lp_views",
            "add_to_cart",
            "purchases",
            "cost_per_results",
        ]
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Calculate CTR if missing
        if "impressions" in df.columns and "clicks" in df.columns and "ctr" not in df.columns:
            df["ctr"] = np.where(
                df["impressions"] > 0, (df["clicks"] / df["impressions"]) * 100, 0
            )

        # Calculate CPC if missing
        if "spend" in df.columns and "clicks" in df.columns and "cpc" not in df.columns:
            df["cpc"] = np.where(df["clicks"] > 0, df["spend"] / df["clicks"], 0)

        # Calculate CPM if missing
        if "spend" in df.columns and "impressions" in df.columns and "cpm" not in df.columns:
            df["cpm"] = np.where(
                df["impressions"] > 0, (df["spend"] / df["impressions"]) * 1000, 0
            )

        # Calculate Cost per Results if missing
        if "spend" in df.columns and "results" in df.columns and "cost_per_results" not in df.columns:
            df["cost_per_results"] = np.where(
                df["results"] > 0, df["spend"] / df["results"], 0
            )

        return df

    def normalize_funnel_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize funnel-specific columns"""
        if df is None or df.empty:
            return df

        normalized_columns = {
            self._normalize_column_name(col): col for col in df.columns
        }

        # Map funnel columns from various aliases
        for target, aliases in self.funnel_column_aliases.items():
            for alias in aliases:
                normalized_alias = self._normalize_column_name(alias)
                if normalized_alias in normalized_columns:
                    source_col = normalized_columns[normalized_alias]
                    df[target] = df[source_col]
                    break
            else:
                # Create column with zeros if not found
                if target not in df.columns:
                    df[target] = 0

        # Extract funnel metrics from result_indicator if available
        if "result_indicator" in df.columns and "results" in df.columns:
            df = df.copy()
            df["results"] = pd.to_numeric(df["results"], errors="coerce")
            
            for alias, target in self.funnel_indicator_aliases.items():
                mask = df["result_indicator"].fillna("").str.lower() == alias.lower()
                if mask.any():
                    df.loc[mask, target] = df.loc[mask, "results"].astype(float)

        return df

    def process_ads_files(
        self, 
        uploaded_files: List[st.runtime.uploaded_file_manager.UploadedFile], 
        sales_df: pd.DataFrame
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, FunnelSummary]]:
        """Process all uploaded ad files"""
        data_by_type: Dict[str, pd.DataFrame] = {}
        read_errors: List[str] = []

        for uploaded in uploaded_files:
            try:
                content = uploaded.read()
                buffer = io.BytesIO(content)
                
                # Read file based on extension
                if uploaded.name.lower().endswith(".csv"):
                    df = pd.read_csv(buffer)
                else:
                    df = pd.read_excel(buffer)

                # Apply normalization and processing
                df = self.detect_and_normalize_columns(df)
                df = self.calculate_missing_kpis(df)
                df = self.normalize_funnel_columns(df)

                # Identify dataset type
                dataset_type = self.identify_dataset_type(df)
                if dataset_type is None:
                    read_errors.append(f"{uploaded.name} (could not identify type)")
                    continue

                df["source_file"] = uploaded.name
                data_by_type[dataset_type] = df
                
            except Exception as exc:
                read_errors.append(f"{uploaded.name}: {exc}")

        # Check if we have all required types
        required_types = {"days", "days_placement_device", "days_time"}
        missing_types = required_types - data_by_type.keys()
        
        if missing_types:
            st.warning(
                f"Missing file types: {', '.join(missing_types)}. "
                "Upload files that match the 'Days', 'Days + Placement + Device', and 'Days + Time' exports."
            )
        
        if read_errors:
            st.warning("Some files could not be processed: " + ", ".join(read_errors))

        # Enrich the days dataset with sales data if available
        if "days" in data_by_type and sales_df is not None:
            enriched_days = self.enrich_ads_dataframe(data_by_type["days"], sales_df)
            data_by_type["days"] = enriched_days
            funnel_summary = self.calculate_funnel_summary(enriched_days)
        else:
            funnel_summary = {}

        return data_by_type, funnel_summary

    def enrich_ads_dataframe(
        self, df: pd.DataFrame, sales_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Enrich ads data with show matching from sales data"""
        if df is None or df.empty:
            return df

        df = df.copy()

        # Normalize date column
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        elif "reporting_starts" in df.columns:
            df["date"] = pd.to_datetime(df["reporting_starts"], errors="coerce")

        # Normalize campaign/ad set names
        if "ad_set_name" not in df.columns and "ad set name" in df.columns:
            df = df.rename(columns={"ad set name": "ad_set_name"})

        if "campaign_name" not in df.columns and "campaign" in df.columns:
            df["campaign_name"] = df["campaign"]
        if "campaign_name" not in df.columns:
            df["campaign_name"] = df.get("ad_set_name")

        # Build show lookup from sales data
        show_lookup = self._build_show_lookup(sales_df)

        # Match each row to a show
        df["matched_show_id"] = df.apply(
            lambda row: self._match_show_identifier(row, show_lookup), axis=1
        )

        return df

    def _build_show_lookup(self, sales_df: pd.DataFrame) -> Dict[str, Dict[int, str]]:
        """Build a lookup dictionary for matching shows"""
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

    def _match_show_identifier(
        self, row: pd.Series, show_lookup: Dict[str, Dict[int, str]]
    ) -> Optional[str]:
        """Match a row to a show ID"""
        text_candidates = [
            str(row.get("campaign_name", "")),
            str(row.get("ad_set_name", "")),
            str(row.get("ad_name", "")),
        ]
        merged_text = " ".join([t for t in text_candidates if t])
        if not merged_text:
            return None

        # Try to extract show ID directly
        show_id = self._extract_show_id_from_text(merged_text)
        if show_id:
            return show_id

        # Fall back to city/sequence matching
        return self._fallback_show_match(merged_text, show_lookup)

    def _extract_show_id_from_text(self, text: str) -> Optional[str]:
        """Extract show ID using regex"""
        match = re.search(r"([A-Z]{2,3}_\d{4}(?:_S\d+)?)", text.upper())
        if match:
            return match.group(1)
        return None

    def _normalize_text(self, text: str) -> str:
        """Normalize text for matching"""
        return re.sub(r"[^a-z0-9]", "", str(text).lower())

    def _fallback_show_match(
        self, text: str, show_lookup: Dict[str, Dict[int, str]]
    ) -> Optional[str]:
        """Fallback matching using city and sequence"""
        if not show_lookup:
            return None

        normalized_text = self._normalize_text(text)
        
        # Extract sequence number
        sequence = 1
        sequence_match = re.search(r"#\s*(\d{1,2})", text.lower())
        if not sequence_match:
            sequence_match = re.search(r"\b(?:show|s)(\d{1,2})\b", text.lower())
        if sequence_match:
            sequence = int(sequence_match.group(1))

        # Try to match city
        for city_key, sequences in show_lookup.items():
            if city_key and city_key in normalized_text:
                if sequence in sequences:
                    return sequences[sequence]
                # Fallback to first available sequence
                return next(iter(sequences.values()))
        
        return None

    def calculate_funnel_summary(self, df: pd.DataFrame) -> Dict[str, FunnelSummary]:
        """Calculate funnel metrics by show"""
        if df is None or df.empty:
            return {}

        required_cols = [
            "matched_show_id",
            "spend",
            "impressions",
            "clicks",
            "lp_views",
            "add_to_cart",
            "purchases",
        ]
        
        for col in required_cols:
            if col not in df.columns:
                df[col] = 0

        # Group by show
        grouped = df.groupby("matched_show_id", dropna=True).agg(
            {
                "spend": "sum",
                "impressions": "sum",
                "clicks": "sum",
                "lp_views": "sum",
                "add_to_cart": "sum",
                "purchases": "sum",
            }
        )

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
                purchases=float(row.get("purchases", 0) or 0),
            )
        
        return result


class IntegratedDashboard:
    """Builds the Streamlit visualisations for the analytics experience."""

    def __init__(self):
        self.sales_data: Optional[pd.DataFrame] = None
        self.ads_data_by_type: Dict[str, pd.DataFrame] = {}
        self.funnel_summary: Dict[str, FunnelSummary] = {}

    @staticmethod
    def _latest_per_show(df: pd.DataFrame) -> pd.DataFrame:
        """Return the most recent record for each show ID."""
        if df is None or df.empty:
            return df

        sort_columns = ["show_id"]
        if "report_date" in df.columns:
            sort_columns.append("report_date")

        snapshot = (
            df.sort_values(sort_columns)
            .drop_duplicates(subset="show_id", keep="last")
        )
        return snapshot

    @staticmethod
    def summarize_sales(df: Optional[pd.DataFrame]) -> Dict[str, float]:
        """Aggregate key ticket sales metrics from the latest snapshot per show."""
        if df is None or df.empty:
            return {}

        snapshot = IntegratedDashboard._latest_per_show(df)
        if snapshot is None or snapshot.empty:
            return {}

        total_shows = int(snapshot["show_id"].nunique())
        capacity_series = snapshot["capacity"] if "capacity" in snapshot.columns else pd.Series(dtype=float)
        total_capacity = float(capacity_series.fillna(0).sum())

        sold_series = snapshot["total_sold"] if "total_sold" in snapshot.columns else pd.Series(dtype=float)
        total_sold = float(sold_series.fillna(0).sum())

        revenue_series = snapshot["sales_to_date"] if "sales_to_date" in snapshot.columns else pd.Series(dtype=float)
        total_revenue = float(revenue_series.fillna(0).sum())

        occupancy_series = snapshot["occupancy_rate"] if "occupancy_rate" in snapshot.columns else pd.Series(dtype=float)
        if occupancy_series is not None and not occupancy_series.dropna().empty:
            avg_occupancy = float(occupancy_series.dropna().mean())
        else:
            avg_occupancy = 0.0

        ticket_price_series = snapshot["avg_ticket_price"] if "avg_ticket_price" in snapshot.columns else pd.Series(dtype=float)
        if ticket_price_series is not None and not ticket_price_series.dropna().empty:
            avg_ticket_price = float(ticket_price_series.dropna().mean())
        else:
            avg_ticket_price = 0.0

        cities_count = int(snapshot["city"].nunique()) if "city" in snapshot.columns else 0
        sold_out_shows = int(occupancy_series.fillna(0).ge(99).sum())

        return {
            "total_shows": total_shows,
            "total_capacity": total_capacity,
            "total_sold": total_sold,
            "total_revenue": total_revenue,
            "avg_occupancy": avg_occupancy,
            "avg_ticket_price": avg_ticket_price,
            "cities_count": cities_count,
            "sold_out_shows": sold_out_shows,
        }

    @staticmethod
    def _build_sales_timeline(
        df: pd.DataFrame, show_id: Optional[str] = None
    ) -> pd.DataFrame:
        """Create a timeline with cumulative and daily ticket sales by report date."""
        if df is None or df.empty or "report_date" not in df.columns:
            return pd.DataFrame()

        history = df.copy()
        if show_id is not None:
            history = history[history["show_id"] == show_id]

        history = history.dropna(subset=["report_date"]).copy()
        if history.empty:
            return pd.DataFrame()

        history["report_date"] = pd.to_datetime(history["report_date"]).dt.normalize()

        sort_columns = ["show_id", "report_date"]
        if "source_row" in history.columns:
            sort_columns.append("source_row")

        history = history.sort_values(sort_columns)

        per_day = (
            history.groupby(["show_id", "report_date"], as_index=False)
            .agg(
                total_sold=("total_sold", "last"),
                reported_daily=("today_sold", "last"),
            )
            .sort_values(["show_id", "report_date"])
        )

        if per_day.empty:
            return pd.DataFrame()

        per_day["total_sold"] = per_day["total_sold"].fillna(0.0)
        per_day["reported_daily"] = (
            per_day["reported_daily"].fillna(0.0).clip(lower=0.0)
        )

        per_day["increment_from_total"] = (
            per_day.groupby("show_id")["total_sold"].diff()
        )
        per_day["increment_from_total"] = per_day["increment_from_total"].fillna(
            per_day["total_sold"]
        )
        per_day["increment_from_total"] = per_day["increment_from_total"].clip(
            lower=0.0
        )

        per_day["daily_sold"] = per_day[["reported_daily", "increment_from_total"]].max(
            axis=1
        )

        aggregated = (
            per_day.groupby("report_date", as_index=False)
            .agg(
                official_total=("total_sold", "sum"),
                daily_sold=("daily_sold", "sum"),
            )
            .sort_values("report_date")
        )

        if aggregated.empty:
            return pd.DataFrame()

        aggregated = aggregated.set_index("report_date")

        start = aggregated.index.min()
        end = pd.Timestamp.today().normalize()
        if pd.isna(start):
            return pd.DataFrame()
        if pd.isna(end) or end < start:
            end = start

        full_range = pd.date_range(start=start, end=end, freq="D")
        aggregated = aggregated.reindex(full_range)
        aggregated.index.name = "report_date"

        aggregated["daily_sold"] = aggregated["daily_sold"].fillna(0.0)

        running_total = 0.0
        cumulative: List[float] = []
        for raw_total, daily in aggregated[["official_total", "daily_sold"]].itertuples(
            index=False
        ):
            raw_total = 0.0 if pd.isna(raw_total) else float(raw_total)
            daily = float(daily or 0.0)

            projected = running_total + daily
            if raw_total > 0:
                running_total = max(raw_total, projected)
            else:
                running_total = max(projected, running_total)
            cumulative.append(running_total)

        aggregated["cumulative_total"] = cumulative
        aggregated["official_total"] = aggregated["official_total"].fillna(0.0)

        return aggregated.reset_index()[
            ["report_date", "cumulative_total", "daily_sold", "official_total"]
        ]

    # ----------------------------- Sales --------------------------------- #
    def create_sales_overview(self, df: pd.DataFrame) -> None:
        if df is None or df.empty:
            st.warning("No ticket sales data available yet.")
            return

        st.subheader("🎫 Ticket Sales Overview")
        summary = self.summarize_sales(df)
        if not summary:
            st.info("Ticket sales data is still being processed.")
            return

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Shows", f"{summary['total_shows']:,}")
        col2.metric("Total Capacity", f"{int(round(summary['total_capacity'])):,}")
        col3.metric("Tickets Sold", f"{int(round(summary['total_sold'])):,}")
        col4.metric("Revenue to Date", f"${summary['total_revenue']:,.0f}")

        col5, col6, col7, col8 = st.columns(4)
        col5.metric("Average Occupancy", f"{summary['avg_occupancy']:.1f}%")
        col6.metric("Average Ticket Price", f"${summary['avg_ticket_price']:,.0f}")
        col7.metric("Cities", f"{summary['cities_count']}")
        col8.metric("Sold Out", f"{summary['sold_out_shows']}")

    def create_sales_charts(self, df: pd.DataFrame) -> None:
        if df is None or df.empty:
            return

        col1, col2 = st.columns(2)

        snapshot = self._latest_per_show(df)

        with col1:
            st.markdown("**Top Cities by Tickets Sold**")
            if {"city", "total_sold", "capacity"}.issubset(snapshot.columns):
                city_performance = (
                    snapshot.groupby("city")
                    .agg({"total_sold": "sum", "capacity": "sum", "sales_to_date": "sum"})
                    .reset_index()
                )
                city_performance["occupancy"] = np.where(
                    city_performance["capacity"] > 0,
                    (city_performance["total_sold"] / city_performance["capacity"]) * 100,
                    0,
                )
                fig = px.bar(
                    city_performance.sort_values("total_sold", ascending=True).tail(10),
                    x="total_sold",
                    y="city",
                    orientation="h",
                    color="occupancy",
                    color_continuous_scale="RdYlGn",
                    labels={"total_sold": "Tickets Sold", "city": "City", "occupancy": "Occupancy %"},
                )
                fig.update_layout(height=420)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Occupancy Distribution**")
            if "occupancy_rate" in snapshot.columns:
                fig = px.histogram(
                    snapshot,
                    x="occupancy_rate",
                    nbins=20,
                    labels={"occupancy_rate": "Occupancy %"},
                    color_discrete_sequence=["#1f77b4"],
                )
                fig.update_layout(height=420)
                st.plotly_chart(fig, use_container_width=True)

        show_options: List[str] = []
        if "show_id" in df.columns:
            show_options = (
                df["show_id"].dropna().astype(str).sort_values().unique().tolist()
            )

        selection_label = "Show timeline scope"
        timeline_scope = "All shows"
        if show_options:
            timeline_scope = st.selectbox(
                selection_label,
                ["All shows"] + show_options,
                key="sales_timeline_scope",
            )
        else:
            st.caption("Showing ticket evolution for all records.")

        selected_show_id = None
        if timeline_scope != "All shows":
            selected_show_id = timeline_scope

        timeline = self._build_sales_timeline(df, selected_show_id)
        if not timeline.empty:
            if selected_show_id:
                st.markdown(f"**Ticket Sales over Time – {selected_show_id}**")
            else:
                st.markdown("**Ticket Sales over Time**")
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(
                go.Bar(
                    x=timeline["report_date"],
                    y=timeline["daily_sold"],
                    name="Daily Tickets Sold",
                    marker_color="#ff7f0e",
                    hovertemplate="%{x|%b %d, %Y}<br>Daily sold: %{y:,.0f}<extra></extra>",
                ),
                secondary_y=False,
            )
            fig.add_trace(
                go.Scatter(
                    x=timeline["report_date"],
                    y=timeline["cumulative_total"],
                    mode="lines+markers",
                    name="Total Tickets Sold",
                    line=dict(color="#1f77b4", width=2),
                    hovertemplate="%{x|%b %d, %Y}<br>Total sold: %{y:,.0f}<extra></extra>",
                ),
                secondary_y=True,
            )
            start_date = timeline["report_date"].dropna().min()
            end_date = pd.Timestamp.today().normalize()
            if pd.isna(start_date):
                start_date = end_date
            if pd.isna(end_date):
                end_date = start_date
            if start_date is not None and end_date is not None and start_date > end_date:
                end_date = start_date

            fig.update_layout(
                height=420,
                xaxis_title="Report Date",
                hovermode="x unified",
                xaxis=dict(type="date", range=[start_date, end_date]),
            )
            fig.update_yaxes(title_text="Daily Tickets Sold", secondary_y=False)
            fig.update_yaxes(title_text="Cumulative Tickets Sold", secondary_y=True)
            st.plotly_chart(fig, use_container_width=True)
        elif "show_date" in df.columns and df["show_date"].notna().any():
            st.markdown("**Ticket Sales over Time**")
            daily = (
                df.groupby("show_date")
                .agg({"today_sold": "sum", "total_sold": "sum"})
                .reset_index()
                .sort_values("show_date")
            )
            daily["cumulative_total"] = daily["total_sold"].cumsum()

            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(
                go.Bar(
                    x=daily["show_date"],
                    y=daily["today_sold"],
                    name="Daily Tickets Sold",
                    marker_color="#ff7f0e",
                    hovertemplate="%{x|%b %d, %Y}<br>Daily sold: %{y:,.0f}<extra></extra>",
                ),
                secondary_y=False,
            )
            fig.add_trace(
                go.Scatter(
                    x=daily["show_date"],
                    y=daily["cumulative_total"],
                    mode="lines+markers",
                    name="Total Tickets Sold",
                    line=dict(color="#1f77b4", width=2),
                    hovertemplate="%{x|%b %d, %Y}<br>Total sold: %{y:,.0f}<extra></extra>",
                ),
                secondary_y=True,
            )
            start_date = daily["show_date"].dropna().min()
            end_date = pd.Timestamp.today().normalize()
            if pd.isna(start_date):
                start_date = end_date
            if pd.isna(end_date):
                end_date = start_date
            if start_date is not None and end_date is not None and start_date > end_date:
                end_date = start_date

            fig.update_layout(
                height=420,
                xaxis_title="Show Date",
                hovermode="x unified",
                xaxis=dict(type="date", range=[start_date, end_date]),
            )
            fig.update_yaxes(title_text="Daily Tickets Sold", secondary_y=False)
            fig.update_yaxes(title_text="Cumulative Tickets Sold", secondary_y=True)
            st.plotly_chart(fig, use_container_width=True)

    # -------------------------- Show Health ------------------------------ #
    def render_show_health(
        self,
        df: pd.DataFrame,
        funnel_summary: Dict[str, FunnelSummary],
    ) -> None:
        if df is None or df.empty:
            return

        shows = df.sort_values(["show_date", "show_id"])["show_id"].unique()
        if len(shows) == 0:
            return

        st.subheader("🩺 Show Health Dashboard")
        selected_show = st.selectbox("Select a show", shows)
        show_records = df[df["show_id"] == selected_show].sort_values("report_date")
        
        if show_records.empty:
            st.info("No historical entries available for this show yet.")
            return

        latest = show_records.iloc[-1]
        days_to_show = (latest["show_date"].date() - date.today()).days
        days_to_show = max(days_to_show, 0)
        remaining_tickets = latest.get("remaining", 0)
        if pd.isna(remaining_tickets):
            remaining_tickets = 0
        total_sold = latest.get("total_sold", 0)
        if pd.isna(total_sold):
            total_sold = 0
        total_capacity = latest.get("capacity", 0)
        if pd.isna(total_capacity):
            total_capacity = 0
        occupancy = latest.get("occupancy_rate", 0)
        avg_ticket_price = latest.get("avg_ticket_price", 0)

        recent_sales = show_records.tail(7)["today_sold"].fillna(0)
        avg_sales_last_7 = latest.get("avg_sales_last_7_days")
        if pd.isna(avg_sales_last_7):
            avg_sales_last_7 = recent_sales.mean()
        days_left = max(days_to_show, 1)
        daily_sales_target = remaining_tickets / days_left if days_left else 0

        st.caption("Key metrics are based on the most recent report available for this show.")

        start_sales_date = (
            show_records["report_date"].dropna().min()
            if "report_date" in show_records.columns
            else None
        )
        if pd.notna(start_sales_date):
            start_sales_display = pd.to_datetime(start_sales_date).strftime("%b %d, %Y")
        else:
            start_sales_display = "Not available"

        col1, col2, col3 = st.columns(3)
        col1.metric("Days to Show", days_to_show)
        col2.metric("Occupancy", f"{occupancy:.1f}%")
        col3.metric("Tickets Remaining", f"{int(remaining_tickets):,}")

        col4, col5, col6 = st.columns(3)
        col4.metric("Total Capacity", f"{int(total_capacity):,}")
        col5.metric("Sales Start Date", start_sales_display)
        col6.metric(
            "Daily Sales Target",
            f"{daily_sales_target:.1f}",
            delta=f"{avg_sales_last_7:.1f} avg last 7d",
            help="Remaining tickets divided by days left. Delta shows the average pace over the last 7 reports.",
        )

        funnel = funnel_summary.get(selected_show)
        total_spend = funnel.spend if funnel else 0
        purchases = funnel.purchases if funnel else 0
        clicks = funnel.clicks if funnel else 0
        lp_views = funnel.lp_views if funnel else 0
        add_to_cart = funnel.add_to_cart if funnel else 0

        session_key = "show_budgets"
        st.session_state.setdefault(session_key, {})
        existing_budget = st.session_state[session_key].get(selected_show, float(total_spend))
        budget_input = st.number_input(
            "Show budget (USD)",
            min_value=0.0,
            value=float(existing_budget or 0.0),
            step=100.0,
            help="Used to calculate the ticket cost metric.",
        )
        st.session_state[session_key][selected_show] = budget_input

        ticket_cost = budget_input / total_sold if total_sold else 0
        daily_cpa = total_spend / total_sold if total_sold else 0
        revenue_to_date = latest.get("sales_to_date", avg_ticket_price * total_sold)
        roas = (revenue_to_date / total_spend) if total_spend else np.nan
        potential_roas = (
            (avg_ticket_price * total_capacity) / total_spend if total_spend else np.nan
        )

        col5, col6, col7, col8 = st.columns(4)
        col5.metric("Ticket Cost", f"${ticket_cost:,.2f}")
        col6.metric("Clicks per Ticket", f"{(clicks / total_sold) if total_sold else 0:.2f}")
        col7.metric("LP Views per Ticket", f"{(lp_views / total_sold) if total_sold else 0:.2f}")
        col8.metric("Add to Cart per Ticket", f"{(add_to_cart / total_sold) if total_sold else 0:.2f}")

        col9, col10, col11, col12 = st.columns(4)
        col9.metric("Daily Sales CPA", f"${daily_cpa:,.2f}")
        col10.metric("Total Spend", f"${total_spend:,.0f}")
        col11.metric("ROAS", f"{roas:.2f}" if not np.isnan(roas) else "–")
        col12.metric(
            "Potential ROAS",
            f"{potential_roas:.2f}" if not np.isnan(potential_roas) else "–",
            help="(Average ticket price × Capacity) ÷ Spend",
        )

        graph_col1, graph_col2 = st.columns(2)

        with graph_col1:
            st.markdown("**Sales trajectory**")
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=show_records["report_date"],
                    y=show_records["sales_to_date"],
                    mode="lines+markers",
                    name="Revenue to date",
                    line=dict(color="#1f77b4", width=2),
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=show_records["report_date"],
                    y=show_records["total_sold"],
                    mode="lines+markers",
                    name="Tickets sold",
                    line=dict(color="#ff7f0e", width=2),
                    yaxis="y2",
                )
            )
            fig.update_layout(
                height=420,
                yaxis=dict(title="Revenue", showgrid=False),
                yaxis2=dict(
                    title="Tickets",
                    overlaying="y",
                    side="right",
                    showgrid=False,
                ),
                hovermode="x unified",
            )
            st.plotly_chart(fig, use_container_width=True)

        with graph_col2:
            st.markdown("**Funnel snapshot**")
            funnel_data = pd.DataFrame(
                {
                    "Stage": [
                        "Impressions",
                        "Clicks",
                        "LP Views",
                        "Add to Cart",
                        "Tickets Sold",
                    ],
                    "Value": [
                        funnel.impressions if funnel else 0,
                        clicks,
                        lp_views,
                        add_to_cart,
                        purchases if purchases else total_sold,
                    ],
                }
            )
            fig = px.funnel(funnel_data, x="Value", y="Stage", color="Stage")
            fig.update_layout(height=420, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Seven-day sales cadence**")
        end = pd.Timestamp.today().normalize()

        cadence = show_records.copy()
        cadence["report_date"] = pd.to_datetime(cadence["report_date"]).dt.normalize()
        cadence = (
            cadence.groupby("report_date")
            .agg(today_sold=("today_sold", lambda s: float(np.nansum(s))))
            .sort_index()
        )

        cadence_start = end - pd.Timedelta(days=6)
        cadence_range = pd.date_range(start=cadence_start, end=end, freq="D")
        cadence = cadence.reindex(cadence_range).fillna(0.0)
        cadence = cadence.reset_index().rename(columns={"index": "report_date"})

        cadence_fig = px.bar(
            cadence,
            x="report_date",
            y="today_sold",
            labels={"report_date": "Report Date", "today_sold": "Tickets Sold"},
            color="today_sold",
            color_continuous_scale="Blues",
        )
        cadence_fig.add_hline(
            y=daily_sales_target,
            line_dash="dash",
            annotation_text="Daily target",
            annotation_position="top left",
        )
        cadence_fig.update_layout(height=320)
        st.plotly_chart(cadence_fig, use_container_width=True)

    # --------------------------- Ads Overview ---------------------------- #
    def create_ads_overview(self, df: pd.DataFrame) -> None:
        if df is None or df.empty:
            st.warning("No advertising data uploaded yet.")
            return

        st.subheader("📈 Advertising Overview")

        total_impressions = df["impressions"].sum()
        total_clicks = df["clicks"].sum()
        total_spend = df["spend"].sum()
        total_conversions = df.get("purchases", df.get("conversions", pd.Series([0] * len(df)))).sum()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Impressions", f"{int(total_impressions):,}")
        col2.metric("Clicks", f"{int(total_clicks):,}")
        col3.metric("Spend", f"${total_spend:,.2f}")
        col4.metric("Purchases", f"{int(total_conversions):,}")

    def create_ads_charts(
        self,
        df: pd.DataFrame,
        placement_df: Optional[pd.DataFrame] = None,
    ) -> None:
        if df is None or df.empty:
            return

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Spend vs. Purchases by Campaign**")
            if {"campaign_name", "spend", "purchases"}.issubset(df.columns):
                perf = (
                    df.groupby("campaign_name")
                    .agg({"spend": "sum", "clicks": "sum", "purchases": "sum"})
                    .reset_index()
                )
                perf["efficiency"] = np.where(
                    perf["spend"] > 0, (perf["purchases"] / perf["spend"]) * 100, 0
                )
                fig = px.scatter(
                    perf,
                    x="spend",
                    y="purchases",
                    size="clicks",
                    hover_data=["campaign_name"],
                    color="efficiency",
                    color_continuous_scale="RdYlGn",
                    labels={"spend": "Spend", "purchases": "Purchases", "efficiency": "Purchases per $100"},
                )
                fig.update_layout(height=420)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Performance over Time**")
            if "date" in df.columns:
                daily = (
                    df.groupby("date")
                    .agg({"impressions": "sum", "clicks": "sum", "spend": "sum", "purchases": "sum"})
                    .reset_index()
                )
                fig = make_subplots(
                    rows=2, 
                    cols=2, 
                    subplot_titles=["Impressions", "Clicks", "Spend", "Purchases"]
                )
                fig.add_trace(
                    go.Scatter(x=daily["date"], y=daily["impressions"], line=dict(color="#1f77b4")), 
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=daily["date"], y=daily["clicks"], line=dict(color="#ff7f0e")), 
                    row=1, col=2
                )
                fig.add_trace(
                    go.Scatter(x=daily["date"], y=daily["spend"], line=dict(color="#2ca02c")), 
                    row=2, col=1
                )
                fig.add_trace(
                    go.Scatter(x=daily["date"], y=daily["purchases"], line=dict(color="#d62728")), 
                    row=2, col=2
                )
                fig.update_layout(height=500, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Placement and Device Performance**")
        if placement_df is None or placement_df.empty:
            st.info("Upload the placement and device breakdown to explore channel performance.")
            return

        breakdown = placement_df.copy()
        numeric_columns = [
            "impressions",
            "clicks",
            "spend",
            "purchases",
            "add_to_cart",
            "results",
        ]
        for column in numeric_columns:
            if column in breakdown.columns:
                breakdown[column] = pd.to_numeric(breakdown[column], errors="coerce").fillna(0)
            else:
                breakdown[column] = 0

        def select_primary_metric(source: pd.DataFrame) -> Tuple[str, str]:
            """Choose the best available performance metric for visualisation."""

            indicator_labels = {
                "actions:landing_page_view": "Landing Page Views",
                "actions:link_click": "Link Clicks",
                "actions:offsite_conversion.fb_pixel_add_to_cart": "Add to Cart",
                "actions:offsite_conversion.fb_pixel_purchase": "Tickets Sold",
                "actions:onsite_conversion.lead_grouped": "Leads",
                "reach": "Reach",
            }

            candidates = [
                ("purchases", "Tickets Sold"),
                ("add_to_cart", "Add to Cart"),
            ]

            for column, label in candidates:
                if column in source.columns and float(source[column].fillna(0).sum()) > 0:
                    return column, label

            if "results" in source.columns and float(source["results"].fillna(0).sum()) > 0:
                label = "Results"
                if "result_indicator" in source.columns:
                    result_rows = source[source["results"].fillna(0) > 0]
                    if not result_rows.empty:
                        indicator_mode = (
                            result_rows["result_indicator"]
                            .dropna()
                            .astype(str)
                            .str.lower()
                            .mode()
                        )
                        if not indicator_mode.empty:
                            label = indicator_labels.get(indicator_mode.iloc[0], label)
                return "results", label

            if "clicks" in source.columns and float(source["clicks"].fillna(0).sum()) > 0:
                return "clicks", "Clicks"

            if "impressions" in source.columns and float(source["impressions"].fillna(0).sum()) > 0:
                return "impressions", "Impressions"

            return "spend", "Spend"

        def format_metric_value(value: float, *, is_currency: bool = False) -> str:
            if value is None or np.isnan(value):
                return "–"
            if is_currency:
                return f"${value:,.2f}"
            if abs(value) >= 100:
                return f"{value:,.0f}"
            if abs(value) >= 10:
                return f"{value:,.1f}"
            if abs(value) >= 1:
                return f"{value:,.2f}"
            return f"{value:,.3f}"

        metric_column, metric_label = select_primary_metric(breakdown)
        cost_label = metric_label[:-1] if metric_label.endswith("s") else metric_label

        total_metric = float(breakdown.get(metric_column, pd.Series(dtype=float)).fillna(0).sum())
        total_spend = float(breakdown.get("spend", pd.Series(dtype=float)).fillna(0).sum())
        avg_cost = total_spend / total_metric if total_metric else np.nan

        summary_cols = st.columns(3)
        summary_cols[0].metric(f"Total {metric_label}", format_metric_value(total_metric))
        summary_cols[1].metric("Total Spend", format_metric_value(total_spend, is_currency=True))
        summary_cols[2].metric(
            f"Cost per {cost_label}",
            format_metric_value(avg_cost, is_currency=True),
        )

        placement_column = None
        for candidate in ["placement", "platform"]:
            if candidate in breakdown.columns:
                placement_column = candidate
                break

        device_column = None
        for candidate in ["device_platform", "impression_device"]:
            if candidate in breakdown.columns:
                device_column = candidate
                break

        cols = st.columns(2)

        if placement_column:
            placement_perf = (
                breakdown.groupby(placement_column)
                .agg(
                    {
                        "impressions": "sum",
                        "spend": "sum",
                        "clicks": "sum",
                        metric_column: "sum",
                    }
                )
                .reset_index()
            )
            placement_perf = placement_perf.rename(columns={metric_column: "primary_metric"})
            placement_perf["cost_per_metric"] = np.where(
                placement_perf["primary_metric"] > 0,
                placement_perf["spend"] / placement_perf["primary_metric"],
                np.nan,
            )
            placement_perf["ctr"] = np.where(
                placement_perf["impressions"] > 0,
                placement_perf["clicks"] / placement_perf["impressions"],
                0,
            )
            placement_perf["conversion_rate"] = np.where(
                placement_perf["impressions"] > 0,
                placement_perf["primary_metric"] / placement_perf["impressions"],
                np.nan,
            )
            placement_perf = placement_perf.sort_values("primary_metric", ascending=False)

            if placement_perf["primary_metric"].sum() <= 0:
                with cols[0]:
                    st.info(
                        f"The placement breakdown does not report any {metric_label.lower()} yet."
                    )
            else:
                with cols[0]:
                    st.markdown(f"Top placements by {metric_label.lower()}")
                    fig = px.bar(
                        placement_perf.head(10),
                        x="primary_metric",
                        y=placement_column,
                        orientation="h",
                        color="cost_per_metric",
                        color_continuous_scale="RdYlGn",
                        labels={
                            "primary_metric": metric_label,
                            placement_column: "Placement",
                            "cost_per_metric": f"Cost per {cost_label}",
                        },
                        hover_data={
                            "spend": ":$.2f",
                            "clicks": ":,.0f",
                            "ctr": ":.2%",
                            "conversion_rate": ":.2%",
                            "cost_per_metric": ":$.2f",
                        },
                    )
                    fig.update_layout(height=420)
                    st.plotly_chart(fig, use_container_width=True)

                    top_row = placement_perf.iloc[0] if not placement_perf.empty else None
                    if top_row is not None:
                        st.caption(
                            "Best placement: "
                            f"{top_row[placement_column]} — "
                            f"{format_metric_value(top_row['primary_metric'])} "
                            f"{metric_label.lower()}"
                        )
        else:
            with cols[0]:
                st.info("Placement details were not found in the uploaded file.")

        if device_column:
            device_perf = (
                breakdown.groupby(device_column)
                .agg(
                    {
                        "impressions": "sum",
                        "spend": "sum",
                        "clicks": "sum",
                        metric_column: "sum",
                    }
                )
                .reset_index()
            )
            device_perf = device_perf.rename(columns={metric_column: "primary_metric"})
            device_perf["ctr"] = np.where(
                device_perf["impressions"] > 0,
                device_perf["clicks"] / device_perf["impressions"],
                0,
            )
            device_perf["cost_per_metric"] = np.where(
                device_perf["primary_metric"] > 0,
                device_perf["spend"] / device_perf["primary_metric"],
                np.nan,
            )
            device_perf["conversion_rate"] = np.where(
                device_perf["impressions"] > 0,
                device_perf["primary_metric"] / device_perf["impressions"],
                np.nan,
            )
            device_perf = device_perf.sort_values("primary_metric", ascending=False)

            if device_perf["primary_metric"].sum() <= 0:
                with cols[1]:
                    st.info(
                        f"The device breakdown does not report any {metric_label.lower()} yet."
                    )
            else:
                with cols[1]:
                    st.markdown(f"Top devices by {metric_label.lower()}")
                    fig = px.bar(
                        device_perf.head(10),
                        x="primary_metric",
                        y=device_column,
                        orientation="h",
                        color="cost_per_metric",
                        color_continuous_scale="RdYlGn",
                        labels={
                            "primary_metric": metric_label,
                            device_column: "Device",
                            "cost_per_metric": f"Cost per {cost_label}",
                        },
                        hover_data={
                            "spend": ":$.2f",
                            "clicks": ":,.0f",
                            "ctr": ":.2%",
                            "conversion_rate": ":.2%",
                            "cost_per_metric": ":$.2f",
                        },
                    )
                    fig.update_layout(height=420)
                    st.plotly_chart(fig, use_container_width=True)

                    top_row = device_perf.iloc[0] if not device_perf.empty else None
                    if top_row is not None:
                        st.caption(
                            "Best device: "
                            f"{top_row[device_column]} — "
                            f"{format_metric_value(top_row['primary_metric'])} "
                            f"{metric_label.lower()}"
                        )
        else:
            with cols[1]:
                st.info("Device breakdown columns were not detected in the upload.")

    # ------------------------ Integrated Analysis ------------------------ #
    def create_integration_analysis(
        self,
        sales_df: pd.DataFrame,
        ads_df: pd.DataFrame,
    ) -> None:
        if sales_df is None or sales_df.empty or ads_df is None or ads_df.empty:
            st.info("Upload both ticket sales data and advertising data to view the integrated analysis.")
            return

        st.subheader("🔗 Integrated Performance")

        if "integration_date" not in sales_df.columns:
            sales_df = sales_df.copy()
            sales_df["integration_date"] = pd.to_datetime(sales_df["show_date"]).dt.date
        if "integration_date" not in ads_df.columns:
            ads_df = ads_df.copy()
            ads_df["integration_date"] = pd.to_datetime(ads_df["date"]).dt.date

        sales_dates = set(sales_df["integration_date"].dropna())
        ads_dates = set(ads_df["integration_date"].dropna())
        overlap_dates = sales_dates.intersection(ads_dates)

        col1, col2, col3 = st.columns(3)
        col1.metric("Sales Dates", len(sales_dates))
        col2.metric("Ads Dates", len(ads_dates))
        overlap_pct = (len(overlap_dates) / max(len(sales_dates), 1)) * 100
        col3.metric("Overlap", f"{overlap_pct:.1f}%")

        if not overlap_dates:
            st.info("No shared dates between advertising activity and sales reports yet.")
            return

        sales_by_date = (
            sales_df.groupby("integration_date")
            .agg({"total_sold": "sum", "sales_to_date": "sum"})
            .reset_index()
        )
        ads_by_date = (
            ads_df.groupby("integration_date")
            .agg({"impressions": "sum", "clicks": "sum", "spend": "sum", "purchases": "sum"})
            .reset_index()
        )
        merged = pd.merge(sales_by_date, ads_by_date, on="integration_date", how="inner")
        
        if merged.empty:
            st.info("No overlapping metrics found after combining the datasets.")
            return

        chart_col1, chart_col2 = st.columns(2)

        trendline_mode = "ols" if HAS_STATSMODELS else None

        with chart_col1:
            st.markdown("**Spend vs. Tickets Sold**")
            fig = px.scatter(
                merged,
                x="spend",
                y="total_sold",
                hover_data=["integration_date"],
                trendline=trendline_mode,
                labels={"spend": "Spend", "total_sold": "Tickets Sold"},
            )
            st.plotly_chart(fig, use_container_width=True)

        with chart_col2:
            st.markdown("**Impressions vs. Revenue**")
            fig = px.scatter(
                merged,
                x="impressions",
                y="sales_to_date",
                hover_data=["integration_date"],
                trendline=trendline_mode,
                labels={"impressions": "Impressions", "sales_to_date": "Revenue"},
            )
            st.plotly_chart(fig, use_container_width=True)

        if trendline_mode is None:
            st.caption(
                "Install `statsmodels` to enable regression trendlines in the integrated analysis charts."
            )

        correlations = {
            "Spend vs. Tickets": merged["spend"].corr(merged["total_sold"]),
            "Impressions vs. Tickets": merged["impressions"].corr(merged["total_sold"]),
            "Clicks vs. Tickets": merged["clicks"].corr(merged["total_sold"]),
            "Spend vs. Revenue": merged["spend"].corr(merged["sales_to_date"]),
        }

        corr_df = pd.DataFrame(
            {
                "Metric": correlations.keys(),
                "Correlation": [round(value or 0, 3) for value in correlations.values()],
            }
        )
        corr_df["Strength"] = corr_df["Correlation"].apply(
            lambda x: "Strong" if abs(x) >= 0.7 else "Moderate" if abs(x) >= 0.4 else "Weak"
        )
        st.dataframe(corr_df, use_container_width=True)

    # -------------------------- Raw Data --------------------------------- #
    def render_raw_tables(
        self, 
        sales_df: pd.DataFrame, 
        ads_data_by_type: Dict[str, pd.DataFrame]
    ) -> None:
        sales_col, ads_col = st.columns(2)
        
        with sales_col:
            st.subheader("🎟️ Ticket Sales Data")
            if sales_df is not None and not sales_df.empty:
                st.dataframe(sales_df, use_container_width=True)
                csv = sales_df.to_csv(index=False)
                st.download_button("Download ticket sales CSV", csv, "sales_data.csv", "text/csv")
            else:
                st.info("Ticket sales data is loaded automatically from the Google Sheet once available.")

        with ads_col:
            st.subheader("📣 Advertising Data")
            if ads_data_by_type:
                for key, df in ads_data_by_type.items():
                    st.markdown(f"**{key.replace('_', ' ').title()}**")
                    st.dataframe(df.head(100), use_container_width=True)
                combined = pd.concat(ads_data_by_type.values())
                csv = combined.to_csv(index=False)
                st.download_button("Download combined ads CSV", csv, "ads_data.csv", "text/csv")
            else:
                st.info("Upload the three Meta reports to inspect raw data.")


def main() -> None:
    st.set_page_config(
        page_title="Ads Analyzer v2.0",
        page_icon="🎭",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("🎭 Ads Analyzer v2.0")
    st.caption(
        "Integrated performance insights across Meta ads and live ticket sales. "
        "Upload the Meta report exports and refresh the Google Sheet sync to unlock the full analysis."
    )

    st.sidebar.header("Configuration")
    st.sidebar.write(
        "Upload the three standard Meta report exports (Days, Days + Placement + Device, Days + Time)."
    )

    sheets_connector = PublicSheetsConnector()
    ads_processor = AdsDataProcessor()
    dashboard = IntegratedDashboard()

    st.sidebar.subheader("Ticket sales data")

    if "sales_data" not in st.session_state:
        st.session_state["sales_data"] = None
        st.session_state["sales_last_refresh"] = None
        st.session_state["sales_error"] = None

    refresh_clicked = st.sidebar.button(
        "Refresh ticket sales data",
        help="Pull the latest snapshot directly from the shared Google Sheet.",
    )

    should_load_sales = (
        st.session_state["sales_data"] is None
        and st.session_state["sales_error"] is None
    ) or refresh_clicked

    if should_load_sales:
        with st.spinner("Loading ticket sales data from Google Sheets..."):
            fetched_sales = sheets_connector.load_data()

        if fetched_sales is not None and not fetched_sales.empty:
            st.session_state["sales_data"] = fetched_sales
            st.session_state["sales_last_refresh"] = datetime.utcnow()
            st.session_state["sales_error"] = None
            summary = dashboard.summarize_sales(fetched_sales)
            loaded_shows = summary.get("total_shows", 0) if summary else 0
            st.sidebar.success(
                f"Loaded {loaded_shows} show report{'s' if loaded_shows != 1 else ''} from Google Sheets."
            )
        else:
            st.session_state["sales_data"] = None
            st.session_state["sales_error"] = "Ticket sales data is unavailable."
            st.sidebar.error("Could not load ticket sales data from the Google Sheet. Please try again later.")

    sales_df = st.session_state.get("sales_data")
    sales_error = st.session_state.get("sales_error")

    sales_summary: Dict[str, float] = {}
    if sales_df is not None and not sales_df.empty:
        sales_summary = dashboard.summarize_sales(sales_df)
        if sales_summary:
            st.sidebar.metric("Shows tracked", f"{sales_summary['total_shows']:,}")
            st.sidebar.metric("Total capacity", f"{int(round(sales_summary['total_capacity'])):,}")
            st.sidebar.metric("Tickets sold", f"{int(round(sales_summary['total_sold'])):,}")
            st.sidebar.metric("Revenue to date", f"${sales_summary['total_revenue']:,.0f}")
        last_refresh = st.session_state.get("sales_last_refresh")
        if last_refresh is not None:
            st.sidebar.caption(
                f"Last refreshed: {last_refresh.strftime('%Y-%m-%d %H:%M UTC')}"
            )
    elif sales_error:
        st.sidebar.warning(
            "Ticket sales data is unavailable. Refresh once the Google Sheet is updated."
        )
    else:
        st.sidebar.info("Loading ticket sales data from Google Sheets...")

    dashboard.sales_data = sales_df

    # File uploader
    uploaded_files = st.sidebar.file_uploader(
        "Upload Meta ad exports",
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=True,
        help="Upload the three files: Days, Days + Placement + Device, Days + Time",
    )

    if uploaded_files:
        try:
            with st.spinner("Processing advertising data..."):
                ads_data_by_type, funnel_summary = ads_processor.process_ads_files(
                    uploaded_files, 
                    sales_df
                )
                dashboard.ads_data_by_type = ads_data_by_type
                dashboard.funnel_summary = funnel_summary
                
                if ads_data_by_type:
                    st.sidebar.success(f"Processed {len(ads_data_by_type)} dataset(s)")
                    for dataset_type in ads_data_by_type.keys():
                        st.sidebar.info(f"✓ {dataset_type.replace('_', ' ').title()}")
                        
        except Exception as exc:
            st.sidebar.error(f"Error processing ads: {exc}")

    # Create tabs
    tab_sales, tab_ads, tab_integration, tab_raw = st.tabs(
        ["Ticket Sales", "Advertising", "Integrated View", "Raw Data"]
    )

    with tab_sales:
        dashboard.create_sales_overview(sales_df)
        st.markdown("---")
        dashboard.render_show_health(sales_df, dashboard.funnel_summary)
        st.markdown("---")
        dashboard.create_sales_charts(sales_df)

    with tab_ads:
        days_df = dashboard.ads_data_by_type.get("days") if dashboard.ads_data_by_type else None
        placement_df = (
            dashboard.ads_data_by_type.get("days_placement_device")
            if dashboard.ads_data_by_type
            else None
        )
        dashboard.create_ads_overview(days_df)
        st.markdown("---")
        dashboard.create_ads_charts(days_df, placement_df)

    with tab_integration:
        days_df = dashboard.ads_data_by_type.get("days") if dashboard.ads_data_by_type else None
        dashboard.create_integration_analysis(sales_df, days_df)

    with tab_raw:
        dashboard.render_raw_tables(sales_df, dashboard.ads_data_by_type)

    st.markdown("---")


if __name__ == "__main__":
    main()
