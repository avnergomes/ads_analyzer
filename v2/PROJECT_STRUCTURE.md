# 📁 Estrutura do Projeto - Ads Analyzer v2.0

```
ads_analyzer/v2/
│
├── 📄 app.py                          # Aplicação principal Streamlit
├── 📄 public_sheets_connector.py      # Conector do Google Sheets
├── 📄 requirements.txt                # Dependências Python
│
├── 📚 Documentação
│   ├── README.md                      # Documentação principal
│   ├── QUICKSTART.md                  # Guia de início rápido
│   ├── EXAMPLES.md                    # Exemplos de uso
│   ├── TROUBLESHOOTING.md             # Solução de problemas
│   ├── DEPLOYMENT.md                  # Guia de deployment
│   ├── CHANGELOG.md                   # Histórico de mudanças
│   └── LICENSE                        # Licença MIT
│
├── 🔧 Ferramentas
│   ├── validate_csv.py                # Validador de CSV
│   └── test_installation.py           # Teste de instalação
│
├── ⚙️ Configuração
│   ├── .streamlit/
│   │   ├── config.toml                # Configurações do Streamlit
│   │   └── secrets.toml.example       # Template de secrets
│   └── .gitignore                     # Arquivos ignorados pelo Git
│
└── 📊 Dados (não commitados)
    ├── Days.csv                       # Upload do usuário
    ├── Days Placement Device.csv      # Upload do usuário
    └── Days Time.csv                  # Upload do usuário
```

## 📝 Descrição dos Arquivos

### Arquivos Principais

#### `app.py`
**Descrição:** Aplicação principal do Streamlit  
**Linhas de código:** ~1,500  
**Responsabilidades:**
- Interface de usuário
- Processamento de dados
- Visualizações
- Integração de componentes

**Classes principais:**
- `AdsDataProcessor`: Processa arquivos de ads
- `IntegratedDashboard`: Cria visualizações
- `FunnelSummary`: Métricas de funil

#### `public_sheets_connector.py`
**Descrição:** Conector para dados de vendas  
**Linhas de código:** ~400  
**Responsabilidades:**
- Download do Google Sheets
- Parse de dados de vendas
- Limpeza e transformação
- Matching de shows

**Classe principal:**
- `PublicSheetsConnector`: Gerencia conexão e dados

#### `requirements.txt`
**Descrição:** Dependências do projeto  
**Pacotes principais:**
- streamlit (Interface)
- pandas (Manipulação de dados)
- plotly (Visualizações)
- requests (HTTP)
- openpyxl (Excel)

### Documentação

#### `README.md`
- Overview do projeto
- Melhorias da v2
- Instruções de uso
- Estrutura de dados

#### `QUICKSTART.md`
- Instalação em 5 minutos
- Primeiro uso
- Dicas rápidas
- Troubleshooting básico

#### `EXAMPLES.md`
- 10+ casos de uso reais
- Análises passo a passo
- Métricas e interpretação
- Dicas de especialista

#### `TROUBLESHOOTING.md`
- Problemas comuns
- Soluções detalhadas
- Ferramentas de diagnóstico
- Checklist de verificação

#### `DEPLOYMENT.md`
- Streamlit Cloud
- Docker
- Heroku
- VPS
- CI/CD
- Segurança

#### `CHANGELOG.md`
- Histórico de versões
- Mudanças detalhadas
- Roadmap futuro

### Ferramentas

#### `validate_csv.py`
**Uso:** `python validate_csv.py arquivo.csv`  
**Propósito:** Validar estrutura de CSV antes do upload  
**Output:**
- Tipo de dataset identificado
- Colunas presentes vs esperadas
- Colunas faltantes
- Relatório detalhado

#### `test_installation.py`
**Uso:** `python test_installation.py`  
**Propósito:** Verificar instalação e dependências  
**Testes:**
- Versão do Python
- Pacotes instalados
- Funcionalidade básica
- Estrutura de arquivos

### Configuração

#### `.streamlit/config.toml`
Configurações do Streamlit:
- Theme (cores, fontes)
- Server (porta, CORS)
- Browser (configurações)
- Client (detalhes de erro)

#### `.streamlit/secrets.toml.example`
Template para secrets:
- URL do Google Sheets
- API keys
- Configurações de banco

#### `.gitignore`
Arquivos ignorados:
- Cache Python
- Ambientes virtuais
- Arquivos de dados
- Secrets
- Logs

## 🔄 Fluxo de Dados

```
┌─────────────────┐
│  Meta Ads       │
│  Manager        │
└────────┬────────┘
         │ Export
         ▼
┌─────────────────┐
│  CSV Files      │
│  - Days         │
│  - Placement    │
│  - Time         │
└────────┬────────┘
         │ Upload
         ▼
┌─────────────────┐
│ AdsData         │
│ Processor       │
│  - Normalize    │
│  - Validate     │
│  - Calculate    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐
│ Integrated      │◄────┤ Google       │
│ Dashboard       │     │ Sheets       │
│  - Sales        │     │ (Vendas)     │
│  - Ads          │     └──────────────┘
│  - Integration  │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Visualizations │
│  - Metrics      │
│  - Charts       │
│  - Tables       │
└─────────────────┘
```

