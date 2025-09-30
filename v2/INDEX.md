# 📚 Índice da Documentação - Ads Analyzer v2.0

Bem-vindo à documentação completa do Ads Analyzer v2.0! Este índice ajuda você a encontrar rapidamente a informação que precisa.

## 🚀 Começando

### Para Novos Usuários
1. **[QUICKSTART.md](QUICKSTART.md)** ⚡ - Comece em 5 minutos
   - Instalação rápida
   - Primeiro uso
   - Dicas essenciais

2. **[README.md](README.md)** 📖 - Visão geral completa
   - O que há de novo na v2
   - Funcionalidades principais
   - Suporte aos arquivos CSV

### Para Desenvolvedores
1. **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** 📁 - Estrutura do projeto
   - Organização de arquivos
   - Fluxo de dados
   - Arquitetura

2. **[CHANGELOG.md](CHANGELOG.md)** 📝 - Histórico de mudanças
   - O que mudou na v2
   - Novas funcionalidades
   - Roadmap futuro

---

## 📖 Guias de Uso

### Uso Básico
- **[QUICKSTART.md](QUICKSTART.md)** - Começando rapidamente
  - Instalação
  - Primeiro upload
  - Navegação básica

### Casos de Uso Avançados
- **[EXAMPLES.md](EXAMPLES.md)** 📊 - Exemplos práticos
  - 10+ casos de uso reais
  - Análises passo a passo
  - Interpretação de métricas
  - Dicas de especialista
  - A/B testing
  - Otimização de budget

### Conteúdo do EXAMPLES.md
1. Análise de Performance de Campanha
2. Otimização de Budget por Show
3. Análise de ROI/ROAS
4. Identificação de Canais Eficientes
5. Otimização por Horário
6. Comparação de Cidades
7. Análise de Funil
8. Previsão de Vendas
9. A/B Testing de Campanhas
10. Dashboard Executivo

---

## 🔧 Solução de Problemas

### Troubleshooting
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** 🐛 - Guia completo
  - Problemas comuns e soluções
  - Ferramentas de diagnóstico
  - Checklist de verificação
  - Estrutura esperada dos arquivos

### Problemas Cobertos
1. Arquivo não é reconhecido
2. Dados faltando após upload
3. Erro ao fazer upload
4. Métricas calculadas incorretas
5. Show não é identificado
6. Erros de memória
7. Gráficos não aparecem
8. Datas incorretas

---

## 🚀 Deployment

### Guia de Deployment
- **[DEPLOYMENT.md](DEPLOYMENT.md)** 🌐 - Deploy em produção
  - Streamlit Cloud (Recomendado)
  - Docker
  - Heroku
  - VPS (DigitalOcean, AWS)
  - CI/CD
  - Segurança

### Plataformas Cobertas
- ✅ Streamlit Cloud (Gratuito)
- ✅ Docker (Containers)
- ✅ Heroku (PaaS)
- ✅ VPS (Self-hosted)
- ✅ GitHub Actions (CI/CD)

---

## 🔍 Referência Técnica

### Arquitetura
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Estrutura completa
  - Organização de arquivos
  - Fluxo de dados
  - Cálculos principais
  - Performance
  - Segurança

### Código
- **[app.py](app.py)** - Aplicação principal
  - `AdsDataProcessor` - Processamento de dados
  - `IntegratedDashboard` - Visualizações
  - `FunnelSummary` - Métricas de funil

- **[public_sheets_connector.py](public_sheets_connector.py)** - Conector
  - `PublicSheetsConnector` - Dados de vendas

### Ferramentas
- **[validate_csv.py](validate_csv.py)** - Validador de CSV
  ```bash
  python validate_csv.py arquivo.csv
  ```

- **[test_installation.py](test_installation.py)** - Teste de instalação
  ```bash
  python test_installation.py
  ```

---

## 📊 Dados e Formatos

### Estrutura de Dados
Consulte **[README.md](README.md)** - Seção "Suporte Completo aos Arquivos"

**Days.csv** (18 colunas):
- Reporting starts/ends
- Campaign info
- Spend, Impressions, Clicks
- Results, KPIs

**Days + Placement + Device.csv** (22 colunas):
- Todas do Days +
- Platform, Placement
- Device platform

**Days + Time.csv** (19 colunas):
- Todas do Days +
- Time of day

### Validação
Antes de fazer upload, valide seus arquivos:
```bash
python validate_csv.py Days.csv "Days Placement.csv" "Days Time.csv"
```

---

## 🎓 Aprendizado

### Para Iniciantes
1. Leia **[QUICKSTART.md](QUICKSTART.md)**
2. Siga o primeiro exemplo em **[EXAMPLES.md](EXAMPLES.md)**
3. Consulte **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** se necessário

### Para Usuários Intermediários
1. Explore todos os casos de uso em **[EXAMPLES.md](EXAMPLES.md)**
2. Entenda a estrutura em **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)**
3. Otimize seguindo as dicas de especialista

### Para Desenvolvedores
1. Estude **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)**
2. Leia o código em `app.py` e `public_sheets_connector.py`
3. Execute os testes com `test_installation.py`
4. Contribua seguindo **[CHANGELOG.md](CHANGELOG.md)**

---

## 🔄 Fluxo de Trabalho Recomendado

### Setup Inicial
```bash
# 1. Clone o repositório
git clone https://github.com/avnergomes/ads_analyzer.git
cd ads_analyzer/v2

# 2. Instale dependências
pip install -r requirements.txt

# 3. Teste a instalação
python test_installation.py

# 4. Execute a aplicação
streamlit run app.py
```

### Uso Diário
1. Exporte dados do Meta Ads Manager
2. Valide os CSVs: `python validate_csv.py arquivo.csv`
3. Faça upload na aplicação
4. Analise os resultados
5. Tome decisões baseadas em dados

