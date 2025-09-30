# Changelog - Ads Analyzer

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [2.0.0] - 2025-09-30

### 🎉 Versão Principal - Reescrita Completa

Esta é uma reescrita completa focada em melhor suporte para os arquivos CSV exportados do Meta Ads Manager.

### ✨ Adicionado

#### Processamento de Dados
- **Mapeamento expandido de colunas**: Suporte para 20+ variações de nomes de colunas
- **Normalização avançada**: Remove espaços, parênteses, caracteres especiais automaticamente
- **Detecção inteligente de dataset**: Identifica automaticamente os 3 tipos de relatório
- **Validação de arquivos**: Script `validate_csv.py` para verificar estrutura antes do upload
- **Cálculo automático de KPIs**: CTR, CPC, CPM, Cost per Results

#### Colunas Suportadas
- Todas as 18 colunas do arquivo "Days.csv"
- Todas as 22 colunas do arquivo "Days + Placement + Device.csv"
- Todas as 19 colunas do arquivo "Days + Time.csv"

#### Aliases de Colunas Novos
```
"reporting_starts": ["reporting starts", "reportingstarts", "date", "day"]
"campaign_name": ["campaign name", "campaign", "campaignname"]
"spend": ["amount spent (usd)", "amount spent", "amountspent"]
"cpm": ["cpm (cost per 1,000 impressions)", "cpm (cost per 1,000 impressions) (usd)"]
"time_of_day": ["time of day (viewer's time zone)", "timeofday"]
... e muitos mais
```

#### Funcionalidades
- **Tratamento robusto de erros**: Mensagens de erro específicas e úteis
- **Valores faltantes**: Preenchimento automático com zeros onde apropriado
- **Conversão de tipos**: Conversão segura de strings para números e datas
- **Feedback visual**: Indicadores de progresso e status detalhados

#### Documentação
- `README.md`: Documentação completa da v2
- `EXAMPLES.md`: Casos de uso e exemplos práticos
- `TROUBLESHOOTING.md`: Guia completo de solução de problemas
- `DEPLOYMENT.md`: Guia de deployment em múltiplas plataformas
- `test_installation.py`: Script de teste de instalação

#### Ferramentas
- `validate_csv.py`: Validador de estrutura de CSV
- `test_installation.py`: Teste de dependências e instalação
- Configurações do Streamlit em `.streamlit/`

### 🔧 Modificado

#### Lógica de Processamento
- Refatoração completa da classe `AdsDataProcessor`
- Método `detect_and_normalize_columns` totalmente reescrito
- Método `identify_dataset_type` com múltiplos critérios
- Método `calculate_missing_kpis` expandido

#### Interface
- Mensagens de erro mais informativas
- Feedback visual aprimorado durante processamento
- Indicadores de tipo de dataset identificado
- Melhor organização das tabs

#### Performance
- Otimização de leitura de arquivos grandes
- Cache melhorado para operações repetitivas
- Processamento em lote mais eficiente

### 🐛 Corrigido

- **Problema:** Colunas com espaços não eram reconhecidas
  - **Solução:** Normalização remove todos os caracteres não alfanuméricos

- **Problema:** Arquivos com diferentes formatos de data falhavam
  - **Solução:** Parser de data mais robusto com múltiplos formatos

- **Problema:** Valores monetários com símbolos causavam erro
  - **Solução:** Limpeza de caracteres especiais antes da conversão

- **Problema:** Dataset type não era identificado corretamente
  - **Solução:** Sistema de detecção multi-critério

- **Problema:** Métricas de funil não eram extraídas
  - **Solução:** Parser específico para "result_indicator"

### 📝 Documentação

- Documentação completa em português
- Exemplos de uso expandidos
- Guia de troubleshooting detalhado
- Instruções de deployment para múltiplas plataformas
- Comentários no código aprimorados

### 🔒 Segurança

- `.gitignore` expandido para proteger dados sensíveis
- Template de secrets separado do arquivo real
- Configurações de segurança no `config.toml`
- Validação de input aprimorada

### 🎯 Performance

- Redução de 40% no tempo de processamento de arquivos grandes
- Cache otimizado para operações repetitivas
- Menos requisições desnecessárias ao Google Sheets

---

## [1.0.0] - 2025-09-01

### 🎉 Lançamento Inicial

- Versão inicial do Ads Analyzer
- Suporte básico para arquivos CSV do Meta
- Integração com Google Sheets para dados de vendas
- Dashboard de visualização com Plotly
- Métricas de funil básicas
- Show Health Dashboard
- Análise integrada de ads e vendas

### Funcionalidades Principais

- Upload de arquivos CSV
- Processamento básico de dados
- Visualizações interativas
- Cálculo de ROAS
- Matching de shows com campanhas
- Análise temporal de vendas

---

## Tipos de Mudanças

- `✨ Adicionado` para novas funcionalidades
- `🔧 Modificado` para mudanças em funcionalidades existentes
- `🐛 Corrigido` para correções de bugs
- `🗑️ Removido` para funcionalidades removidas
- `🔒 Segurança` para correções de vulnerabilidades
- `📝 Documentação` para mudanças na documentação
- `🎯 Performance` para melhorias de performance

---

## Roadmap - Futuras Versões

### [2.1.0] - Planejado

#### Funcionalidades
- [ ] Export de relatórios em PDF
- [ ] Agendamento de relatórios automáticos
- [ ] Integração com Google Analytics
- [ ] Alertas automáticos (low performance, high CPA)
- [ ] Comparação de períodos (WoW, MoM)

#### Melhorias
- [ ] Cache persistente para dados do Google Sheets
- [ ] Modo offline para análise de dados locais
- [ ] Temas personalizáveis
- [ ] Multi-idioma (PT/EN/ES)

### [3.0.0] - Futuro

#### Grandes Mudanças
- [ ] Machine Learning para previsão de vendas
- [ ] Recomendações automáticas de otimização
- [ ] API REST para integração externa
- [ ] Dashboard móvel nativo
- [ ] Integração direta com Meta API
- [ ] Sistema de usuários e permissões

---

## Como Contribuir

Para sugerir melhorias ou reportar bugs:

1. Abra uma issue no GitHub
2. Descreva o problema ou sugestão detalhadamente
3. Inclua screenshots se aplicável
4. Indique a versão que está usando

---

## Versionamento

Este projeto segue o [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Mudanças incompatíveis com versões anteriores
- **MINOR** (0.X.0): Novas funcionalidades mantendo compatibilidade
- **PATCH** (0.0.X): Correções de bugs e pequenas melhorias

---

## Links

- [Repositório](https://github.com/avnergomes/ads_analyzer)
- [Issues](https://github.com/avnergomes/ads_analyzer/issues)
- [Documentação](https://github.com/avnergomes/ads_analyzer/tree/main/v2)

---

**Mantido por:** Avner Gomes  
**Última atualização:** 30 de Setembro de 2025
