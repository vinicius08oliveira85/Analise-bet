# Gestão de Risco Avançada - Champions League Betting

---

## Princípios Fundamentais

1. **Preservação de Capital** > Crescimento
2. **Edges Pequenos + Consistência** > Home Runs
3. **Matemática** > Intuição
4. **Processo** > Resultado Individual

---

## 1. BANKROLL MANAGEMENT

### Estrutura de Banca
```
BANCA TOTAL (100%)
├── Banca Ativa (70%) - Apostas CL + outras ligas
├── Reserva de Oportunidade (20%) - Edges excepcionais, live betting
├── Reserva de Segurança (10%) - Nunca tocar, recolhe juros
```

### Kelly Criterion - Implementação Prática

```python
def kelly_stake(prob, odds, bankroll, fraction=0.25, max_stake_pct=0.05):
    """
    fraction: 0.25 = 25% Kelly (conservador)
    max_stake_pct: teto absoluto 5% banca ativa
    """
    if prob * odds <= 1: return 0  # Sem edge
    
    kelly_full = (prob * odds - 1) / (odds - 1)
    kelly_frac = kelly_full * fraction
    
    # Cap em 5% banca ativa
    stake_pct = min(kelly_frac, max_stake_pct)
    
    # Arredondar para unidades discretas
    return round(stake_pct * bankroll * 0.7, 2)  # 70% banca ativa
```

### Tabela de Stakes por Confiança

| Confiança | Prob Mínima | Kelly Frac | Stake Máx | Exemplos |
|-----------|-------------|------------|-----------|----------|
| **Máxima (5★)** | ≥85% | 25% | 5% | Bayern 1.17, United 1.25 |
| **Alta (4★)** | 75-85% | 20% | 3.5% | Over 2.5 barbadas, DC 1X |
| **Média (3★)** | 65-75% | 15% | 2.5% | BTTS value, AH -1 |
| **Baixa (2★)** | 55-65% | 10% | 1.5% | Over 3.5, Marcador |
| **Especulativa (1★)** | <55% | 5% | 0.5% | Combos loteria, Placar exato |

---

## 2. PORTFOLIO CONSTRUCTION

### Alocação por Tipo de Aposta (Banca Ativa)

| Categoria | % Banca Ativa | Nº Apostas/Semana | Objetivo |
|-----------|---------------|-------------------|----------|
| **Core (Fundação)** | 40% | 2-3 | Crescimento estável 3-5%/mês |
| **Value (Especialista)** | 30% | 3-5 | Alpha 8-12%/mês |
| **Hedge (Cobertura)** | 20% | 2-3 | Reduzir variância |
| **Satellite (Loteria)** | 10% | 1-2 | Upside 20%+ (pequeno) |

### Diversificação Obrigatória
- **Max 30%** em um único dia de jogos
- **Max 20%** em uma única liga (CL = 1 liga)
- **Max 15%** em um único time
- **Max 10%** em correlação >0.5 (ver matriz)

---

## 3. RISK LIMITS - HARD STOPS

### Limites Diários
| Métrica | Limite | Ação |
|---------|--------|------|
| Perda Diária | 3% banca total | **PARAR** - revisar apenas amanhã |
| Perda Matchday CL | 5% banca ativa | Reduzir stakes 50% próximos jogos |
| Stake Total Dia | 10% banca ativa | Não exceder |
| Nº Apostas Dia | 8 | Qualidade > Quantidade |

### Limites Semanais
| Métrica | Limite | Ação |
|---------|--------|------|
| Drawdown Semanal | 8% banca total | Reduzir todas stakes 50% |
| Drawdown Mensal | 15% banca total | **PAUSAR 1 SEMANA** - auditoria completa |
| ROI Mínimo (4 semanas) | +2% | Se negativo → revisar modelos |

### Limites por Combinação
| Combo Tipo | Stake Máx | Perda Máx/Combo | Correlação Máx |
|------------|-----------|-----------------|----------------|
| Fundação | 5% | 2% | 0.20 |
| Cobertura | 2.5% | 1.5% | 0.35 |
| Especialista | 1% | 0.8% | 0.40 |
| Loteria | 0.5% | 0.5% | 0.50 |

---

## 4. POSITION SIZING DINÂMICO

### Ajuste por Volatilidade (Volatility Targeting)
```python
def vol_adjusted_stake(base_stake, recent_vol, target_vol=0.15):
    """
    recent_vol: desvio padrão retornos últimos 30 dias
    target_vol: volatilidade alvo anualizada 15%
    """
    if recent_vol == 0: return base_stake
    multiplier = target_vol / (recent_vol * np.sqrt(252))
    return base_stake * min(max(multiplier, 0.5), 1.5)
```

### Ajuste por Streak (Anti-Martingale)
```python
def streak_adjustment(current_stake, wins_last_10, losses_last_10):
    win_rate = wins_last_10 / (wins_last_10 + losses_last_10)
    
    if win_rate > 0.65:      # Hot streak - leve aumento
        return current_stake * 1.1
    elif win_rate < 0.45:    # Cold streak - reduzir
        return current_stake * 0.7
    elif losses_last_10 >= 4: # 4+ perdas seguidas
        return current_stake * 0.5  # Cut half
    return current_stake
```

---

## 5. HEDGING & LIVE MANAGEMENT

### Regras de Hedge (Ao Vivo)
| Cenário | Ação | Tamanho Hedge |
|---------|------|---------------|
| Favorito vence 1-0 aos 60' | Back empate/under | 50% lucro potencial |
| Underdog vence 1-0 aos 70' | Cash out parcial | 30-40% stake |
| 0-0 aos 75' (Over 2.5 bet) | Back Under 1.5 HT | 25% stake |
| Golo contra (nosso time) | Avaliar cash out | Se xG < 0.3 → cash out 50% |

