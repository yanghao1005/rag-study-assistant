# Guió de diapositives (català)

> **Font de veritat:** la deck viva a `http://localhost:3000/presentacio` (`frontend/src/features/presentacio/slides.ts`, 44 pantalles). Aquest fitxer és una còpia antiga de 20 pantalles; no el projectis. Hashes i temps actualitzats: `REVISIO-TRIBUNAL.md`.

20 pantalles, 16:9. Una idea per pantalla. Temps total objectiu: **30 min** (xerrada + demo).


Notes del presentador: el que dius, no el que es llegeix. Si la demo peta, les 13–16 substitueixen el recorregut en viu (captures del 31/08/2026).

Figures TikZ: exportar abans de muntar l’HTML; no incrustar `.tex`.

---

## Bloc A — Problema (slides 1–6, ~8 min)

### 1. Portada — 1 min

**Pantalla**

- Studyraft
- Assistent d’estudi RAG sobre documents propis
- Hao Yang · TFM · Màster universitari en Enginyeria Informàtica
- Director: Jordi Planes Cid
- EPS, Universitat de Lleida · setembre 2026

**Notes.** Nom, títol, director. Una frase: «he construït un sistema que parteix dels PDF de l’estudiant i tanca el cicle fins al repàs». No expliquis l’índex de la memòria.

**Asset.** Cap; fons clar Studyraft.

---

### 2. El problema — 1 min

**Pantalla** (tres línies)

- Un LLM sense recuperació al·lucina.
- Un cercador sense cites no s’audita.
- Unes flashcards sense calendari no consoliden.

**Notes.** El cas d’ús és estudiar d’apunts en PDF. Les eines genèriques cobreixen un tros. Cal (i) documents *teus*, (ii) evidència localitzable, (iii) pràctica + repàs.

---

### 3. Quatre baules — 1,5 min

**Pantalla.** Figura del cicle (exportar `figures/cicle.tex`):

1. Indexar PDF privat
2. Recuperar amb evidència
3. Generar ancorat
4. Repassar SM-2

**Notes.** Això és el producte, no un notebook. Si una baula falta, el cicle es trenca: NotebookLM cita però no tanca SRS; Anki tanca SRS però no parteix del PDF amb cites.

**Asset.** `cicle.svg`

---

### 4. El forat no és un algoritme nou — 1,5 min

**Pantalla.** Taula (cobertura declarada, agost 2026; no és un ranking):

| | PDF propis | Cites | Pràctica | SRS |
|---|---|---|---|---|
| Anki | no natiu | no | sí | sí |
| NotebookLM | sí | sí | limitat | no |
| ChatGPT + fitxers | sí | variable | no | no |
| Studyraft | sí | sí | sí | SM-2 |

**Notes.** No «guanyem» Anki ni NotebookLM. Ocupem la casella d’integració: quatre baules sobre documents privats, amb arquitectura llegible i avaluable. Una sola taula; no l’estat de l’art sencer.

---

### 5. Què aporta aquest TFM — 1,5 min

**Pantalla.** Cinc punts curts:

- Hexàgon (domini sense I/O) després d’un prototip LangChain
- Ingestió per etapes, relançable
- RAG híbrid (dens + lèxic + RRF)
- Cicle d’estudi a la UI (xat, biblioteca, planner)
- Protocol: tests + latència + recorregut qualitatiu

**Notes.** La reconstrucció hexagonal és una contribució d’enginyeria, no cosmètica: permet tests sense claus i canviar d’OpenAI a Gemini sense reescriure el xat.

---

### 6. Objectius: O1–O5 fets, O6 parcial — 1,5 min

**Pantalla**

- O1–O5: implementats (API + UI + test)
- O6: protocol executat, **parcial**
- No mesurat: fidelitat, només dens, ingestió, xat extrem a extrem, estudi amb alumnes

**Notes.** Digues «parcial» aquí, no a la última pregunta del tribunal. O6 no es tanca amb un pytest. Això obre el bloc d’arquitectura: com s’ha construït el que sí es pot demostrar.

---

## Bloc B — Arquitectura (slides 7–11, ~6 min)

### 7. Hexàgon — 1,5 min

**Pantalla.** Figura `hexagonal.tex`: HTTP / CLI / worker → ports → casos d’ús → domini; a la dreta Postgres, LLM, Storage.

**Notes.** El cas d’ús no coneix HTTP ni el client de BD. SM-2 viu al domini («aquesta carta surt avui perquè q < 3»). Costat conductor vs conduït: una frase n’hi ha prou.

**Asset.** `hexagonal.svg`

---

### 8. Ingestió per etapes — 1 min

**Pantalla.** Una línia:

`download → parse → chunk → embed → store → synopsis`

**Notes.** Relançable i depurable; el worker corre a FastAPI. Un PDF escanejat (parse buit) és un error honest: no hi ha OCR. No ensenyes Docker ni les 35 rutes.

**Asset.** opcional `pipeline.svg`

---

### 9. RAG híbrid — 2 min

**Pantalla.** Figura `retrieval.tex`: pregunta → intent → embedding → dens + FTS → RRF → rerank opcional → cites + LLM.

**Notes.** Dens per paràfrasi, lèxic per termes rars, RRF fusiona sense un model extra. Intent: resum / capítol / factual. El rerank LLM i l’agentic existeixen com a flags, **apagats per defecte**. Producte: top-k = 8.

