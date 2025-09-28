"""Streamlit application for integrated ad and ticket sales analytics."""

from __future__ import annotations

import importlib.util
import io
import re
import warnings
from dataclasses import dataclass
from datetime import date
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
    """Handles ad data ingestion, normalization, and enrichment."""

    def __init__(self):
        self.standard_column_aliases: Dict[str, List[str]] = {
            "date": [
                "reporting_starts",
                "date",
                "day",
                "date_start",
                "created_time",
            ],
            "campaign_name": ["campaign_name", "campaign", "campaign id", "campaign"],
            "ad_set_name": ["ad_set_name", "ad set name"],
            "ad_name": ["ad_name", "ad name"],
            "impressions": ["impressions"],
            "reach": ["reach"],
            "frequency": ["frequency"],
            "clicks": ["clicks", "link_clicks", "link clicks"],
            "spend": [
                "spend",
                "amount_spent",
                "amount spent",
                "amount spent (usd)",
            ],
            "ctr": ["ctr", "ctr (link)", "click_through_rate"],
            "cpc": ["cpc", "cost_per_click"],
            "cpm": [
                "cpm",
                "cpm (cost per 1,000 impressions)",
                "cpm (cost per 1,000 impressions) (usd)",
            ],
            "results": ["results"],
            "result_indicator": ["result_indicator", "result indicator"],
            "ends": ["ends"],
            "starts": ["starts"],
            "placement": ["placement"],
            "platform": ["platform"],
            "device_platform": ["device platform", "device_platform"],
            "impression_device": ["impression device"],
            "time_of_day": ["time of day (viewer's time zone)", "time"],
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
        return re.sub(r"[^a-z0-9]", "", col.lower())

    def detect_and_normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return df

        normalized_df = df.copy()

        col_map: Dict[str, str] = {}
        normalized_existing = {
            self._normalize_column_name(col): col for col in normalized_df.columns
        }

        for standard, aliases in self.standard_column_aliases.items():
            for alias in aliases:
                normalized_alias = self._normalize_column_name(alias)
                if normalized_alias in normalized_existing:
                    current_name = normalized_existing[normalized_alias]
                    if standard not in normalized_df.columns:
                        col_map[current_name] = standard
                    break

        if col_map:
            normalized_df = normalized_df.rename(columns=col_map)

        return normalized_df

    def identify_dataset_type(self, df: pd.DataFrame) -> Optional[str]:
        if df is None:
            return None

        normalized_columns = {self._normalize_column_name(col) for col in df.columns}

        if "timeofdayviewerstimezone" in normalized_columns or "timeofday" in normalized_columns:
            return "days_time"
        if "placement" in normalized_columns or "platform" in normalized_columns:
            return "days_placement_device"
        if {"adsetname", "date"}.issubset(normalized_columns) or {"reportingstarts", "adsetname"}.issubset(normalized_columns):
            return "days"
        return None

    def calculate_missing_kpis(self, df: pd.DataFrame) -> pd.DataFrame:
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
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        if "impressions" in df.columns and "clicks" in df.columns and "ctr" not in df.columns:
            df["ctr"] = np.where(
                df["impressions"] > 0, (df["clicks"] / df["impressions"]) * 100, 0
            )

        if "spend" in df.columns and "clicks" in df.columns and "cpc" not in df.columns:
            df["cpc"] = np.where(df["clicks"] > 0, df["spend"] / df["clicks"], 0)

        if "spend" in df.columns and "impressions" in df.columns and "cpm" not in df.columns:
            df["cpm"] = np.where(
                df["impressions"] > 0, (df["spend"] / df["impressions"]) * 1000, 0
            )

        return df

    def normalize_funnel_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return df

        normalized_columns = {
            self._normalize_column_name(col): col for col in df.columns
        }

        for target, aliases in self.funnel_column_aliases.items():
            for alias in aliases:
                normalized_alias = self._normalize_column_name(alias)
                if normalized_alias in normalized_columns:
                    source_col = normalized_columns[normalized_alias]
                    df[target] = df[source_col]
                    break
            else:
                if target not in df.columns:
                    df[target] = 0

        if "result_indicator" in df.columns and "results" in df.columns:
            df = df.copy()
            df["results"] = pd.to_numeric(df["results"], errors="coerce")
            for alias, target in self.funnel_indicator_aliases.items():
                mask = df["result_indicator"].fillna("").str.lower() == alias
                if mask.any():
                    df.loc[mask, target] = df.loc[mask, "results"].astype(float)

        return df

    def process_ads_files(
        self, uploaded_files: List[st.runtime.uploaded_file_manager.UploadedFile], sales_df: pd.DataFrame
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, FunnelSummary]]:
        data_by_type: Dict[str, pd.DataFrame] = {}
        read_errors: List[str] = []

        for uploaded in uploaded_files:
            try:
                content = uploaded.read()
                buffer = io.BytesIO(content)
                if uploaded.name.lower().endswith(".csv"):
                    df = pd.read_csv(buffer)
                else:
                    df = pd.read_excel(buffer)

                df = self.detect_and_normalize_columns(df)
                df = self.calculate_missing_kpis(df)
                df = self.normalize_funnel_columns(df)

                dataset_type = self.identify_dataset_type(df)
                if dataset_type is None:
                    read_errors.append(uploaded.name)
                    continue

                df["source_file"] = uploaded.name
                data_by_type[dataset_type] = df
            except Exception as exc:  # pragma: no cover - defensive
                read_errors.append(f"{uploaded.name}: {exc}")

        required_types = {"days", "days_placement_device", "days_time"}
        missing_types = required_types - data_by_type.keys()
        if missing_types:
            raise ValueError(
                "Missing required files. Please upload reports that match the 'Days', "
                "'Days + Placement + Device', and 'Days + Time' exports."
            )
        if read_errors:
            st.warning(
                "Some uploaded files could not be processed: " + ", ".join(read_errors)
            )

        enriched_days = self.enrich_ads_dataframe(data_by_type["days"], sales_df)
        data_by_type["days"] = enriched_days
        funnel_summary = self.calculate_funnel_summary(enriched_days)
        return data_by_type, funnel_summary

    def enrich_ads_dataframe(
        self, df: pd.DataFrame, sales_df: pd.DataFrame
    ) -> pd.DataFrame:
        if df is None or df.empty:
            return df

        df = df.copy()

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        elif "reporting_starts" in df.columns:
            df["date"] = pd.to_datetime(df["reporting_starts"], errors="coerce")

        if "ad_set_name" not in df.columns and "ad set name" in df.columns:
            df = df.rename(columns={"ad set name": "ad_set_name"})

        if "campaign_name" not in df.columns and "campaign" in df.columns:
            df["campaign_name"] = df["campaign"]
        if "campaign_name" not in df.columns:
            df["campaign_name"] = df.get("ad_set_name")

        show_lookup = self._build_show_lookup(sales_df)

        df["matched_show_id"] = df.apply(
            lambda row: self._match_show_identifier(row, show_lookup), axis=1
        )

        return df

    def _build_show_lookup(self, sales_df: pd.DataFrame) -> Dict[str, Dict[int, str]]:
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
        text_candidates = [
            str(row.get("campaign_name", "")),
            str(row.get("ad_set_name", "")),
            str(row.get("ad_name", "")),
        ]
        merged_text = " ".join([t for t in text_candidates if t])
        if not merged_text:
            return None

        show_id = self._extract_show_id_from_text(merged_text)
        if show_id:
            return show_id

        return self._fallback_show_match(merged_text, show_lookup)

    def _extract_show_id_from_text(self, text: str) -> Optional[str]:
        match = re.search(r"([A-Z]{2,3}_\d{4}(?:_S\d+)?)", text.upper())
        if match:
            return match.group(1)
        return None

    def _normalize_text(self, text: str) -> str:
        return re.sub(r"[^a-z0-9]", "", text.lower())

    def _fallback_show_match(
        self, text: str, show_lookup: Dict[str, Dict[int, str]]
    ) -> Optional[str]:
        if not show_lookup:
            return None

        normalized_text = self._normalize_text(text)
        sequence = 1
        sequence_match = re.search(r"#\s*(\d{1,2})", text.lower())
        if not sequence_match:
            sequence_match = re.search(r"\b(?:show|s)(\d{1,2})\b", text.lower())
        if sequence_match:
            sequence = int(sequence_match.group(1))

        for city_key, sequences in show_lookup.items():
            if city_key and city_key in normalized_text:
                if sequence in sequences:
                    return sequences[sequence]
                # fallback to first sequence available
                return next(iter(sequences.values()))
        return None

    def calculate_funnel_summary(self, df: pd.DataFrame) -> Dict[str, FunnelSummary]:
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

    # ----------------------------- Sales --------------------------------- #
    def create_sales_overview(self, df: pd.DataFrame) -> None:
        if df is None or df.empty:
            st.warning("No ticket sales data available yet.")
            return

        st.subheader("🎫 Ticket Sales Overview")

        total_shows = len(df["show_id"].unique())
        total_capacity = df["capacity"].sum()
        total_sold = df["total_sold"].sum()
        total_revenue = df["sales_to_date"].sum()
        avg_occupancy = df["occupancy_rate"].mean()
        cities_count = df["city"].nunique()
        sold_out_shows = (df["occupancy_rate"] >= 99).sum()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Shows", f"{total_shows:,}")
        col2.metric("Total Capacity", f"{int(total_capacity):,}")
        col3.metric("Tickets Sold", f"{int(total_sold):,}")
        col4.metric("Revenue to Date", f"${total_revenue:,.0f}")

        col5, col6, col7, col8 = st.columns(4)
        col5.metric("Average Occupancy", f"{avg_occupancy:.1f}%")
        col6.metric("Average Ticket Price", f"${df['avg_ticket_price'].mean():,.0f}")
        col7.metric("Cities", f"{cities_count}")
        col8.metric("Sold Out", f"{sold_out_shows}")

    def create_sales_charts(self, df: pd.DataFrame) -> None:
        if df is None or df.empty:
            return

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Top Cities by Tickets Sold**")
            if {"city", "total_sold", "capacity"}.issubset(df.columns):
                city_performance = (
                    df.groupby("city")
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
            if "occupancy_rate" in df.columns:
                fig = px.histogram(
                    df,
                    x="occupancy_rate",
                    nbins=20,
                    labels={"occupancy_rate": "Occupancy %"},
                    color_discrete_sequence=["#1f77b4"],
                )
                fig.update_layout(height=420)
                st.plotly_chart(fig, use_container_width=True)

        if "show_date" in df.columns and df["show_date"].notna().any():
            st.markdown("**Ticket Sales over Time**")
            daily = (
                df.groupby("show_date").agg({"today_sold": "sum", "sales_to_date": "sum", "total_sold": "sum"}).reset_index()
            )
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=daily["show_date"],
                    y=daily["total_sold"],
                    mode="lines+markers",
                    name="Total Sold",
                    line=dict(color="#1f77b4", width=2),
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=daily["show_date"],
                    y=daily["today_sold"],
                    mode="lines+markers",
                    name="Sold Today",
                    line=dict(color="#ff7f0e", width=2),
                )
            )
            fig.update_layout(
                height=420,
                xaxis_title="Show Date",
                yaxis_title="Tickets",
                hovermode="x unified",
            )
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

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Days to Show", days_to_show)
        col2.metric("Occupancy", f"{occupancy:.1f}%")
        col3.metric("Tickets Remaining", f"{int(remaining_tickets):,}")
        col4.metric(
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
        cadence = show_records.tail(7)
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

    def create_ads_charts(self, df: pd.DataFrame) -> None:
        if df is None or df.empty:
            return

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Spend vs. Purchases by Ad Set**")
            if {"ad_set_name", "spend", "purchases"}.issubset(df.columns):
                perf = (
                    df.groupby("ad_set_name")
                    .agg({"spend": "sum", "clicks": "sum", "purchases": "sum"})
                    .reset_index()
                )
                perf["ctr"] = np.where(
                    perf["spend"] > 0, (perf["purchases"] / perf["spend"]) * 100, 0
                )
                fig = px.scatter(
                    perf,
                    x="spend",
                    y="purchases",
                    size="clicks",
                    hover_data=["ad_set_name"],
                    color="ctr",
                    color_continuous_scale="RdYlGn",
                    labels={"spend": "Spend", "purchases": "Purchases", "ctr": "Purchases per $100"},
                )
                fig.update_layout(height=420)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Performance over Time**")
            if "date" in df.columns:
                daily = (
                    df.groupby("date").agg({"impressions": "sum", "clicks": "sum", "spend": "sum", "purchases": "sum"}).reset_index()
                )
                fig = make_subplots(rows=2, cols=2, subplot_titles=["Impressions", "Clicks", "Spend", "Purchases"])
                fig.add_trace(go.Scatter(x=daily["date"], y=daily["impressions"], line=dict(color="#1f77b4")), row=1, col=1)
                fig.add_trace(go.Scatter(x=daily["date"], y=daily["clicks"], line=dict(color="#ff7f0e")), row=1, col=2)
                fig.add_trace(go.Scatter(x=daily["date"], y=daily["spend"], line=dict(color="#2ca02c")), row=2, col=1)
                fig.add_trace(go.Scatter(x=daily["date"], y=daily["purchases"], line=dict(color="#d62728")), row=2, col=2)
                fig.update_layout(height=500, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

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
            sales_df.groupby("integration_date").agg({"total_sold": "sum", "sales_to_date": "sum"}).reset_index()
        )
        ads_by_date = (
            ads_df.groupby("integration_date").agg({"impressions": "sum", "clicks": "sum", "spend": "sum", "purchases": "sum"}).reset_index()
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
    def render_raw_tables(self, sales_df: pd.DataFrame, ads_data_by_type: Dict[str, pd.DataFrame]) -> None:
        sales_col, ads_col = st.columns(2)
        with sales_col:
            st.subheader("🎟️ Ticket Sales Data")
            if sales_df is not None and not sales_df.empty:
                st.dataframe(sales_df, use_container_width=True)
                csv = sales_df.to_csv(index=False)
                st.download_button("Download ticket sales CSV", csv, "sales_data.csv", "text/csv")
            else:
                st.info("Load the ticket sales sheet to view details.")

        with ads_col:
            st.subheader("📣 Advertising Data")
            if ads_data_by_type:
                for key, df in ads_data_by_type.items():
                    st.markdown(f"**{key.replace('_', ' ').title()}**")
                    st.dataframe(df, use_container_width=True)
                combined = pd.concat(ads_data_by_type.values())
                csv = combined.to_csv(index=False)
                st.download_button("Download combined ads CSV", csv, "ads_data.csv", "text/csv")
            else:
                st.info("Upload the three Meta reports (Days, Days + Placement + Device, Days + Time) to inspect raw data.")


def main() -> None:
    st.set_page_config(
        page_title="Ads Analyzer v3.0",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("📊 Ads Analyzer v3.0")
    st.caption(
        "Integrated performance insights across Meta ads and live ticket sales. Upload the Meta report exports (Days, Days + Placement + Device, Days + Time) to unlock the full analysis."
    )

    st.sidebar.header("Configuration")
    st.sidebar.write(
        "Upload the three standard Meta report exports exactly as provided in the samples (Days, Days + Placement + Device, Days + Time)."
    )

    sheets_connector = PublicSheetsConnector()
    ads_processor = AdsDataProcessor()
    dashboard = IntegratedDashboard()

    if "sales_data" not in st.session_state:
        with st.spinner("Loading ticket sales from Google Sheets..."):
            sales_data = sheets_connector.load_data()
            st.session_state["sales_data"] = sales_data
            if sales_data is not None:
                summary = sheets_connector.get_data_summary(sales_data)
                st.sidebar.success(f"Loaded {summary.get('total_shows', 0)} show reports")
            else:
                st.sidebar.error("Failed to load the public sheet. Please refresh the page.")

    if st.sidebar.button("Refresh ticket sales"):
        with st.spinner("Refreshing ticket sales data..."):
            st.session_state["sales_data"] = sheets_connector.load_data()

    sales_df = st.session_state.get("sales_data")
    dashboard.sales_data = sales_df

    uploaded_files = st.sidebar.file_uploader(
        "Upload Meta ad exports",
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=True,
        help="Upload the three files that match the samples in the repository (Days, Days + Placement + Device, Days + Time).",
    )

    if uploaded_files:
        try:
            ads_data_by_type, funnel_summary = ads_processor.process_ads_files(uploaded_files, sales_df)
            dashboard.ads_data_by_type = ads_data_by_type
            dashboard.funnel_summary = funnel_summary
            st.sidebar.success("Advertising data processed successfully.")
        except ValueError as exc:
            st.sidebar.error(str(exc))
        except Exception as exc:  # pragma: no cover - defensive
            st.sidebar.error(f"Unexpected error while processing ads: {exc}")

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
        dashboard.create_ads_overview(days_df)
        st.markdown("---")
        dashboard.create_ads_charts(days_df)

    with tab_integration:
        days_df = dashboard.ads_data_by_type.get("days") if dashboard.ads_data_by_type else None
        dashboard.create_integration_analysis(sales_df, days_df)

    with tab_raw:
        dashboard.render_raw_tables(sales_df, dashboard.ads_data_by_type)

    st.markdown("---")
    st.caption("Built with ❤️ using Streamlit · Ads Analyzer v3.0")


if __name__ == "__main__":
    main()
