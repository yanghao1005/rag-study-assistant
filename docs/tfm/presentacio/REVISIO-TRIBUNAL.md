# Revisió de la defensa — ull de tribunal (passada 4)

**Data:** 20 de setembre de 2026  
**Deck:** `http://localhost:3000/presentacio` (**44 pantalles**)  
**Memòria:** `docs/tfm/REVISIO-TRIBUNAL.md`

Això no és la rúbrica oficial EPS. Lectura com a membre pedant: dipòsit + 25 min + preguntes.

**Veredicte.** El sistema (hexàgon, pipeline, híbrid, SM-2) és al codi. La deck torna a tenir **avaluació a pantalla** (tests, p50, límits) i l’híbrid 20+20→8. La UI és en castellà de tu; memòria i deck en català. No tradueixis les captures.

---

## Recorregut 25 min (demo a dins)

Portades: 10 s. **No llegeixis les 44.** Objectiu: 20 min de xerrada + 5 min de demo.

| Min | `#` | Què |
| --- | --- | --- |
| 0:00–0:20 | 1 | Portada. Subtítol oral: RAG sobre PDF propis. |
| 0:20–1:30 | 2–4 | Problema + quatre baules. |
| 1:30–3:00 | 6–7, 9–10 | Producte, abast, mercat, **SM-2 vs ITS `#/10`**. |
| 3:00–9:00 | 12–27 | Disseny. **Gao `#/18`**, chunk `#/20`, ingestió `#/21`, híbrid `#/23`, SM-2 `#/27`. Salta BD/casos si vas llarg. |
| 9:00–9:40 | 29–30 | Guió demo. UI en castellà. |
| **9:40–14:40** | — | **Demo 5 min.** Si peta: `#/31`–`#/35`. |
| 14:40–17:00 | 37–39 | Tests, p50, límits. **No saltis.** |
| 17:00–19:30 | 41, 43–44 | Cost + futur + tancament. |

**No saltar:** Gao `#/18`, híbrid `#/23`, SM-2 `#/27`, tests `#/37`, p50 `#/38`, límits `#/39`.

---

## Preguntes dures (ja a pantalla)

| Pregunta | Pantalla | Resposta |
| --- | --- | --- |
| Sou l’únic operador? | `#/38` `#/39` | Sí. Descriptiu, l’autor, apunts propis. |
| El max 3991 vs 2745 demostra que el rerank és més estable? | `#/38` | No. Es compara el **p50**. Max híbrid = fred. |
| On és la fórmula SM-2? | `#/27` | `q<3` → 1 dia. `q≥3`: 1 → 6 → `round(I × ease)`. |
| Això és hexagonal si el worker viu a FastAPI? | `#/13` | El worker és un *entrypoint*, no el nucli. |
| Quin model pagueu? | `#/41` | embedding-3-small; xat `gpt-4.1-mini`. |
| Heu demostrat que l’híbrid recupera millor? | `#/23` `#/39` | No. Argument: paràfrasi *i* sigles. Sense dens-only. |
| Playwright valida el RAG? | `#/37` | No. Smoke landing/login, sí a la CI. |
| Rate limit? | `#/39` | Flag de paper; no hi ha middleware. |

---

## Dipòsit (no la xerrada)

- `metadata.tex` ja té autor / tutor / UdL / EPS / màster / Lleida.
- Portada institucional EPS + declaració d’autoria / ètica: secretaria, no la deck.
- `guio.md` i `index.html` estan desfasats. Un sol URL: el frontend.
