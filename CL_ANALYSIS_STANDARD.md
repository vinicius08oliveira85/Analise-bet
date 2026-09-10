# Padrão de Análise Champions League - Regras de Padronização

---

## 1. ESTRUTURA OBRIGATÓRIA DO ARQUIVO FINAL

### 1.1 Cabeçalho
```markdown
# Análise Champions League - Matchday X | DD de Mês AAAA
**Data da Análise:** DD/MM/AAAA HH:MM UTC
**Fontes:** [Lista de fontes com timestamp]
**Versão:** 1.0
```

### 1.2 Seções Obrigatórias (ordem fixa)
1. **Resumo Executivo** - Tabela única com todas apostas ≥75%
2. **Análise por Jogo** - 6 jogos (ordem cronológica)
3. **Combinações Otimizadas** - Mínimo 4 combos padronizados
4. **Staking Plan** - Tabela com % banca por estratégia
5. **Alertas Pré-Jogo** - Checklist 1h antes
6. **Fontes Completas** - Tabela com URL, tipo, timestamp

---

## 2. COLETA DE DADOS - CAMPOS OBRIGATÓRIOS POR JOGO

### 2.1 Odds (Mínimo 4 casas)
| Campo | Formato | Exemplo |
|-------|---------|---------|
| Casa | Nome padrão | Bet365, William Hill, BoyleSports, Betfair Exch |
| 1X2 | Decimal 2 casas | 1.17 / 9.40 / 18.00 |
| Over 2.5 / 3.5 | Decimal | 1.22 / 1.55 |
| BTTS Sim/Não | Decimal | 1.85 / 1.95 |
| Handicap Asiático | Linha + Odds | -1.5 @ 1.45 |
| Dupla Chance | 1X / X2 / 12 | 1.01 / 13.00 / 1.03 |
| Escanteios | Over/Under linha | Over 7.5 @ 1.25 |

### 2.2 Probabilidades Modeladas (Mínimo 4 modelos)
| Modelo | Fonte | 1 | X | 2 | Over 2.5 | BTTS | Placar |
|--------|-------|---|---|---|----------|------|--------|
| xGScore | xgscore.io | 85.5% | 10.2% | 4.3% | 82% | 58% | 3-1 |
| ForaBet | forebet.com | 79% | 14% | 7% | 78% | - | 3-1 |
| Whoscored | whoscored.com | 84% | 11% | 5% | 80% | - | 3-0 |
| Lines | lines.com | 87% | 9% | 4% | 83% | - | - |
| **Média Ensemble** | **Cálculo próprio** | **84.3%** | **10.6%** | **5.1%** | **80.8%** | **56.4%** | **3.1-1.0** |

### 2.3 Team News (Formato Padronizado)
```markdown
**Time (Formação) - Técnico**
- **OUT:** Jogador (lesão, retorno estimado)
- **DÚVIDA:** Jogador (% chance, detalhe)
- **SUSPENSO:** Jogador (jogos restantes)
- **XI Provável:** G; D-D-D-D; M-M; M-M-M; A
- **Forma (últimos 5):** V V E D V
- **xG (últimos 5):** 2.1, 1.8, 2.3, 0.9, 1.5 (média: 1.72)
- **Estatística Chave:** "Invicto 38 jogos CL casa"
```

### 2.4 Mercados de Valor (Tabela Padronizada)
| Mercado | Odds Melhor | Prob. Ensemble | EV% | Kelly% | Recomendação |
|---------|-------------|----------------|-----|--------|--------------|
| Vitória Mandante | 1.17 | 87% | +1.8% | 2.1% | ✅ PRINCIPAL |
| Over 2.5 | 1.23 | 81% | -1.6% | - | ❌ Sem valor |

---

## 3. REGRAS DE CÁLCULO

### 3.1 Probabilidade Implícita
```python
prob_implicita = (1 / odds) * 100
# Com vig removido (método proporcional):
total_vig = sum(1/odds for odds in [odd_1, odd_x, odd_2])
prob_justa_1 = (1/odd_1) / total_vig * 100
```

### 3.2 Expected Value (EV)
```python
EV = (prob_real * odds) - 1
# Exemplo: 87% * 1.17 - 1 = 0.0179 = +1.79%
```

### 3.3 Kelly Criterion (Fracionário 25%)
```python
kelly_full = (prob_real * odds - 1) / (odds - 1)
kelly_frac = kelly_full * 0.25  # 25% Kelly para segurança
```