### Troubleshooting
1. Consulte **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**
2. Execute `test_installation.py`
3. Valide CSVs com `validate_csv.py`
4. Verifique logs do Streamlit
5. Abra issue no GitHub se necessário

---

## 📞 Suporte e Comunidade

### Obter Ajuda

**Documentação:**
- Comece com [QUICKSTART.md](QUICKSTART.md)
- Problemas? [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Casos de uso: [EXAMPLES.md](EXAMPLES.md)

**Ferramentas de Diagnóstico:**
```bash
# Teste sua instalação
python test_installation.py

# Valide seus arquivos
python validate_csv.py arquivo.csv
```

**Comunidade:**
- 🐙 GitHub Issues: Reporte bugs
- 💬 Discussions: Perguntas e ideias
- 📧 Email: Via GitHub profile

### Contribuir
Quer contribuir? Veja **[CHANGELOG.md](CHANGELOG.md)** para o roadmap.

---

## 📝 Checklist de Leitura

### Essencial (Leia primeiro)
- [ ] [QUICKSTART.md](QUICKSTART.md) - Começar
- [ ] [README.md](README.md) - Visão geral
- [ ] [EXAMPLES.md](EXAMPLES.md) - Pelo menos 3 exemplos

### Recomendado
- [ ] [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Quando tiver problemas
- [ ] [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Entender a arquitetura
- [ ] [CHANGELOG.md](CHANGELOG.md) - O que mudou

### Avançado
- [ ] [DEPLOYMENT.md](DEPLOYMENT.md) - Deploy em produção
- [ ] Código fonte: `app.py`
- [ ] Código fonte: `public_sheets_connector.py`

---

## 🎯 Mapa Mental da Documentação

```
Ads Analyzer v2.0
├── 🚀 Começando
│   ├── QUICKSTART.md (5 min para começar)
│   └── README.md (Visão completa)
│
├── 📖 Guias
│   ├── EXAMPLES.md (10+ casos de uso)
│   ├── TROUBLESHOOTING.md (Solução de problemas)
│   └── DEPLOYMENT.md (Deploy em produção)
│
├── 🔧 Referência
│   ├── PROJECT_STRUCTURE.md (Arquitetura)
│   ├── CHANGELOG.md (Histórico)
│   └── Código fonte (app.py, etc)
│
└── 🛠️ Ferramentas
    ├── validate_csv.py (Validar CSVs)
    ├── test_installation.py (Testar setup)
    └── .streamlit/ (Configurações)
```

---

## 🔍 Busca Rápida

### "Como faço para..."

**...começar rapidamente?**
→ [QUICKSTART.md](QUICKSTART.md)

**...resolver um erro?**
→ [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**...otimizar minhas campanhas?**
→ [EXAMPLES.md](EXAMPLES.md) - Casos 1, 2, 3

**...fazer deploy?**
→ [DEPLOYMENT.md](DEPLOYMENT.md)

**...entender a arquitetura?**
→ [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

**...ver o que mudou?**
→ [CHANGELOG.md](CHANGELOG.md)

**...validar meus CSVs?**
→ Use `python validate_csv.py`

**...testar a instalação?**
→ Use `python test_installation.py`

---

## 📊 Estatísticas da Documentação

- **Total de arquivos:** 13
- **Total de linhas:** ~5,000
- **Documentos principais:** 7
- **Ferramentas:** 2
- **Exemplos de uso:** 10+
- **Problemas cobertos:** 15+
- **Plataformas de deploy:** 5

---

## 🎓 Níveis de Conhecimento

### Iniciante (0-1 semana)
Foque em:
- QUICKSTART.md
- README.md
- EXAMPLES.md (primeiros 3)

### Intermediário (1-4 semanas)
Adicione:
- TROUBLESHOOTING.md
- PROJECT_STRUCTURE.md
- Todos os EXAMPLES.md

### Avançado (1+ mês)
Domine:
- DEPLOYMENT.md
- Código fonte
- Contribuições ao projeto

---

## 🔄 Atualizações

Esta documentação é atualizada regularmente.

**Última atualização:** 30 de Setembro de 2025  
**Versão da documentação:** 2.0.0  
**Versão do software:** 2.0.0

### Verificar Atualizações
```bash
git pull origin main
cd v2
```

---

## 💡 Dica Final

**Comece simples:**
1. Leia o [QUICKSTART.md](QUICKSTART.md)
2. Faça o primeiro upload
3. Explore a interface
4. Consulte [EXAMPLES.md](EXAMPLES.md) quando precisar

**Aprenda fazendo:**
- Teste com dados reais
- Experimente diferentes análises
- Consulte a documentação quando necessário

**Compartilhe conhecimento:**
- Ajude outros usuários
- Reporte problemas
- Sugira melhorias

---

## 📚 Leitura Recomendada

### Ordem de Leitura Sugerida

1. **Dia 1:** [QUICKSTART.md](QUICKSTART.md) + primeiro upload
2. **Dia 2-3:** [README.md](README.md) completo
3. **Semana 1:** [EXAMPLES.md](EXAMPLES.md) - todos os casos
4. **Semana 2:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
5. **Mês 1:** [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
6. **Quando necessário:** [DEPLOYMENT.md](DEPLOYMENT.md)

---

**Bem-vindo ao Ads Analyzer v2.0!** 🎉

*Esta é uma ferramenta poderosa para análise de performance de ads e vendas.*  
*Use a documentação como sua aliada no processo de aprendizado.*

**Boas análises!** 📊

---

**Desenvolvido por:** Avner Gomes  
**Para:** Flai Data  
**Versão:** 2.0  
**Licença:** MIT