## 📊 Estrutura de Dados

### CSV Input Files

#### Days.csv (18 colunas)
```
Reporting starts, Reporting ends, Campaign name,
Campaign delivery, Ad set budget, Ad set budget type,
Amount spent (USD), Attribution setting,
CPM (cost per 1,000 impressions) (USD),
Impressions, Frequency, Reach, CTR (Link),
Link clicks, Results, Result indicator,
Cost per results, Ends
```

#### Days + Placement + Device.csv (22 colunas)
```
[All Days columns] +
Platform, Placement, Device platform,
Impression device
```

#### Days + Time.csv (19 colunas)
```
[All Days columns] +
Time of day (viewer's time zone)
```

### Processed Data Structure

```python
{
    'date': datetime,
    'campaign_name': str,
    'spend': float,
    'impressions': int,
    'clicks': int,
    'ctr': float,
    'cpc': float,
    'cpm': float,
    'results': int,
    'lp_views': int,
    'add_to_cart': int,
    'purchases': int,
    'matched_show_id': str,
    'source_file': str
}
```

## 🧮 Cálculos Principais

### KPIs Calculados

```python
# Click-Through Rate
CTR = (Clicks / Impressions) × 100

# Cost Per Click
CPC = Spend / Clicks

# Cost Per Mille (1000 impressions)
CPM = (Spend / Impressions) × 1000

# Cost Per Result
CPR = Spend / Results

# Return on Ad Spend
ROAS = Revenue / Spend

# Ticket Cost
Ticket_Cost = Total_Spend / Total_Tickets_Sold
```

### Métricas de Funil

```python
Funnel_Conversion = {
    'impressions_to_clicks': Clicks / Impressions,
    'clicks_to_lp': LP_Views / Clicks,
    'lp_to_cart': Add_to_Cart / LP_Views,
    'cart_to_purchase': Purchases / Add_to_Cart
}
```

## 🔐 Segurança

### Dados Sensíveis Protegidos
- ✅ Secrets não commitados
- ✅ .gitignore configurado
- ✅ CSV data ignorado
- ✅ Logs protegidos

### Boas Práticas
- Use `.env` para desenvolvimento
- Use secrets do Streamlit em produção
- Nunca commite `secrets.toml`
- Sempre valide inputs

## 📈 Performance

### Otimizações Implementadas
- Cache de dados do Google Sheets
- Processamento em lote
- Conversões de tipo otimizadas
- Lazy loading de visualizações

### Métricas
- Tempo de load: ~2-5s
- Processamento de CSV: ~1-3s por arquivo
- Renderização: ~500ms por gráfico

## 🧪 Testes

### Cobertura
- Instalação de dependências
- Funcionalidade básica
- Estrutura de arquivos
- Validação de CSV

### Executar Testes
```bash
python test_installation.py
python validate_csv.py arquivo.csv
```

## 🚀 Deployment

### Opções Suportadas
1. **Streamlit Cloud** (Recomendado)
   - Gratuito
   - Deploy automático
   - SSL incluído

2. **Docker**
   - Portável
   - Isolado
   - Escalável

3. **Heroku**
   - Fácil
   - Integração Git
   - Add-ons disponíveis

4. **VPS**
   - Controle total
   - Customizável
   - Self-hosted

## 📞 Suporte

### Obter Ajuda
1. Consulte a documentação
2. Execute ferramentas de diagnóstico
3. Verifique issues no GitHub
4. Abra nova issue se necessário

### Recursos
- 📧 Email: contato via GitHub
- 🐙 GitHub: [avnergomes/ads_analyzer](https://github.com/avnergomes/ads_analyzer)
- 📚 Docs: Pasta `v2/` do repositório

## 🙏 Créditos

**Desenvolvido por:** Avner Gomes  
**Para:** Flai Data  
**Tecnologias:** Streamlit, Pandas, Plotly  
**Licença:** MIT  
**Ano:** 2025

---

## 📝 Notas de Versão

**Versão atual:** 2.0.0  
**Data de lançamento:** 30 de Setembro de 2025  
**Última atualização:** 30 de Setembro de 2025

### Compatibilidade
- Python: 3.8+
- Streamlit: 1.28+
- Pandas: 2.0+
- Meta Ads: 2024-2025 exports

### Próxima Versão Planejada
**v2.1.0** - Novembro 2025
- Export PDF
- Alertas automáticos
- Google Analytics
- Multi-idioma

---

**Este é um projeto open source mantido ativamente.**  
**Contribuições são bem-vindas!** 🎉