### Cash Out Rules
- **Nunca** cash out por medo (apenas por math)
- **Auto-cash out** se: probabilidade implícita live > 95% (lock profit)
- **Partial cash out** se: edge live < 1% mas > 0%

---

## 6. MODEL RISK CONTROLS

### Model Degradation Detection
```python
def check_model_health(model_predictions, actual_results, window=50):
    """
    Rodar semanalmente
    """
    # Brier Score
    brier = np.mean((np.array(model_predictions) - np.array(actual_results))**2)
    
    # Calibration (binning)
    calibration_err = calibration_error(model_predictions, actual_results)
    
    # Log Loss
    logloss = log_loss(actual_results, model_predictions)
    
    alerts = []
    if brier > 0.22: alerts.append(f"Brier {brier:.3f} > 0.22")
    if calibration_err > 0.05: alerts.append(f"Calib {calibration_err:.3f} > 0.05")
    if logloss > 0.65: alerts.append(f"LogLoss {logloss:.3f} > 0.65")
    
    return alerts
```

### Model Weight Adjustment
| Métrica | Threshold | Ação |
|---------|-----------|------|
| Brier > 0.22 | 2 semanas seguidas | Reduzir peso 50% |
| Calibration > 0.05 | 3 semanas | Re-treinar / remover |
| LogLoss > 0.65 | Imediato | Pausar modelo |
| EV Realizado < 0 | 1 mês | Remover do ensemble |

---

## 7. PSYCHOLOGICAL CONTROLS

### Regras Comportamentais
1. **Não apostar** se: cansado, emocionalmente abalado, sob influência
2. **Não aumentar stake** para "recuperar" perda (anti-tilt)
3. **Não pular análise** por pressa - se não há tempo, não aposta
4. **Registro obrigatório** de TODA aposta (mesmo as perdidas)
5. **Revisão semanal** obrigatória - 30min domingo

### Tilt Detection
```python
def detect_tilt(recent_bets):
    signals = []
    if len([b for b in recent_bets if b['stake'] > b['avg_stake']*1.5]) > 2:
        signals.append("Stake escalating")
    if len([b for b in recent_bets if b['time'] > 22:00]) > 3:
        signals.append("Late night betting")
    if sum(b['stake'] for b in recent_bets) > daily_limit * 0.8:
        signals.append("Approaching daily limit")
    return signals
```

---

## 8. REPORTING & ACCOUNTABILITY

### Dashboard Semanal (Automatizado)
| Métrica | Fórmula | Target |
|---------|---------|--------|
| **ROI** | Lucro / Volume | >5% |
| **ROC** | Lucro / Banca | >2% |
| **Hit Rate** | Acerto / Total | >55% (1X2) |
| **Avg Odds** | Média ponderada | 1.5-2.5 |
| **CLV** | Closing Line Value | >0% (beat market) |
| **Max DD** | Pico → Vale | <8% |
| **Sharpe** | (ROI - rf) / Vol | >1.0 |

### Log Obrigatório por Aposta
```json
{
  "date": "2026-09-10",
  "match": "Bayern vs Bodo",
  "market": "Bayern Vence",
  "odds": 1.17,
  "prob": 0.872,
  "ev": 0.018,
  "kelly": 0.021,
  "stake_pct": 0.03,
  "stake_eur": 30,
  "confidence": 5,
  "combo": "Fundacao",
  "result": "PENDING",
  "notes": "Gnabry out, Kane 7g streak"
}
```

---

## 9. CONTINGÊNCIA - CENÁRIOS EXTREMOS

| Cenário | Trigger | Protocolo |
|---------|---------|-----------|
| **Black Swan** (ex: pandemia, guerra) | Mercado fecha / odds >100 | Cash out tudo, banca em cash |
| **Model Collapse** | 3 modelos falham mesma semana | Pausar tudo, voltar a paper trading 2 semanas |
| **Account Limitation** | Bookie limita stakes | Migrar para exchanges/sharp books |
| **Regulatory Change** | Nova lei país | Compliance imediato, ajustar jurisdição |
| **Tech Failure** | API/scraper down 2h+ | Fallback manual (fontes Tier 1 apenas) |

---

## 10. CHECKLIST DIÁRIO (Pré-Jogo)

- [ ] Banca atualizada
- [ ] Limites diários calculados
- [ ] Correlações verificadas (matriz)
- [ ] Model health check OK
- [ ] Team news confirmados 1h antes
- [ ] Odds não movidas >5% contra (sharp move)
- [ ] Stakes calculadas (Kelly + ajustes)
- [ ] Log preparado para cada aposta
- [ ] Plano B se lineup mudar (ex: Kane não joga)
- [ ] Mental state: OK para operar

---

## 11. ESCALA DE EVOLUÇÃO

| Fase | Banca | Stakes | Combos | Foco |
|------|-------|--------|--------|------|
| **Iniciante** | <1k | 1% fixo | Apenas Fundação | Disciplina, registro |
| **Desenvolvimento** | 1-10k | Kelly 15% | Fundação + Cobertura | Calibração modelos |
| **Consistente** | 10-50k | Kelly 20% | 3 combos | Otimização portfolio |
| **Profissional** | 50-200k | Kelly 25% | 4 combos + live | Scaling, automação |
| **Institucional** | >200k | Kelly 25% + vol target | Custom | Risk management avançado |

---

*Revisar trimestralmente | Aprovar mudanças por escrito | Versionar no git*