# 📚 Exemplos de Uso - Ads Analyzer v2.0

Este documento contém exemplos práticos de uso do Ads Analyzer.

## 🎯 Casos de Uso Comuns

### 1. Análise de Performance de Campanha

**Objetivo:** Entender qual campanha está performando melhor.

**Passos:**
1. Faça upload dos três arquivos CSV
2. Vá para a tab "Advertising"
3. Observe o gráfico "Spend vs. Purchases by Campaign"
4. Identifique campanhas com:
   - Alto gasto + Baixas conversões = Precisa otimização
   - Baixo gasto + Altas conversões = Aumentar budget
   - Alto gasto + Altas conversões = Está funcionando bem

**Métricas chave:**
- CPC (Cost Per Click): Quanto você paga por clique
- CPM (Cost Per Mille): Custo por 1000 impressões
- Conversion Rate: Taxa de conversão

---

### 2. Otimização de Budget por Show

**Objetivo:** Distribuir budget de forma eficiente entre shows.

**Passos:**
1. Vá para tab "Ticket Sales"
2. Role até "Show Health Dashboard"
3. Selecione um show
4. Analise:
   - Days to Show: Quantos dias faltam
   - Tickets Remaining: Quantos ingressos restam
   - Daily Sales Target: Meta diária necessária
   - Avg Sales Last 7 Days: Ritmo atual

**Decisões:**
- Se avg sales < target: Aumentar spend
- Se avg sales > target: Pode reduzir spend
- Se dias < 7 e ocupancy < 70%: Aumentar urgentemente

---

### 3. Análise de ROI/ROAS

**Objetivo:** Calcular retorno sobre investimento em ads.

**Passos:**
1. Vá para "Show Health Dashboard"
2. Insira o budget total do show
3. Observe:
   - ROAS (Return on Ad Spend): Receita / Gasto
   - Potential ROAS: Receita potencial máxima
   - Ticket Cost: Custo de aquisição por ingresso

**Interpretação:**
- ROAS > 3.0: Excelente
- ROAS 2.0-3.0: Bom
- ROAS 1.0-2.0: Aceitável
- ROAS < 1.0: Prejuízo

---

### 4. Identificação de Canais Eficientes

**Arquivo necessário:** Days + Placement + Device.csv

**Objetivo:** Descobrir quais placements performam melhor.

**Análise:**
```python
# No arquivo Days + Placement + Device
# Observe as colunas:
- Platform: Facebook, Instagram, Messenger
- Placement: Feed, Stories, Reels
- Device: Mobile, Desktop
```

**Insights comuns:**
- Instagram Stories: Alto engagement, jovens
- Facebook Feed: Maior alcance, audiência ampla
- Mobile: Maior volume, menor CPC
- Desktop: Menor volume, maior conversão

---

### 5. Otimização por Horário

**Arquivo necessário:** Days + Time.csv

**Objetivo:** Descobrir os melhores horários para ads.

**Análise:**
```python
# Coluna: Time of day (viewer's time zone)
# Valores: 00:00-23:59
```

**Padrões comuns:**
- 8h-10h: Comute matinal
- 12h-14h: Almoço
- 18h-21h: Pós-trabalho (melhor)
- 21h-23h: Antes de dormir

**Ação:**
- Concentrar budget nos horários de pico
- Reduzir ou pausar em horários de baixa conversão

---

### 6. Comparação de Cidades

**Objetivo:** Ver quais cidades estão performando melhor.

**Passos:**
1. Tab "Ticket Sales"
2. Gráfico "Top Cities by Tickets Sold"
3. Compare:
   - Total de ingressos vendidos
   - Taxa de ocupação (cor)
   - Receita total

**Decisões:**
- Cidades com baixa ocupação: Aumentar ads
- Cidades com alta ocupação: Manter ou reduzir
- Cidades esgotadas: Considerar shows extras

---

### 7. Análise de Funil

**Objetivo:** Identificar onde as pessoas estão "caindo" no funil.

**Passos:**
1. Vá para "Show Health Dashboard"
2. Selecione um show
3. Observe o gráfico "Funnel snapshot"

**Etapas do funil:**
1. **Impressions**: Pessoas que viram o ad
2. **Clicks**: Pessoas que clicaram
3. **LP Views**: Pessoas que viram a landing page
4. **Add to Cart**: Pessoas que adicionaram ao carrinho
5. **Purchases**: Pessoas que compraram

**Taxa de conversão esperada:**
- Impressions → Clicks: 1-3%
- Clicks → LP Views: 80-95%
- LP Views → Add to Cart: 20-40%
- Add to Cart → Purchase: 60-80%