### 3.4 Probabilidade Combinada (Independentes)
```python
prob_combinada = prob_a * prob_b * prob_c
odds_combinada = odds_a * odds_b * odds_c
```

---

## 4. CLASSIFICAÇÃO DE CONFIANÇA

| Nível | Critério | Símbolo |
|-------|----------|---------|
| **Máxima** | Prob ≥85% + EV+ + 5+ modelos concordam + histórico robusto | ⭐⭐⭐⭐⭐ |
| **Alta** | Prob ≥75% + EV+ + 4 modelos + team news favorável | ⭐⭐⭐⭐ |
| **Média** | Prob ≥65% + EV+ ou Prob ≥75% EV neutro | ⭐⭐⭐ |
| **Baixa** | Prob ≥55% + EV+ marginal | ⭐⭐ |
| **Especulativa** | EV+ alto mas prob <55% | ⭐ |

---

## 5. COMBINAÇÕES PADRÃO (4 OBRIGATÓRIAS)

### Combo 1 - "FUNDAÇÃO" (Baixo Risco)
- 2-3 seleções prob ≥80% mercado 1X2
- Odds combinada 1.40-1.70
- Stake: 3-5% banca

### Combo 2 - "COBERTURA" (Médio Risco)
- 1X/12 nas barbadas + 1-2 mercados valor (BTTS/Over)
- Odds combinada 2.00-3.50
- Stake: 1.5-2.5% banca

### Combo 3 - "ESPECIALISTA" (Mercado Específico)
- 3-4 seleções mesmo mercado (ex: Over 2.5, BTTS, Escanteios)
- Todas com EV+ individual
- Stake: 1% banca

### Combo 4 - "LOTERIA DE VALOR" (Alto Risco/Retorno)
- 4-5 seleções EV+ alto (>15%) mas prob menor
- Odds combinada >5.00
- Stake: 0.5% banca

---

## 6. FONTES PRIORITÁRIAS (Ordem de Confiabilidade)

### Tier 1 - Modelos Quantitativos
1. **xGScore** (xgscore.io) - xG projetado
2. **Lines/Polymarket** (lines.com) - Mercado preditivo
3. **KickOff** (kickoff.co.uk) - Modelo Poisson
4. **PredictStats** (predictstats.com) - Ensemble

### Tier 2 - Análise Qualitativa Especializada
5. **Whoscored** (Kieran Williams) - Stats + team news
6. **TheHardTackle** - Análise tática profunda
7. **WinComparator** - Algoritmo proprietário

### Tier 3 - Odds & Market Data
8. **OddsJet** - Comparador multi-bookmaker
9. **Betfair Exchange** - Odds "sharp" sem viés
10. **Flashscore/William Hill/BoyleSports** - Odds varejo

### Tier 4 - Team News Oficiais
11. **Sites oficiais dos clubes** / **UEFA.com**
12. **Reporters locais** (Bulinews, Report.az, etc.)

---

## 7. CHECKLIST PRÉ-PUBLICAÇÃO

- [ ] Todos 6 jogos cobertos
- [ ] Odds de 4+ casas por jogo
- [ ] 4+ modelos de probabilidade por jogo
- [ ] Team news completos (lesões, suspensões, XI)
- [ ] Tabela "Mercados ≥75%" completa (todos mercados, não só 1X2)
- [ ] EV e Kelly calculados para cada recomendação
- [ ] 4 combinações padronizadas montadas
- [ ] Staking plan com % banca
- [ ] Alertas 1h antes listados
- [ ] Fontes tabeladas com URL + timestamp
- [ ] Disclaimer responsável incluído

---

## 8. NAMING CONVENTION ARQUIVOS

```
champions_league_analysis_YYYY-MM-DD.md
champions_league_analysis_YYYY-MM-DD_v2.md  (se atualização)
```

## 9. GIT COMMIT MESSAGE PADRÃO

```
feat: CL Matchday X analysis - DD/MM [baseline|enhanced|final]
- X jogos analisados
- Y mercados ≥75% identificados
- Z combinações montadas
- Fontes: [principais]
```

---

## 10. ATUALIZAÇÕES PERMITIDAS

| Momento | Ação | Versionamento |
|---------|------|---------------|
| Pré-jogo (T-24h) | Análise baseline | v1.0 |
| T-6h | Team news confirmados | v1.1 |
| T-1h | Odds movement + XI oficial | v1.2 |
| Pós-jogo | Resultado + lições | v2.0 (novo arquivo) |

---

*Documento vivo - Atualizar conforme evolução da metodologia*
*Última atualização: 10/09/2026*