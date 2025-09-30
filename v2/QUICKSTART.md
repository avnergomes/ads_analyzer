# ⚡ Quick Start - Ads Analyzer v2.0

Comece a usar o Ads Analyzer em menos de 5 minutos!

## 📦 Instalação Rápida

### 1. Clone o Repositório

```bash
git clone https://github.com/avnergomes/ads_analyzer.git
cd ads_analyzer/v2
```

### 2. Crie um Ambiente Virtual (Recomendado)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 4. Teste a Instalação

```bash
python test_installation.py
```

Se todos os testes passarem ✅, você está pronto!

### 5. Execute a Aplicação

```bash
streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`

---

## 🎯 Primeiro Uso

### Passo 1: Exporte os Dados do Meta

No Meta Ads Manager:

1. Selecione suas campanhas
2. Clique em "Export" → "Customize Columns"
3. Exporte 3 relatórios separados:
   - **Days** (breakdown por dia)
   - **Days + Placement + Device** (com placement e device)
   - **Days + Time** (com time of day)

### Passo 2: Upload dos Arquivos

1. Na barra lateral, clique em "Upload Meta ad exports"
2. Selecione os 3 arquivos CSV
3. Aguarde o processamento

### Passo 3: Explore os Dados

**Tab "Ticket Sales":**
- Visão geral de vendas
- Show Health Dashboard
- Gráficos de performance

**Tab "Advertising":**
- Métricas de ads
- Performance por campanha
- Evolução temporal

**Tab "Integrated View":**
- Correlação ads ↔ vendas
- Análise de ROI/ROAS
- Eficiência geral

**Tab "Raw Data":**
- Dados brutos
- Downloads disponíveis

---

## 🔧 Validação de Arquivos

Antes de fazer upload, valide seus CSVs:

```bash
python validate_csv.py Days.csv "Days Placement Device.csv" "Days Time.csv"
```

Isso verifica:
- ✅ Estrutura correta
- ✅ Colunas necessárias
- ✅ Tipo de dataset identificado

---

## 💡 Dicas Rápidas

### Nomes de Campanha
Use o padrão de show ID nas campanhas:
```
WDC_0927        # Washington DC, 27 de Setembro
WDC_0927_S2     # Show 2 em Washington DC
NYC_1015        # New York, 15 de Outubro
```

### Budget por Show
No Show Health Dashboard, insira o budget total do show para calcular:
- Ticket Cost
- ROAS atual
- ROAS potencial

### Download de Dados
Em qualquer tab, você pode:
- Visualizar dados brutos
- Download em CSV
- Usar em outras ferramentas

---

## 🚨 Problemas Comuns

### "File type not recognized"
- Verifique se o arquivo foi exportado do Meta
- Não edite manualmente as colunas
- Use o validador: `python validate_csv.py arquivo.csv`

### "Missing required columns"
- Certifique-se de exportar todas as colunas padrão
- Não remova ou renomeie colunas

### Aplicação não abre
```bash
# Verifique se Streamlit está instalado
pip list | grep streamlit

# Se não estiver, instale
pip install streamlit

# Execute novamente
streamlit run app.py
```

---

## 📚 Próximos Passos

- 📖 Leia o [README.md](README.md) completo
- 🔍 Veja [EXAMPLES.md](EXAMPLES.md) para casos de uso
- 🐛 Consulte [TROUBLESHOOTING.md](TROUBLESHOOTING.md) se tiver problemas
- 🚀 Faça deploy seguindo [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🆘 Precisa de Ajuda?

1. Execute o teste de instalação: `python test_installation.py`
2. Valide seus arquivos: `python validate_csv.py arquivo.csv`
3. Consulte a documentação completa
4. Abra uma issue no GitHub

---

## ✨ Recursos Úteis

### Atalhos do Streamlit
- `R`: Recarregar aplicação
- `Ctrl/Cmd + Shift + R`: Limpar cache
- `Ctrl/Cmd + K`: Abrir menu de comandos

### Links Importantes
- [Repositório GitHub](https://github.com/avnergomes/ads_analyzer)
- [Documentação Streamlit](https://docs.streamlit.io)
- [Meta Ads Manager](https://business.facebook.com/adsmanager)

---

## 🎉 Está Funcionando!

Se você chegou até aqui e tudo está rodando, parabéns! 🎊

Agora você pode:
- ✅ Analisar performance de campanhas
- ✅ Otimizar budget por show
- ✅ Calcular ROI/ROAS
- ✅ Identificar oportunidades
- ✅ Tomar decisões data-driven

**Bom trabalho e boas análises!** 📊

---

**Desenvolvido por:** Avner Gomes para Flai Data  
**Versão:** 2.0  
**Última atualização:** Setembro 2025