**Asset.** `retrieval.svg`

---

### 10. Cites, no «el model ho ha dit» — 1 min

**Pantalla.** Tres camps: fitxer · interval de pàgines · fragment.

**Notes.** La confiança del xat és la cita clicable, no la fluïdesa de la frase. Política lecture-focused: el context ve dels apunts, no d’un corpus web.

**Asset.** retall de `05-chat.png` (cites visibles; contactes tapats com a la memòria).

---

### 11. Canviem a l’app — 0,5 min

**Pantalla.** Una frase: «Demo en local, un sol recorregut.»

Quatre batecs (també a les notes):

1. Assignatura + PDF ja *Listo* (no esperis el worker)
2. Pregunta factual → cita
3. Biblioteca: flashcard o quiz
4. Ressenya SM-2 al planner

**Notes.** Alt+Tab a localhost. Si peta: «passo a captures» i avança a 13. No reinstal·lis res.

---

## Bloc C — Demo (10 min en viu; slides 12–16 de xarxa)

### 12. Guió de demo (no projectar el text sencer)

**Pantalla.** Quatre verbs: Indexar · Preguntar · Practicar · Repassar.

**Notes (assaig, sempre el mateix PDF):**

1. Documents en estat Listo.
2. «Què diu el document sobre [terme del corpus]?» Senyala fitxer i pàgines.
3. Obre un conjunt de la biblioteca (no generis de zero si triga).
4. Marca una carta; el planner diu el proper dia.

Wi‑Fi UdL = pla B. Tot local, sessió feta, tabs en mosaic.

---

### 13. Xarxa: documents — si cal

**Asset.** `screenshots/04-documents.png` — PDF *Listo*, noms numerats.

**Notes.** RF ingestió visible. Una assignatura auxiliar *test* pot sortir a la barra: no és el corpus del benchmark.

---

### 14. Xarxa: xat

**Asset.** `screenshots/05-chat.png`

**Notes.** Intent resum o factual, el que ensenyi la captura. El correu del peu i dades de persones al fragment: tapats a la memòria; igual aquí.

---

### 15. Xarxa: pràctica

**Assets.** `06-quiz.png` o `07-flashcards.png` (una sola).

**Notes.** Conjunts amb títol, editables. No és un test efímer al xat.

---

### 16. Xarxa: planner

**Asset.** `screenshots/08-planner.png`

**Notes.** SM-2 al domini, no un cron misteriós. Tanca la demo: el cicle torna al calendari.

---

## Bloc D — Prova i límits (slides 17–20, ~8 min)

### 17. Qualitat de programari — 2 min

**Pantalla** (1/09 i 31/08/2026):

- 63 pytest unitaris
- ruff i mypy nets (77 fitxers)
- tsc OK
- 4 Vitest · 2 Playwright smoke (landing/login, no el RAG)

**Notes.** Això és programari. Playwright no executa xat ni planner. El cicle a la UI el demostra la demo (o les captures), no la CI.

---

### 18. Latència de retrieval — 2,5 min

**Pantalla.** 8 consultes factuals, 114 chunks, 31/08/2026, **k = 10 al CLI d’aquest run** (el producte usa k = 8):

| Política | p50 | max |
|---|---|---|
| Híbrid RRF | 369 ms | 3991 ms |
| Híbrid + rerank LLM | 1608 ms | 2745 ms |

**Notes.** El max 3991 ms és la primera consulta (fred). El rerank es va mesurar després, model calent: no llegeixis el max com a «el rerank és més ràpid al pitjor cas». El que es compara és el **p50**. Per això el rerank està apagat per defecte. No afirmis rellevància ni groundedness.

---

### 19. Què no afirma aquesta avaluació — 2 min

**Pantalla**

- Sense línia «només dens»
- Sense mètrica de fidelitat
- Sense temps d’ingestió ni xat extrem a extrem
- Sense estudi amb n alumnes

**Notes.** O6 resta parcial. És un TFM d’enginyeria de sistema, no un paper de IR ni un assaig pedagògic. Si pregunten ètica: PDF privats, RLS, el que surt cap a l’ReM són fragments; una frase i prou.

---

### 20. Tancament — 1,5 min

**Pantalla**

- Sistema: hexàgon + híbrid + cicle SM-2
- O1–O5 al producte; O6 oberta on toca
- Futur: OCR, visor PDF amb highlight, groundedness, E2E
- github.com/yanghao1005/rag-study-assistant

**Notes.** Agraeix. «Preguntes.» No reobris el capítol 7 ni l’annex de desplegament tret que ho demanin.

---

## Ritme (control)

| Minut | Slide | Què |
|---|---|---|
| 0–8 | 1–6 | Problema i objectius |
| 8–14 | 7–11 | Arquitectura i cites |
| 14–24 | 12 (+13–16 si cal) | Demo |
| 24–30 | 17–20 | Números, límits, tancament |

Si vas llarg: salta 5 (contribucions, ja les has dit a 3–4) i 8 (pipeline: una frase a 7). No saltis 6 ni 19.

## El que no entra

Gantt, 35 rutes, Docker pas a pas, `legacy_code`, llistes de frameworks, «O6 complet», zoom estil Prezi.
