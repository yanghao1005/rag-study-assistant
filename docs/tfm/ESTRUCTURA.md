# Què cal redactar a la memòria del TFM

No existeix una plantilla nacional única. Cada centre fixa portada, extensió i algun capítol extra.
Aquesta carpeta usa un **superset** alineat amb:

- UPM / ETSI Informàtics (ordre de capítols i format Times 12 pt, A4, 1,5)
- UCM (resum + abstract EN, paraules clau, ~50 pàgines de cos)
- FIB / UPC (ètica, sostenibilitat i, a MEI, gestió del projecte)

Quan tinguis la guia del teu màster, ajusta `metadata.tex` i, si cal, l'ordre de `\input` a `main.tex`. El cos està en **català**.

## 1. Peces que gairebé sempre són obligatòries

| Peça | Què demana el tribunal | En aquest repo |
| --- | --- | --- |
| Portada institucional | Universitat, màster, títol CA+EN, autor, director, curs | Plantilla oficial del centre (fora d'aquest `.tex`) |
| Resum | ½–1 pàgina + paraules clau; al principi | `front/resumen.tex` |
| Índexs | Continguts, figures, taules | automàtics |
| Introducció i objectius | Problema, per què no basta un producte existent, abast | `chapters/01-introduccion.tex` |
| Estat de l'art | RAG, cerca híbrida, SRS, apps d'estudi, arquitectures | `chapters/02-estado-arte.tex` |
| Desenvolupament | Disseny + implementació justificant decisions | caps. 3–5 |
| Resultats | Evidència: latència, qualitat, tests, limitacions | `chapters/06-resultados.tex` |
| Conclusions i futur | Objectius acomplerts / no, línies I+D | `chapters/08-conclusiones.tex` |
| Bibliografia | APA o IEEE segons centre; cites verificables | `bib/referencias.bib` |
| Annexos | Desplegament, API, esquema SQL, protocol d'aval. | `anexos/` |

## 2. Peces que alguns centres exigeixen i d'altres no

| Peça | On s'exigeix | Consell |
| --- | --- | --- |
| Avaluació de riscos / alternatives | UPM (abans del desenvolupament) | Ja és al cap. 7; si ets UPM, mou-lo davant del cap. 5 |
| Gestió i planificació | FIB MEI, molts TFM d'enginyeria | Cap. 7 (fases reals del repo) |
| Ètica, privadesa, sostenibilitat | UPC (acord 07-2023) i cada cop més tribunals | Cap. 7 + annex si creix |
| Traducció d'intro i conclusions a l'anglès | UCM si el cos no és anglès | Afegir al final si aplica |
| Dedicatòria / agraïments / declaració d'autoria | Opcionals; no s'inclouen aquí | Si el centre els demana, van a la plantilla oficial |

## 3. Índex proposat (aquesta memòria)

1. **Introducció i objectius** — problema, motivació, contribucions, objectius SMART, fora d'abast.
2. **Estat de l'art** — fil del cicle d'estudi (indexar → recuperar → generar ancorat → repassar); cada secció tanca una baula i el forat del TFM és la integració. No és un catàleg de frameworks.
3. **Anàlisi i requisits** — actors, RF/RNF, casos d'ús del cicle assignatura → PDF → xat → pràctica.
4. **Arquitectura i disseny** — hexàgon FastAPI, Next.js, Supabase (Auth, pgvector, Storage, RLS).
5. **Desenvolupament** — pipeline d'ingestió, retrieval, generació, frontend, qualitat (ruff/mypy/vitest/Playwright).
6. **Experimentació i resultats** — protocol amb el CLI de benchmark, tests, amenaces a la validesa. **Aquí falten números reals.**
7. **Gestió, riscos, ètica i sostenibilitat** — planificació, riscos tècnics, GDPR dels PDF, cost energètic dels embeddings.
8. **Conclusions i treball futur**
9. **Bibliografia**
10. **Annexos** — desplegament, esquema/API, com reproduir l'avaluació.

Extensió orientativa del cos (sense portada ni annexos): **50–80 pàgines**. Un TFM d'enginyeria de programari amb sistema construït viu bé en ~60.

## 4. Què ja es pot redactar amb el codi (Studyraft)

- Motivació i objectius: cicle d'estudi sobre PDF propis, cites, flashcards/quiz, planner SM-2.
- Arquitectura hexagonal: `backend/app/domain`, `ports`, `adapters`, `entrypoints`, `container.py`.
- Pipeline: `DOWNLOAD → PARSE → CHUNK → EMBED → STORE → SYNOPSIS`.
- Retrieval: dens (pgvector) + lèxic (BM25) + fusió; rerank LLM opcional; índex jeràrquic (sinopsi); agentic (flag).
- Frontend: Next.js 16, auth Supabase, xat amb streaming i cites, documents, quiz, planner, settings.
- Qualitat: pytest unitari, ruff, mypy, Vitest, Playwright smoke, Docker Compose.
- Migració 0008: `documents.synopsis` + `flashcard_reviews`.

## 5. Què NO es pot inventar (bloqueja una memòria defensable)

1. **Dades de portada**: van a la plantilla oficial del centre, no a aquest `.tex`.
2. **Resultats quantitatius**: executa `python -m app.entrypoints.cli.benchmark` sobre un corpus real i enganxa taules al cap. 6.
3. **Estat de l'art de veritat**: cal llegir i citar papers, no només llistar eines.
4. **Plantilla oficial** de portada: s'uneix al PDF d'aquest cos al lliurament.
5. **Ètica/sostenibilitat** amb el formulari UPC si estudies allà.
6. **Comparació experimental** vs baseline (només dens, només BM25, amb/sense rerank). El codi ho permet; falten les xifres.

## 6. Ordre de redacció recomanat

1. Completar `metadata.tex`.
2. Cap. 3 (requisits) i 4 (arquitectura) — surten del codi.
3. Cap. 5 (desenvolupament) amb figures del pipeline i de l'hexàgon.
4. Cap. 2 (estat de l'art) amb bibliografia.
5. Córrer avaluació i escriure cap. 6.
6. Cap. 1 i 8 al final (intro i conclusions es reescriuen quan ja hi ha resultats).
7. Cap. 7 i annexos.
8. Resum (últim).

## 7. Rúbrica típica del tribunal (per no fallar el to)

- Problema clar i objectius comprovables.
- Treballs relacionats honestos (límits del que existeix).
- Decisions de disseny justificades (per què hexagonal, per què híbrid, per què Supabase).
- Resultats amb mètode, no només captures de pantalla.
- Limitacions i treball futur realistes (PDF escanejat, agentic d'una passada, sense visor PDF complet).
- Memòria ben maquetada, cites correctes, català tècnic.
