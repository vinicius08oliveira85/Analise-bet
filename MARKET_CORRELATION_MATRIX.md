# Matriz de Correlação entre Mercados - Champions League

---

## Objetivo
Evitar over-exposure a riscos correlacionados nas combinações.

---

## Correlações Históricas (Base: 5 temporadas CL)

| Mercado A | Mercado B | Correlação | Interpretação |
|-----------|-----------|------------|---------------|
| **Vitória Mandante** | **Over 2.5** | **+0.65** | Times que vencem tendem a marcar mais |
| **Vitória Mandante** | **BTTS Não** | **+0.45** | Favoritos controlam jogo, sofrem menos |
| **Over 2.5** | **BTTS Sim** | **+0.72** | Alta correlação - muitos gols = ambos marcam |
| **Over 2.5** | **Over 3.5** | **+0.85** | Quase linear - evite combinar ambos |
| **BTTS Sim** | **Over 3.5** | **+0.58** | Moderada |
| **Vitória Mandante** | **AH -1.5** | **+0.90** | Quase idêntico - NÃO combinar |
| **Empate** | **Under 2.5** | **+0.55** | Jogos truncados |
| **Vitória Visitante** | **BTTS Sim** | **+0.40** | Visitantes que vencem costumam marcar |
| **Escanteios Over** | **Over 2.5** | **+0.35** | Baixa - bom para diversificar |
| **Escanteios Over** | **Vitória Mandante** | **+0.30** | Muito baixa - excelente diversificador |
| **Cartões Over** | **Empate** | **+0.25** | Jogos tensos, truncados |
| **1º Tempo Over 0.5** | **Over 2.5** | **+0.60** | Gol cedo abre jogo |

---

## Regras de Combinação (Anti-Correlação)

### ✅ COMBINAÇÕES RECOMENDADAS (Baixa Correlação < 0.4)
| Mercado 1 | Mercado 2 | Correlação | Exemplo |
|-----------|-----------|------------|---------|
| Vitória Mandante | Escanteios Over | 0.30 | Bayern vence + Over 7.5 cantos |
| BTTS Sim | Vitória Visitante | 0.40 | BTTS + United vence fora |
| Over 2.5 | Cartões Over | 0.20 | Gols + jogo físico |
| DC 1X | Over 3.5 | 0.25 | Cobertura + gols |
| AH -1 | Escanteios Over | 0.28 | Handicap + cantos |

### ⚠️ COMBINAÇÕES CAUTELA (Correlação 0.4-0.6)
| Mercado 1 | Mercado 2 | Correlação | Ação |
|-----------|-----------|------------|------|
| Vitória Mandante | Over 2.5 | 0.65 | Reduzir stake 50% |
| BTTS Sim | Over 2.5 | 0.72 | **Evitar** ou stake mínima |
| Vitória Mandante | BTTS Não | 0.45 | OK se stake reduzida |

### ❌ COMBINAÇÕES PROIBIDAS (Correlação > 0.7)
| Mercado 1 | Mercado 2 | Correlação | Por que |
|-----------|-----------|------------|---------|
| Over 2.5 | Over 3.5 | 0.85 | Quase mesmo evento |
| Vitória Mandante | AH -1.5 | 0.90 | Matematicamente ligados |
| BTTS Sim | Over 3.5 | 0.58 | Overlap alto |

---

## Aplicação Prática nas 4 Combinações Padrão

### Combo 1 - Fundação (1X2 apenas)
- **Zero correlação interna** - mercados mutuamente exclusivos por jogo
- Risco: Apenas correlação entre jogos (ex: duas barbadas no mesmo dia)
- **Mitigação:** Max 1 barbada por liga/país por combo

### Combo 2 - Cobertura (1X + Valor)
| Seleção | Mercado | Correlação com outra | Ajuste |
|---------|---------|---------------------|--------|
| Bayern 1X | DC | - | Base |
| United 1X | DC | 0.05 (jogos independentes) | OK |
| PSV BTTS | BTTS | 0.15 vs DC | OK |
| Como Over 2.5 | Over | 0.25 vs BTTS | OK |

### Combo 3 - Especialista (Mesmo Mercado)
- **Over 2.5 x3** → Correlação entre jogos ~0.15 (independentes)
- **BTTS x4** → Correlação entre jogos ~0.10
- **Risco:** Variância alta, mas não correlacionado
- **Stake:** 1% banca (Kelly fracionário já considera)

### Combo 4 - Loteria (EV+ Alto)
- Mercados mistos intencionalmente (BTTS + Over + DC)
- Correlação média ~0.25
- **Stake:** 0.5% (tamanho controla risco)

---

## Cálculo de Risco de Portfólio

```python
def portfolio_var(bets, correlation_matrix, confidence=0.95):
    """
    Value at Risk do portfólio considerando correlações
    """
    weights = [b['stake_pct'] for b in bets]
    returns = [b['odds'] - 1 for b in bets]
    probs = [b['prob'] for b in bets]
    
    # Covariance matrix
    n = len(bets)
    cov = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                cov[i][j] = probs[i] * (1 - probs[i]) * returns[i]**2
            else:
                corr = correlation_matrix.get((i,j), 0.15)  # default baixa
                cov[i][j] = corr * np.sqrt(cov[i][i] * cov[j][j])
    
    port_var = np.sqrt(np.dot(weights, np.dot(cov, weights)))
    return port_var * norm.ppf(confidence)
```

### Limites de Risco
| Métrica | Limite | Ação se Excedido |
|---------|--------|------------------|
| VaR 95% Diário | 2% banca | Reduzir stakes proporcionalmente |
| Exposição Single Match | 5% banca | Não combinar >2 mercados mesmo jogo |
| Correlação Média Portfolio | <0.35 | Substituir seleções correlacionadas |
| Drawdown Máximo | 10% | Parar, revisar modelos |

---

## Monitoramento Dinâmico

### Alertas de Correlação Emergente
- **Odds Movement Paralelo:** Se 2+ seleções movem mesma direção → revisar
- **News Impact:** Lesão zagueiro → Over 2.5 e BTTS correlacionam +0.2
- **Weather:** Chuva forte → Under 2.5 e Empate correlacionam +0.3

### Ajuste de Pesos por Correlação
```python
def adjusted_kelly(kelly_raw, correlation_penalty):
    return kelly_raw * (1 - correlation_penalty)
# Ex: Kelly 2% com penalidade 0.3 → 1.4%
```

---

## Tabela Rápida de Referência

| Quer combinar... | Com... | Decisão |
|------------------|--------|---------|
| Vitória Favorito | Over 2.5 | ⚠️ Stake 50% |
| Vitória Favorito | BTTS Não | ✅ OK |
| Vitória Favorito | Escanteios Over | ✅ **Excelente** |
| BTTS Sim | Over 2.5 | ❌ Evitar |
| Over 2.5 | Over 3.5 | ❌ **Proibido** |
| AH -1.5 | Vitória Simples | ❌ **Proibido** |
| DC 1X | Over 3.5 | ✅ OK |
| Empate | Under 2.5 | ⚠️ Stake 50% |

---

*Atualizar correlações a cada 500 jogos (aprox. 1 temporada)*
*Fonte: Dados históricos CL 2021-2026, Opta/Understat*