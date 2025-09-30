# Ads Analyzer v2.0 - Guia de Troubleshooting

## 🔍 Problemas Comuns e Soluções

### 1. Arquivo não é reconhecido

**Sintoma:** O sistema não identifica o tipo do arquivo CSV enviado.

**Possíveis causas:**
- Arquivo não é um export válido do Meta Ads Manager
- Colunas foram modificadas ou renomeadas manualmente
- Arquivo está corrompido ou incompleto

**Soluções:**
1. Verifique se o arquivo foi exportado diretamente do Meta Ads Manager
2. Não modifique os nomes das colunas após o export
3. Execute o validador: `python validate_csv.py seu_arquivo.csv`
4. Compare com os arquivos de exemplo fornecidos

### 2. Dados faltando após o upload

**Sintoma:** Algumas métricas aparecem como zero ou vazias.

**Possíveis causas:**
- Colunas não estão no formato esperado
- Valores nulos no arquivo original
- Tipo de dados incompatível

**Soluções:**
1. Verifique se todas as colunas necessárias estão presentes
2. Confira se os valores numéricos não contêm caracteres especiais
3. Use o formato de data correto (YYYY-MM-DD)
4. Remova linhas totalmente vazias do CSV

### 3. Erro ao fazer upload do arquivo

**Sintoma:** Mensagem de erro ao tentar enviar o arquivo.

**Possíveis causas:**
- Arquivo muito grande
- Formato incompatível
- Encoding incorreto

**Soluções:**
1. Verifique o tamanho do arquivo (máximo recomendado: 100MB)
2. Use apenas arquivos .csv, .xlsx ou .xls
3. Salve o CSV com encoding UTF-8
4. Divida arquivos muito grandes em períodos menores

### 4. Métricas calculadas incorretas

**Sintoma:** CTR, CPC ou CPM parecem incorretos.

**Possíveis causas:**
- Divisão por zero
- Valores faltantes nas colunas base
- Unidades monetárias diferentes

**Soluções:**
1. Verifique se as colunas spend, impressions e clicks têm valores
2. Confirme que o spend está em USD
3. Revise os cálculos:
   - CTR = (clicks / impressions) × 100
   - CPC = spend / clicks
   - CPM = (spend / impressions) × 1000

### 5. Show não é identificado nas ads

**Sintoma:** A coluna "matched_show_id" aparece vazia.

**Possíveis causas:**
- Nome da campanha não segue o padrão
- Cidade não corresponde aos dados de vendas
- Show ID não está no nome da campanha

**Soluções:**
1. Use o formato de show ID na campanha: `CITY_MMDD` (ex: WDC_0927)
2. Inclua o nome da cidade na campanha ou ad set
3. Para múltiplos shows, use: `CITY_MMDD_S1`, `CITY_MMDD_S2`, etc.
4. Verifique se a cidade corresponde aos dados do Google Sheets

### 6. Erros de memória com arquivos grandes

**Sintoma:** O aplicativo congela ou fecha ao processar arquivos.

**Possíveis causas:**
- Arquivo muito grande
- Muitas linhas de dados
- Memória insuficiente

**Soluções:**
1. Divida o período de análise em intervalos menores
2. Feche outras abas do navegador
3. Aumente a memória disponível para o Streamlit
4. Use filtros no Meta antes de exportar

### 7. Gráficos não aparecem

**Sintoma:** As visualizações não são exibidas.

**Possíveis causas:**
- Dados insuficientes
- Colunas necessárias faltando
- Erro de JavaScript no navegador

**Soluções:**
1. Limpe o cache do navegador
2. Tente outro navegador (Chrome recomendado)
3. Verifique se há dados suficientes para o gráfico
4. Recarregue a página (F5)

### 8. Datas não aparecem corretamente

**Sintoma:** Datas aparecem como texto ou erradas.

**Possíveis causas:**
- Formato de data não reconhecido
- Timezone incorreto
- Conversão de tipo falhou

**Soluções:**
1. Use o formato ISO: YYYY-MM-DD
2. Evite formatos regionais (DD/MM/YYYY)
3. Não use timestamps, apenas datas
4. Verifique se a coluna é reconhecida como "date"

## 🔧 Ferramentas de Diagnóstico

### Validador de CSV
```bash
python validate_csv.py arquivo.csv
```

Mostra:
- Tipo de arquivo identificado
- Colunas encontradas vs esperadas
- Colunas faltantes
- Número de linhas

### Logs do Sistema
O Streamlit gera logs no terminal. Para ver mais detalhes:
```bash
streamlit run app.py --logger.level=debug
```

### Verificação Manual de Colunas
```python
import pandas as pd

df = pd.read_csv('seu_arquivo.csv')
print("Colunas:", df.columns.tolist())
print("Tipos:", df.dtypes)
print("Primeiras linhas:", df.head())
```

## 📋 Checklist de Verificação

Antes de reportar um problema, verifique:

- [ ] Arquivo é um export direto do Meta Ads Manager
- [ ] Arquivo não foi editado manualmente
- [ ] Todas as 3 types de arquivo foram enviados
- [ ] Arquivos estão em formato CSV ou Excel
- [ ] Encoding é UTF-8
- [ ] Não há linhas completamente vazias
- [ ] Valores numéricos não contêm texto
- [ ] Datas estão no formato correto
- [ ] Arquivo não está corrompido
- [ ] Tamanho do arquivo é razoável (<100MB)

## 🆘 Estrutura Esperada dos Arquivos

### Days.csv (18 colunas)
```
Reporting starts, Reporting ends, Campaign name, Campaign delivery,
Ad set budget, Ad set budget type, Amount spent (USD), Attribution setting,
CPM (cost per 1,000 impressions) (USD), Impressions, Frequency, Reach,
CTR (Link), Link clicks, Results, Result indicator, Cost per results, Ends
```

### Days Placement Device.csv (22 colunas)
```
[Todas as colunas do Days] + Platform, Placement, Device platform, 
Impression device
```

### Days Time.csv (19 colunas)
```
[Todas as colunas do Days] + Time of day (viewer's time zone)
```

## 💡 Dicas de Prevenção

1. **Sempre exporte diretamente do Meta**
   - Não copie/cole em Excel
   - Não edite manualmente
   - Use "Export" > "CSV"

2. **Mantenha os nomes originais**
   - Não traduza colunas
   - Não remova espaços ou parênteses
   - Não reordene colunas

3. **Teste com dados pequenos primeiro**
   - Exporte 1 semana primeiro
   - Verifique se funciona
   - Depois exporte período completo

4. **Use o validador**
   - Execute antes de fazer upload
   - Corrija problemas identificados
   - Confirme que todos os 3 tipos são identificados

## 📞 Suporte Adicional

Se o problema persistir após seguir este guia:

1. Execute o validador e salve o resultado
2. Capture uma screenshot do erro
3. Anote os passos que causaram o problema
4. Verifique se há erros no console do navegador (F12)
5. Entre em contato fornecendo essas informações

## 🔄 Última Atualização

Este guia foi atualizado para a versão 2.0 em Setembro de 2025.
