"""
Data Mapper Module - v1.0
Classe para mapear e integrar dados de Sales (Google Sheets) com CSVs de Ads (Meta)
"""

import re
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple


class DataMapper:
    """
    Classe para mapear e integrar dados de Sales (Google Sheets) com CSVs de Ads (Meta).
    
    Esta classe cria uma ponte robusta entre:
    - Planilha de Sales: show_id, city, show_date, capacity, total_sold, etc.
    - CSV de Ads: Campaign name, Impressions, Clicks, Spend, Results, etc.
    """
    
    def __init__(self):
        # Mapeamento de campos Sales -> Ads
        self.field_mapping = {
            # Campos de identificação
            'show_id': 'matched_show_id',
            'city': 'city',
            'show_date': 'show_date',
            
            # Campos de vendas
            'total_sold': 'tickets_sold',
            'capacity': 'venue_capacity',
            'remaining': 'tickets_remaining',
            'sales_to_date': 'revenue',
            'occupancy_rate': 'occupancy_pct',
            
            # Campos de ads (mapeados dos CSVs)
            'spend': 'Amount spent (USD)',
            'impressions': 'Impressions',
            'clicks': 'Link clicks',
            'ctr': 'CTR (Link)',
            'cpm': 'CPM (cost per 1,000 impressions) (USD)',
            'reach': 'Reach',
            'frequency': 'Frequency',
            'results': 'Results',
            'cost_per_result': 'Cost per results'
        }
        
        # Mapeamento específico por tipo de CSV
        self.csv_mappings = {
            'days': {
                'date_field': 'Reporting starts',
                'end_date_field': 'Reporting ends',
                'campaign_field': 'Campaign name',
                'required_fields': [
                    'Amount spent (USD)', 'Impressions', 'Link clicks',
                    'CTR (Link)', 'CPM (cost per 1,000 impressions) (USD)',
                    'Reach', 'Frequency', 'Results', 'Cost per results'
                ],
                'optional_fields': ['Attribution setting', 'Ad set budget', 'Campaign delivery']
            },
            'days_placement_device': {
                'date_field': 'Reporting starts',
                'end_date_field': 'Reporting ends',
                'campaign_field': 'Campaign name',
                'dimension_fields': ['Platform', 'Placement', 'Device platform', 'Impression device'],
                'metric_fields': [
                    'Amount spent (USD)', 'Impressions', 'Link clicks',
                    'CPM (cost per 1,000 impressions) (USD)', 'Reach', 'Frequency'
                ]
            },
            'days_time': {
                'date_field': 'Reporting starts',
                'end_date_field': 'Reporting ends',
                'campaign_field': 'Campaign name',
                'dimension_fields': ['Time of day (viewer\'s time zone)'],
                'metric_fields': [
                    'Amount spent (USD)', 'Impressions', 'Link clicks',
                    'CPM (cost per 1,000 impressions) (USD)', 'Reach', 'Frequency'
                ]
            }
        }
        
        # Padrões de nomenclatura de campanha para extrair show_id
        self.campaign_patterns = [
            # Padrão principal: AAA_9999 ou AAA_9999_S9
            r'([A-Z]{2,4})[-_\s]*(\d{4})(?:[-_\s]*S(\d+))?',
            
            # Padrão com cidade por extenso: CityName_9999
            r'([A-Za-z]+)[-_\s]*(\d{4})',
            
            # Padrão legacy: US-AAA-Sales-9999
            r'US-([A-Z]{2,4})-Sales-(\d{4})',
            
            # Padrão com tour: Tour_CityName_99
            r'Tour[-_\s]+([A-Za-z]+)[-_\s]+(\d+)'
        ]
    
    def normalize_csv_data(self, df: pd.DataFrame, csv_type: str) -> pd.DataFrame:
        """
        Normaliza dados do CSV de acordo com o tipo.
        
        Args:
            df: DataFrame do CSV
            csv_type: Tipo do CSV ('days', 'days_placement_device', 'days_time')
        
        Returns:
            DataFrame normalizado
        """
        if df is None or df.empty or csv_type not in self.csv_mappings:
            return df
        
        df_normalized = df.copy()
        mapping = self.csv_mappings[csv_type]
        
        # Normalizar data
        date_field = mapping['date_field']
        if date_field in df_normalized.columns:
            df_normalized['date'] = pd.to_datetime(df_normalized[date_field], errors='coerce')
        
        # Normalizar data de fim
        end_date_field = mapping.get('end_date_field')
        if end_date_field and end_date_field in df_normalized.columns:
            df_normalized['end_date'] = pd.to_datetime(df_normalized[end_date_field], errors='coerce')
        
        # Normalizar campanha
        campaign_field = mapping['campaign_field']
        if campaign_field in df_normalized.columns:
            df_normalized['campaign'] = df_normalized[campaign_field]
        
        # Normalizar métricas numéricas
        numeric_fields = mapping.get('metric_fields', []) + mapping.get('required_fields', [])
        for field in numeric_fields:
            if field in df_normalized.columns:
                # Remover formatação e converter
                df_normalized[field] = pd.to_numeric(
                    df_normalized[field].astype(str).str.replace(',', '').str.replace('$', '').str.replace('%', ''),
                    errors='coerce'
                ).fillna(0)
        
        # Calcular métricas derivadas se necessário
        if 'Amount spent (USD)' in df_normalized.columns and 'Link clicks' in df_normalized.columns:
            df_normalized['CPC'] = df_normalized.apply(
                lambda row: row['Amount spent (USD)'] / row['Link clicks'] 
                if row['Link clicks'] > 0 else 0,
                axis=1
            )
        
        if 'Amount spent (USD)' in df_normalized.columns and 'Results' in df_normalized.columns:
            df_normalized['CPA'] = df_normalized.apply(
                lambda row: row['Amount spent (USD)'] / row['Results'] 
                if row['Results'] > 0 else 0,
                axis=1
            )
        
        return df_normalized
    
    def extract_show_id_from_campaign(self, campaign_name: str, sales_df: pd.DataFrame = None) -> Optional[str]:
        """
        Extrai show_id do nome da campanha usando múltiplos padrões.
        
        Args:
            campaign_name: Nome da campanha
            sales_df: DataFrame de vendas para validação (opcional)
        
        Returns:
            show_id extraído ou None
        """
        if not campaign_name or pd.isna(campaign_name):
            return None
        
        campaign_upper = str(campaign_name).upper()
        
        # Tentar cada padrão
        for pattern in self.campaign_patterns:
            match = re.search(pattern, campaign_upper)
            if match:
                groups = match.groups()
                
                # Construir show_id baseado nos grupos capturados
                if len(groups) >= 2:
                    city_code = groups[0]
                    show_num = groups[1]
                    sequence = groups[2] if len(groups) > 2 and groups[2] else None
                    
                    # Formato padrão: AAA_9999 ou AAA_9999_S9
                    if sequence:
                        show_id = f"{city_code}_{show_num}_S{sequence}"
                    else:
                        show_id = f"{city_code}_{show_num}"
                    
                    # Validar contra sales_df se fornecido
                    if sales_df is not None and not sales_df.empty:
                        if 'show_id' in sales_df.columns:
                            if show_id in sales_df['show_id'].values:
                                return show_id
                            # Tentar sem sequência
                            base_id = f"{city_code}_{show_num}"
                            if base_id in sales_df['show_id'].values:
                                return base_id
                    else:
                        return show_id
        
        return None
    
    def merge_sales_and_ads(
        self, 
        sales_df: pd.DataFrame, 
        ads_df: pd.DataFrame,
        how: str = 'left'
    ) -> pd.DataFrame:
        """
        Merge dados de sales com ads usando show_id como chave.
        
        Args:
            sales_df: DataFrame de vendas
            ads_df: DataFrame de anúncios (normalizado)
            how: Tipo de merge ('left', 'right', 'inner', 'outer')
        
        Returns:
            DataFrame merged
        """
        if sales_df is None or sales_df.empty:
            return ads_df
        if ads_df is None or ads_df.empty:
            return sales_df
        
        # Garantir que temos show_id em ads_df
        if 'matched_show_id' in ads_df.columns:
            ads_df['show_id'] = ads_df['matched_show_id']
        elif 'campaign' in ads_df.columns:
            # Extrair show_id das campanhas
            ads_df['show_id'] = ads_df['campaign'].apply(
                lambda x: self.extract_show_id_from_campaign(x, sales_df)
            )
        
        # Preparar agregação de ads por show
        agg_dict = {}
        if 'Amount spent (USD)' in ads_df.columns:
            agg_dict['Amount spent (USD)'] = 'sum'
        if 'Impressions' in ads_df.columns:
            agg_dict['Impressions'] = 'sum'
        if 'Link clicks' in ads_df.columns:
            agg_dict['Link clicks'] = 'sum'
        if 'Reach' in ads_df.columns:
            agg_dict['Reach'] = 'sum'
        if 'Results' in ads_df.columns:
            agg_dict['Results'] = 'sum'
        
        if not agg_dict:
            return sales_df
        
        ads_agg = ads_df.groupby('show_id', dropna=True).agg(agg_dict).reset_index()
        
        # Renomear para clareza
        rename_map = {
            'Amount spent (USD)': 'total_ad_spend',
            'Impressions': 'total_impressions',
            'Link clicks': 'total_clicks',
            'Reach': 'total_reach',
            'Results': 'total_conversions'
        }
        ads_agg.rename(columns={k: v for k, v in rename_map.items() if k in ads_agg.columns}, inplace=True)
        
        # Merge
        merged = pd.merge(
            sales_df,
            ads_agg,
            on='show_id',
            how=how,
            suffixes=('_sales', '_ads')
        )
        
        # Calcular métricas combinadas
        if 'sales_to_date' in merged.columns and 'total_ad_spend' in merged.columns:
            merged['roas'] = merged.apply(
                lambda row: row['sales_to_date'] / row['total_ad_spend'] 
                if pd.notna(row.get('total_ad_spend')) and row.get('total_ad_spend', 0) > 0 else 0,
                axis=1
            )
        
        if 'total_ad_spend' in merged.columns and 'total_sold' in merged.columns:
            merged['cpa'] = merged.apply(
                lambda row: row['total_ad_spend'] / row['total_sold']
                if pd.notna(row.get('total_sold')) and row.get('total_sold', 0) > 0 else 0,
                axis=1
            )
        
        if 'total_sold' in merged.columns and 'total_clicks' in merged.columns:
            merged['click_to_purchase_rate'] = merged.apply(
                lambda row: (row['total_sold'] / row['total_clicks'] * 100)
                if pd.notna(row.get('total_clicks')) and row.get('total_clicks', 0) > 0 else 0,
                axis=1
            )
        
        return merged
    
    def create_campaign_name_from_show_id(self, show_id: str) -> str:
        """
        Cria nome de campanha sugerido a partir do show_id.
        
        Args:
            show_id: ID do show (ex: 'WDC_0927_S2')
        
        Returns:
            Nome de campanha formatado
        """
        if not show_id:
            return ""
        
        parts = show_id.split('_')
        if len(parts) >= 2:
            city = parts[0]
            date = parts[1]
            sequence = parts[2] if len(parts) > 2 else ""
            
            if sequence:
                return f"{city}-Sales-{date}-{sequence}"
            else:
                return f"{city}-Sales-{date}"
        
        return show_id
    
    def validate_data_quality(self, df: pd.DataFrame, data_type: str) -> Dict[str, any]:
        """
        Valida qualidade dos dados e retorna relatório.
        
        Args:
            df: DataFrame para validar
            data_type: Tipo de dados ('sales' ou 'ads')
        
        Returns:
            Dict com métricas de qualidade
        """
        if df is None or df.empty:
            return {
                'valid': False,
                'error': 'DataFrame está vazio',
                'row_count': 0
            }
        
        report = {
            'valid': True,
            'row_count': len(df),
            'column_count': len(df.columns),
            'missing_values': {},
            'data_types': {},
            'warnings': []
        }
        
        # Verificar valores faltantes
        for col in df.columns:
            missing = df[col].isna().sum()
            if missing > 0:
                pct = (missing / len(df)) * 100
                report['missing_values'][col] = {
                    'count': int(missing),
                    'percentage': round(pct, 2)
                }
                if pct > 50:
                    report['warnings'].append(f"⚠️ {col}: {pct:.1f}% valores faltantes")
        
        # Verificar tipos de dados
        for col in df.columns:
            report['data_types'][col] = str(df[col].dtype)
        
        # Validações específicas por tipo
        if data_type == 'sales':
            required_fields = ['show_id', 'city', 'show_date', 'capacity', 'total_sold']
            for field in required_fields:
                if field not in df.columns:
                    report['warnings'].append(f"❌ Campo obrigatório ausente: {field}")
                    report['valid'] = False
        
        elif data_type == 'ads':
            required_fields = ['Campaign name', 'Amount spent (USD)', 'Impressions']
            for field in required_fields:
                if field not in df.columns:
                    report['warnings'].append(f"❌ Campo obrigatório ausente: {field}")
                    report['valid'] = False
        
        return report


