"""
Conector para Google Sheets público com mapeamento detalhado
Análise linha a linha da planilha de vendas de shows
"""

import pandas as pd
import numpy as np
import requests
import csv
from io import StringIO
from datetime import datetime, timedelta
import re
import logging

logger = logging.getLogger(__name__)

class PublicSheetsConnector:
    """
    Conector para Google Sheets público - análise minuciosa da estrutura
    """
    
    def __init__(self):
        # URL pública da planilha (formato CSV export)
        self.sheet_id = "1hVm1OALKQ244zuJBQV0SsQT08A2_JTDlPytUNULRofA"
        self.csv_url = f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/export?format=csv&gid=0"
        
        # Mapeamento detalhado das colunas identificadas na planilha
        self.column_mapping = {
            0: 'show_id',           # Show ID (Ex: WDC_0927, OTW_1006)
            1: 'show_date',         # Show Date (Data do show)
            2: 'report_date',       # Report Date (Data do relatório)
            3: 'show_name',         # Show Name (Ex: 27.Wash DC, 6.Ottawa)
            4: 'capacity',          # Capacity (Capacidade total)
            5: 'venue_holds',       # Venue holds
            6: 'wheelchair_companions', # Wheelchair & Companions
            7: 'camera',            # Camera
            8: 'artists_hold',      # Artist's Hold
            9: 'kills',             # Kills
            10: 'yesterday_sales',  # Yesterday (vendas de ontem)
            11: 'today_sold',       # Today's Sold (vendas de hoje)
            12: 'sales_to_date',    # Sales to date (vendas até a data)
            13: 'total_sold',       # Total Sold (total vendido)
            14: 'remaining',        # Remaining (restante)
            15: 'sold_percentage',  # Sold % (percentual vendido)
            16: 'atp',              # ATP (Average Ticket Price)
            17: 'report_message'    # Report Message
        }
        
        # Padrões para identificar diferentes tipos de linhas
        self.patterns = {
            'month_header': r'^(September|October|November|December)$',
            'month_asterisk': r'^\*(September|October|November|December)\*$',
            'show_id': r'^[A-Z]{2,3}_\d{4}(_S\d+)?$',  # Ex: WDC_0927, WDC_0927_S3
            'end_row': r'^endRow$',
            'summary_line': r'^\d+\s*\(\+\d+\)\s*\d+',  # Ex: "1371 (+8) 1379"
            'date_format': r'^\d{4}-\d{2}-\d{2}$'
        }
    
    def load_data(self):
        """
        Carrega dados da planilha pública e faz análise linha a linha
        
        Returns:
            pd.DataFrame: DataFrame com dados limpos e mapeados
        """
        try:
            # Fazer download dos dados
            response = requests.get(self.csv_url, timeout=30)
            response.raise_for_status()
            
            # Parsear CSV
            csv_data = StringIO(response.text)
            reader = csv.reader(csv_data)
            
            # Análise linha a linha
            raw_data = list(reader)
            processed_data = self._analyze_rows_minutely(raw_data)
            
            # Converter para DataFrame
            df = pd.DataFrame(processed_data)
            
            # Aplicar limpeza e transformações
            df = self._clean_and_transform(df)
            
            logger.info(f"Dados carregados com sucesso: {len(df)} registros de shows")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {str(e)}")
            return None
    
    def _analyze_rows_minutely(self, raw_data):
        """
        Análise minuciosa linha por linha da planilha
        
        Args:
            raw_data (list): Dados brutos do CSV
            
        Returns:
            list: Lista de dicionários com dados de shows válidos
        """
        processed_shows = []
        current_month = None
        
        logger.info(f"Analisando {len(raw_data)} linhas da planilha...")
        
        for row_idx, row in enumerate(raw_data):
            if not row or len(row) == 0:
                continue
                
            # Análise do primeiro campo para determinar tipo da linha
            first_cell = str(row[0]).strip() if row[0] else ""
            
            # Log detalhado para debug
            logger.debug(f"Linha {row_idx}: '{first_cell}' | Colunas: {len(row)}")
            
            # Identificar tipo da linha
            line_type = self._identify_line_type(first_cell, row)
            
            if line_type == "month_header":
                current_month = first_cell
                logger.info(f"Encontrado cabeçalho de mês: {current_month}")
                continue
                
            elif line_type == "show_data":
                # Extrair dados do show
                show_data = self._extract_show_data(row, row_idx, current_month)
                if show_data:
                    processed_shows.append(show_data)
                    logger.debug(f"Show extraído: {show_data['show_id']} - {show_data['show_name']}")
                    
            elif line_type == "summary_line":
                # Linha de resumo que segue um show (ignorar)
                logger.debug(f"Linha de resumo ignorada: {first_cell}")
                continue
                
            elif line_type in ["month_asterisk", "end_row", "header"]:
                # Linhas especiais (ignorar)
                logger.debug(f"Linha especial ignorada ({line_type}): {first_cell}")
                continue
                
            else:
                # Linha não identificada
                logger.debug(f"Linha não identificada: {first_cell}")
        
        logger.info(f"Total de shows processados: {len(processed_shows)}")
        return processed_shows
    
    def _identify_line_type(self, first_cell, row):
        """
        Identifica o tipo de linha baseado em padrões
        
        Args:
            first_cell (str): Primeira célula da linha
            row (list): Linha completa
            
        Returns:
            str: Tipo identificado da linha
        """
        # Verificar padrões conhecidos
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
            
        # Verificar se é linha de cabeçalho
        if "Show ID" in first_cell or "Show Date" in first_cell:
            return "header"
            
        # Se tem mais de 10 colunas e segunda coluna parece data, pode ser show
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
        """
        Extrai dados de um show específico
        
        Args:
            row (list): Linha com dados do show
            row_idx (int): Índice da linha
            current_month (str): Mês atual sendo processado
            
        Returns:
            dict: Dicionário com dados do show
        """
        try:
            # Garantir que temos colunas suficientes
            if len(row) < 18:
                logger.warning(f"Linha {row_idx} tem apenas {len(row)} colunas, esperado 18")
                return None
            
            # Extrair dados usando mapeamento de colunas
            show_data = {}
            
            for col_idx, field_name in self.column_mapping.items():
                try:
                    value = row[col_idx] if col_idx < len(row) else None
                    show_data[field_name] = self._clean_cell_value(value, field_name)
                except Exception as e:
                    logger.warning(f"Erro ao extrair campo {field_name} na linha {row_idx}: {e}")
                    show_data[field_name] = None
            
            # Adicionar metadados
            show_data['source_row'] = row_idx
            show_data['current_month'] = current_month
            show_data['extraction_date'] = datetime.now().isoformat()
            
            # Validar dados essenciais
            if not show_data.get('show_id') or not show_data.get('show_name'):
                logger.warning(f"Linha {row_idx}: dados essenciais faltando")
                return None
            
            return show_data
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados da linha {row_idx}: {e}")
            return None
    
    def _clean_cell_value(self, value, field_name):
        """
        Limpa valor individual de célula
        
        Args:
            value: Valor da célula
            field_name (str): Nome do campo
            
        Returns:
            Valor limpo
        """
        if value is None or value == "":
            return None
            
        # Converter para string
        str_value = str(value).strip()
        
        # Campos monetários
        if field_name in ['sales_to_date']:
            # Remover formatação monetária
            cleaned = re.sub(r'[$R$,\s]', '', str_value)
            try:
                return float(cleaned)
            except:
                return None
        
        # Campos numéricos
        if field_name in ['capacity', 'venue_holds', 'wheelchair_companions', 'camera', 
                         'artists_hold', 'kills', 'yesterday_sales', 'today_sold', 
                         'total_sold', 'remaining', 'sold_percentage', 'atp']:
            try:
                # Remover vírgulas e espaços
                cleaned = re.sub(r'[,\s]', '', str_value)
                return float(cleaned) if cleaned else None
            except:
                return None
        
        # Campos de data
        if field_name in ['show_date', 'report_date']:
            try:
                return pd.to_datetime(str_value)
            except:
                return None
        
        # Campos de texto
        return str_value if str_value else None
    
    def _clean_and_transform(self, df):
        """
        Aplica limpeza e transformações finais
        
        Args:
            df (pd.DataFrame): DataFrame bruto
            
        Returns:
            pd.DataFrame: DataFrame limpo
        """
        if df.empty:
            return df
        
        # Filtrar registros válidos
        df = df[df['show_id'].notna() & (df['show_id'] != '')]
        
        # Converter tipos
        df = self._convert_data_types(df)
        
        # Adicionar campos calculados
        df = self._add_calculated_fields(df)
        
        # Extrair informações adicionais
        df = self._extract_additional_info(df)
        
        return df.reset_index(drop=True)
    
    def _convert_data_types(self, df):
        """Converte tipos de dados"""
        # Datas
        for col in ['show_date', 'report_date']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Numéricos
        numeric_cols = ['capacity', 'venue_holds', 'wheelchair_companions', 'camera',
                       'artists_hold', 'kills', 'yesterday_sales', 'today_sold',
                       'total_sold', 'remaining', 'sold_percentage', 'atp', 'sales_to_date']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def _add_calculated_fields(self, df):
        """Adiciona campos calculados"""
        # Taxa de ocupação recalculada
        df['occupancy_rate'] = np.where(
            df['capacity'] > 0,
            (df['total_sold'] / df['capacity']) * 100,
            0
        )
        
        # Preço médio do ingresso
        df['avg_ticket_price'] = np.where(
            df['total_sold'] > 0,
            df['sales_to_date'] / df['total_sold'],
            0
        )
        
        # Receita potencial total
        df['potential_revenue'] = df['capacity'] * df['avg_ticket_price']
        
        # Receita perdida
        df['lost_revenue'] = (df['capacity'] - df['total_sold']) * df['avg_ticket_price']
        
        # Categoria de performance
        df['performance_category'] = pd.cut(
            df['occupancy_rate'],
            bins=[0, 50, 75, 90, 100],
            labels=['Baixa', 'Média', 'Alta', 'Esgotado'],
            include_lowest=True
        )
        
        return df
    
    def _extract_additional_info(self, df):
        """Extrai informações adicionais dos dados"""
        # Extrair cidade do nome do show
        df['city'] = df['show_name'].str.extract(r'\.([A-Za-z\s]+)', expand=False)
        df['city'] = df['city'].str.strip()
        
        # Identificar shows múltiplos (mesmo dia/local)
        df['is_multi_show'] = df['show_id'].str.contains('_S\d+', na=False)
        df['show_sequence'] = df['show_id'].str.extract(r'_S(\d+)', expand=False)
        df['show_sequence'] = pd.to_numeric(df['show_sequence'], errors='coerce')
        
        # Identificar código da cidade
        df['city_code'] = df['show_id'].str.extract(r'^([A-Z]{2,3})_', expand=False)
        
        # Extrair data do show ID
        df['show_date_from_id'] = df['show_id'].str.extract(r'_(\d{4})', expand=False)
        
        return df
    
    def get_data_summary(self, df):
        """
        Gera resumo detalhado dos dados carregados
        
        Args:
            df (pd.DataFrame): DataFrame com dados
            
        Returns:
            dict: Resumo dos dados
        """
        if df is None or df.empty:
            return {"error": "Nenhum dado disponível"}
        
        summary = {
            "total_shows": len(df),
            "unique_cities": df['city'].nunique() if 'city' in df.columns else 0,
            "total_capacity": df['capacity'].sum(),
            "total_sold": df['total_sold'].sum(),
            "total_revenue": df['sales_to_date'].sum(),
            "avg_occupancy": df['occupancy_rate'].mean(),
            "date_range": {
                "start": df['show_date'].min(),
                "end": df['show_date'].max()
            },
            "cities": df['city'].value_counts().to_dict() if 'city' in df.columns else {},
            "performance_distribution": df['performance_category'].value_counts().to_dict() if 'performance_category' in df.columns else {},
            "data_quality": {
                "complete_records": df.dropna().shape[0],
                "missing_revenue": df['sales_to_date'].isnull().sum(),
                "missing_dates": df['show_date'].isnull().sum()
            }
        }
        
        return summary
    
    def create_sample_ads_data_mapping(self, df):
        """
        Cria estrutura de dados compatível com arquivos de sample de anúncios
        Para facilitar o join entre dados de vendas e anúncios
        
        Args:
            df (pd.DataFrame): DataFrame com dados de vendas
            
        Returns:
            dict: Mapeamento para integração com dados de anúncios
        """
        if df is None or df.empty:
            return {}
        
        # Estrutura típica esperada em arquivos de anúncios
        mapping = {
            "campaign_mapping": {
                # Mapear cidades para campanhas
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
                # Mapear datas para análise temporal
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