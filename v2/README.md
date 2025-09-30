# Ads Analyzer v2.0

## 🎯 O que há de novo na versão 2.0?

Esta versão foi completamente aprimorada para processar os arquivos CSV exportados do Meta Ads Manager com maior precisão e confiabilidade.

### 📊 Melhorias Principais

#### 1. **Mapeamento de Colunas Aprimorado**
- Suporte expandido para variações de nomes de colunas
- Normalização inteligente que remove espaços, parênteses e caracteres especiais
- Compatível com exports em diferentes idiomas e formatos

#### 2. **Detecção Automática de Tipo de Dataset**
- Identifica automaticamente os três tipos de relatório:
  - **Days**: Relatório básico por dia
  - **Days + Placement + Device**: Com dados de placement e dispositivo
  - **Days + Time**: Com dados de horário do dia

#### 3. **Processamento Robusto de Dados**
- Conversão automática de tipos de dados
- Cálculo de KPIs faltantes (CTR, CPC, CPM)
- Tratamento de valores nulos e inconsistências
- Normalização de métricas de funil

#### 4. **Suporte Completo aos Arquivos Fornecidos**

**Days.csv** (18 colunas):
- Reporting starts/ends
- Campaign name, delivery, budget
- Amount spent, Attribution setting
- CPM, Impressions, Frequency, Reach
- CTR, Link clicks, Results
- Result indicator, Cost per results, Ends

**Days + Placement + Device.csv** (22 colunas):
- Todas as colunas do Days
- Platform, Placement
- Device platform, Impression device

**Days + Time.csv** (19 colunas):
- Todas as colunas do Days
- Time of day (viewer's time zone)

### 🔧 Melhorias Técnicas

#### Aliases de Colunas Expandidos
```python
"campaign_name": [
    "campaign_name", 
    "campaign name", 
    "campaign", 
    "campaign id",
    "campaignname",
],
"spend": [
    "spend",
    "amount_spent",
    "amount spent",
    "amount spent (usd)",
    "amountspent",
    "amountspent(usd)",
],
# E muitos mais...
```

#### Identificação Inteligente de Dataset
- Verifica a presença de colunas específicas
- Prioriza identificação por características únicas
- Suporte para variações de nomenclatura

#### Cálculo Automático de Métricas
- CTR = (Clicks / Impressions) × 100
- CPC = Spend / Clicks
- CPM = (Spend / Impressions) × 1000
- Cost per Results = Spend / Results

### 📁 Estrutura do Projeto

```
v2/
├── app.py                      # Aplicação principal aprimorada
├── public_sheets_connector.py  # Conector do Google Sheets
├── requirements.txt            # Dependências atualizadas
└── README.md                   # Este arquivo
```

### 🚀 Como Usar

1. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

2. **Executar a aplicação:**
```bash
streamlit run app.py
```

3. **Upload dos arquivos:**
   - Faça upload dos três arquivos CSV na barra lateral
   - Os arquivos serão automaticamente identificados e processados
   - Visualize os resultados nas diferentes abas

### 📥 Formatos de Arquivo Suportados

- CSV (`.csv`)
- Excel (`.xlsx`, `.xls`)

### 🎨 Funcionalidades

#### Tab: Ticket Sales
- Overview geral de vendas
- Show Health Dashboard com métricas por show
- Gráficos de performance

#### Tab: Advertising
- Overview de métricas de ads
- Análise de performance por campanha
- Evolução temporal

#### Tab: Integrated View
- Correlação entre gastos e vendas
- Análise integrada de performance
- Métricas de ROI e ROAS

#### Tab: Raw Data
- Visualização dos dados brutos
- Download de CSVs processados
- Exploração de dados

### 🔍 Detalhes de Processamento

#### Normalização de Colunas
```python
# Exemplo de normalização
"Amount spent (USD)" → "spend"
"CPM (cost per 1,000 impressions)" → "cpm"
"Time of day (viewer's time zone)" → "time_of_day"
```

#### Métricas de Funil
- Landing Page Views (LP Views)
- Add to Cart
- Purchases/Conversions

### 🐛 Tratamento de Erros

- Arquivos não reconhecidos são listados com avisos
- Colunas faltantes são criadas com valores zero
- Tipos de dados são convertidos de forma segura
- Erros são registrados e reportados ao usuário

### 💡 Dicas

1. **Nomes de Arquivo**: Não importa o nome do arquivo, o sistema identifica pelo conteúdo
2. **Ordem de Upload**: A ordem dos arquivos não importa
3. **Dados Faltantes**: O sistema preenche valores faltantes automaticamente
4. **Múltiplas Tentativas**: Você pode fazer upload novamente a qualquer momento

### 📝 Logs e Debug

O sistema registra informações importantes:
- Tipos de dataset identificados
- Colunas mapeadas
- Erros de processamento
- Estatísticas de dados

### 🎯 Compatibilidade

Testado com:
- Python 3.8+
- Streamlit 1.28+
- Pandas 2.0+
- Exports do Meta Ads Manager (2024-2025)

### 📞 Suporte

Para problemas ou dúvidas:
1. Verifique os logs no console
2. Confirme que os arquivos são exports válidos do Meta
3. Verifique se todas as dependências estão instaladas

### 🔄 Diferenças da v1

| Aspecto | v1 | v2 |
|---------|----|----|
| Aliases de colunas | ~10 por coluna | 20+ por coluna |
| Normalização | Básica | Avançada com regex |
| Detecção de dataset | Simples | Multi-critério |
| Tratamento de erros | Básico | Robusto com fallbacks |
| KPIs calculados | 3 | 5+ |
| Mensagens de erro | Genéricas | Específicas e úteis |

### 🚀 Melhorias Futuras

- [ ] Suporte para mais formatos de export
- [ ] Análise preditiva de performance
- [ ] Recomendações automáticas
- [ ] Export de relatórios em PDF
- [ ] API para integração

---

**Desenvolvido por Avner Gomes para Flai Data**

*Versão 2.0 - Setembro 2025*