def integrate_sales_and_ads_data(
    sales_df: pd.DataFrame,
    ads_days_df: pd.DataFrame,
    ads_placement_df: Optional[pd.DataFrame] = None,
    ads_time_df: Optional[pd.DataFrame] = None
) -> Tuple[pd.DataFrame, Dict[str, any]]:
    """
    Integra dados de vendas com todos os tipos de CSVs de anúncios.
    
    Args:
        sales_df: DataFrame de vendas (Google Sheets)
        ads_days_df: CSV Days
        ads_placement_df: CSV Days + Placement + Device (opcional)
        ads_time_df: CSV Days + Time (opcional)
    
    Returns:
        Tuple contendo:
        - DataFrame integrado
        - Dict com estatísticas da integração
    """
    mapper = DataMapper()
    stats = {
        'sales_rows': len(sales_df) if sales_df is not None else 0,
        'ads_rows': len(ads_days_df) if ads_days_df is not None else 0,
        'matched_shows': 0,
        'unmatched_shows': 0,
        'total_shows': 0
    }
    
    # Normalizar dados de ads
    if ads_days_df is not None:
        ads_days_normalized = mapper.normalize_csv_data(ads_days_df, 'days')
    else:
        ads_days_normalized = None
    
    if ads_placement_df is not None:
        ads_placement_normalized = mapper.normalize_csv_data(ads_placement_df, 'days_placement_device')
    else:
        ads_placement_normalized = None
    
    if ads_time_df is not None:
        ads_time_normalized = mapper.normalize_csv_data(ads_time_df, 'days_time')
    else:
        ads_time_normalized = None
    
    # Merge principal
    integrated = mapper.merge_sales_and_ads(sales_df, ads_days_normalized, how='left')
    
    # Estatísticas
    if 'show_id' in integrated.columns:
        stats['total_shows'] = len(integrated['show_id'].unique())
        if 'total_ad_spend' in integrated.columns:
            stats['matched_shows'] = len(integrated[integrated['total_ad_spend'].notna()]['show_id'].unique())
            stats['unmatched_shows'] = stats['total_shows'] - stats['matched_shows']
    
    return integrated, stats


def safe_numeric(value, default=0):
    """
    Converte valor para numérico de forma segura.
    
    Args:
        value: Valor a ser convertido
        default: Valor padrão se conversão falhar
    
    Returns:
        Valor numérico ou default
    """
    if pd.isna(value) or value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
