# Template de Revisão Pós-Jogo - Champions League

---

## Objetivo
Registrar resultado real vs previsão para calibrar modelos e melhorar futuro.

---

## Estrutura por Jogo

### 1. RESULTADO REAL
| Campo | Valor |
|-------|-------|
| Placar Final | |
| Placar HT | |
| Gols (Minutos) | |
| Escanteios (Total/Cada) | |
| Cartões (A/V/Vm) | |
| xG Real (Opta/Understat) | |
| Posse % | |
| Chutes (Total/No alvo) | |

### 2. COMPARAÇÃO PREVISÃO vs REAL
| Mercado | Previsão (Prob) | Odds | Real | Acerto? | EV Realizado |
|---------|-----------------|------|------|---------|--------------|
| 1X2 | | | | ✅/❌ | |
| Over 2.5 | | | | ✅/❌ | |
| Over 3.5 | | | | ✅/❌ | |
| BTTS | | | | ✅/❌ | |
| AH | | | | ✅/❌ | |
| DC | | | | ✅/❌ | |
| Escanteios | | | | ✅/❌ | |
| Marcador | | | | ✅/❌ | |

### 3. ANÁLISE DE ERROS
| Mercado | Erro Tipo | Causa Raiz | Ação Corretiva |
|---------|-----------|------------|----------------|
| Ex: Over 2.5 | False Positive | Modelo superestimou xG do time fraco | Ajustar peso xGScore para underdogs |
| Ex: BTTS | False Negative | Não considerou desfalque zagueiro titular | Adicionar check "zagueiro titular ausente" |

**Tipos de Erro:**
- **False Positive** - Previu que aconteceria, não aconteceu
- **False Negative** - Previu que NÃO aconteceria, aconteceu
- **Calibration Error** - Probabilidade errada (ex: disse 80%, frequência real 60%)
- **Timing Error** - Odds mudaram após análise, valor sumiu

### 4. MODEL PERFORMANCE
| Modelo | Brier Score | Log Loss | Calibration | Comentário |
|--------|-------------|----------|-------------|------------|
| xGScore | | | | |
| Lines | | | | |
| KickOff | | | | |
| Whoscored | | | | |
| Ensemble | | | | |

### 5. LIÇÕES APRENDIDAS
- [ ] Fator novo identificado: _______________
- [ ] Peso de modelo ajustado: _______________
- [ ] Nova fonte de dados necessária: _______________
- [ ] Regra de exclusão criada: _______________

### 6. MÉTRICAS AGREGADAS (Matchday)
| Métrica | Valor | Target | Status |
|---------|-------|--------|--------|
| Taxa Acerto 1X2 | % | >65% | |
| Taxa Acerto Over 2.5 | % | >60% | |
| Taxa Acerto BTTS | % | >55% | |
| ROI Combinada Fundação | % | >5% | |
| ROI Combinada Valor | % | >15% | |
| Brier Score Ensemble | | <0.20 | |
| Log Loss Ensemble | | <0.60 | |

---

## Checklist Pós-Rodada
- [ ] Todos resultados registrados
- [ ] Erros categorizados
- [ ] Modelos reponderados se necessário
- [ ] Novas features documentadas
- [ ] Próxima rodada: ajustes aplicados

---

*Arquivo: `post_match_review_YYYY-MM-DD.md`*
*Commit junto com análise pré-jogo para rastreabilidade*