**Problemas comuns:**
- Baixo CTR: Ad não é atrativo
- Alto Click, baixo LP View: Landing page lenta
- Alto Add to Cart, baixo Purchase: Problema no checkout
- Baixo Add to Cart: Oferta não convence

---

### 8. Previsão de Vendas

**Objetivo:** Estimar se o show vai esgotar.

**Cálculo:**
```
Tickets faltantes: 150
Dias até show: 10
Vendas diárias necessárias: 15

Média últimos 7 dias: 12

Projeção: 12 × 10 = 120 ingressos
Resultado: Não vai esgotar (30 ingressos faltando)
```

**Ação:**
- Aumentar budget de ads
- Criar urgência (últimos ingressos)
- Oferecer promoções

---

### 9. A/B Testing de Campanhas

**Objetivo:** Comparar performance de diferentes criativos.

**Setup:**
- Campanha A: Criativo 1
- Campanha B: Criativo 2
- Mesmo budget e público

**Métricas para comparar:**
- CTR (Click-Through Rate)
- CPC (Cost Per Click)
- Conversion Rate
- Cost per Purchase

**Exemplo:**
```
Campanha A: CTR 2.5%, CPC $0.50, Conv 8%
Campanha B: CTR 1.8%, CPC $0.40, Conv 12%

Resultado: B é melhor (menor CPC, maior conversão)
Ação: Pausar A, aumentar budget em B
```

---

### 10. Dashboard Executivo

**Objetivo:** Visão geral rápida para stakeholders.

**Métricas principais:**
- Total gasto em ads
- Total de ingressos vendidos
- ROAS médio
- Ocupação média
- Receita total

**Onde encontrar:**
- Tab "Integrated View"
- Correlações entre spend e vendas
- Eficiência geral das campanhas

---

## 🔧 Exemplos de Análise Avançada

### Calcular Break-even

```python
Custo do show: $50,000
Ingressos: 1,000
Preço médio: $75

Receita máxima: 1,000 × $75 = $75,000
Lucro potencial: $75,000 - $50,000 = $25,000

Budget máximo para ads: $25,000
Para break-even: Budget / Ingressos = $25 por ingresso

Se Ticket Cost < $25: Lucrativo
Se Ticket Cost > $25: Prejuízo
```

### Otimização de Bid Strategy

**Problema:** CPC muito alto

**Soluções:**
1. **Ampliar audiência:** Público maior = menor competição
2. **Melhorar relevância:** Criativo mais atraente = melhor score
3. **Testar horários:** Horários fora de pico = CPC menor
4. **Mudança de placement:** Stories pode ser mais barato que Feed

---

## 📊 Relatórios Sugeridos

### Relatório Semanal

**Métricas:**
- Total spend vs target
- Ingressos vendidos vs meta
- ROAS atual
- Shows em risco (baixa ocupação)
- Top 3 campanhas

### Relatório Pré-Show

**7 dias antes do show:**
- Ocupação atual
- Ingressos restantes
- Projeção de esgotamento
- Recomendações de ação

### Relatório Pós-Show

**Após o show:**
- Ocupação final
- Total gasto em ads
- ROAS final
- Lições aprendidas
- Benchmarks para próximos shows

---

## 🎓 Dicas de Especialista

1. **Comece com dados limpos:** Sempre valide os CSVs antes
2. **Acompanhe diariamente:** Não espere até a última semana
3. **Teste diferentes criativos:** A/B test é essencial
4. **Segmente por cidade:** Cada mercado é diferente
5. **Use remarketing:** Pessoas que visitaram mas não compraram
6. **Otimize landing page:** Velocidade e clareza importam
7. **Monitore concorrentes:** O que estão fazendo diferente?
8. **Aprenda com histórico:** Analise shows passados
9. **Seja ágil:** Ajuste rapidamente se algo não funciona
10. **Foco no ROAS:** Não apenas em vendas absolutas

---

## 📞 Perguntas Frequentes

**P: Quando aumentar o budget?**
R: Quando ROAS > 2.0 e ainda há ingressos para vender.

**P: Quando pausar uma campanha?**
R: Quando ROAS < 1.0 por 3+ dias consecutivos.

**P: Qual é um bom CTR?**
R: 1.5-3.0% para cold audience, 3-8% para warm/hot.

**P: Quanto gastar por show?**
R: 10-30% da receita potencial, dependendo da ocupação atual.

**P: Quando começar os ads?**
R: 6-8 semanas antes do show para eventos grandes.

---

**Última atualização:** Setembro 2025
