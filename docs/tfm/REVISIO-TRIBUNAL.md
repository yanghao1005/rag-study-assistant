# Revisió de la memòria — ull de tribunal

**Data:** 1 de setembre de 2026  
**PDF:** `docs/tfm/build/tfmbody.pdf` (~62 pàgines, `oneside` / `openany`)  
**Això no és la rúbrica oficial del centre.** És una lectura com a membre de tribunal d’un TFM d’enginyeria: sistema construït + memòria.

**Passada d'estil (1/09/2026, cos només):** resum més mètode+resultat; menys «no és X»; sense `DESIGN.md` ni paths de repo al cos; Vitest explicat; annex A maquetat; dates de memòria unificades a l'1/09. **Passada 20/09:** `metadata.tex` omplert (Hao Yang / Planes / UdL); Playwright smoke reconegut a la CI del cap. 5–6.

---



## 1. Què aguanta (no reobrir)


| Punt                                                                                            | Per què el tribunal ho accepta                        |
| ----------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| Novetat = integració avaluable, no algoritme nou                                                | Honest; evita la pregunta «on és el paper de SIGIR?». |
| Cap. 2 amb 4 baules + papers (chunking, Lost in the Middle, RAGAS, PaperQA, ITS, SM-2/HLR/FSRS) | Ja no és un catàleg de productes.                     |
| Taula de mercat com a *cobertura declarada*, no ranking                                         | No infla.                                             |
| RLS vs service role + diagrama de confiança                                                     | Pregunta típica de seguretat coberta.                 |
| O6 obert on toca (groundedness, dens-only, *n* alumnes)                                         | Millor que un número inventat.                        |
| Cap. 6: p50/max, 8 consultes, 114 chunks, captures amb RF al peu, amenaces a la validesa        | Protocol d’enginyeria, no galeria.                    |
| Cap. 7: tres comptes (hores / allotjament / tokens) + exemples A/B                              | Deixa de ser «preus genèrics».                        |
| Rate limit: flag sense middleware                                                               | Deute dit; no es ven com a protecció.                 |
| 390 h = estimació Git, no timesheet                                                             | Dit al cap. 1.                                        |
| Idiomes: memòria català; UI castellà de tu                                                      | Coherent; les captures diuen *Listo* i està explicat. |
| Abstract EN + paraules clau                                                                     | Molts centres ho exigiran.                            |
| Sense pàgines en blanc entre capítols                                                           | Adequat a PDF de lliurament.                          |


---



## 2. Estil (el que un tribunal nota sense dir-ho)



### El que funciona

- Veu d’enginyeria, no de brochure: «el problema no és cridar un LLM».
- Cada capítol obre amb *què mesura* o *què no és*. Això ajuda a un lector cansat.
- Figures amb funció (cicle, hexàgon, pipeline, seqüències, Gantt, captures).
- Català tècnic correcte en general; anglicismes (RAG, chunk, groundedness, rerank) estan justificats i a la llista d’acrònims.



### El que cansa o sona a defensa anticipada

La memòria **nega massa**. Patró recurrent: «no és X; és Y». Serveix un cop per capítol; repetit (intro, SoA, resultats, conclusions) sona a que l’autor té por del tribunal. No cal reescriure els caps. 3–6. Si es poleix estil, **retallar 4–5 negacions** a intro/conclusions n’hi ha prou.

Frases que un membre pedant marcarà:

- Cites a `DESIGN.md` i rutes de repo al cos: el PDF ha de ser llegible **sense obrir Git**. El tribunal no té el teu editor. Deixar paths als annexos; al cos, «el sistema de disseny Studyraft» n’hi ha prou.
- Mescla **Must/Should/Could** (anglès MoSCoW) amb text català: acceptable si es defineix un cop (ja es fa); no n’afegeixis més.
- Captures en castellà dins d’una memòria en català: **correcte** (és el producte). No tradueixis les captures.
- Resum molt carregat de stack (versions, 38 rutes, `optimizePackageImports`). Per a un resum institucional a vegades es prefereix *problema + mètode + resultat* i deixar el catàleg al cap. 4. No és un error; és gust.



### Forma / maquetació

- Encara hi ha `\texttt` llargs que desborden (sobretot annex A i alguna línia del cap. 5). No tomba la nota; queda matusser a la impressió.
- `metadata.tex`: data «agost de 2026» vs preus d’API de l’**1/09/2026** i cap. 6 del **31/08**. Unifica convocatòria/data de lliurament quan tinguis la de la secretaria.
- Portada pròpia del `.tex` **no existeix** (acordat). El PDF actual comença pel resum: a uns centres està bé com a *cos*; **no** és el PDF de dipòsit.
- No hi ha dedicatòria, agraïments ni declaració d’autoria en aquest `.tex`. Si la guia del màster els demana, van a la **plantilla oficial**, no cal inventar-los aquí.

---



## 3. Per capítol: preguntes típiques i forats



### Front (resum, índexs, acrònims)


| Estat                             | Forat                                                                                           |
| --------------------------------- | ----------------------------------------------------------------------------------------------- |
| Resum CA + Abstract EN + keywords | D*ata del resum encara 31/08; el cap. 7 ja és 01/09. Actualitzar una línia el* dia del dipòsit. |
| Acrònims útils                    | Falta **SSE** ja hi és; es podria afegir **p50**, **MoSCoW**, **GDPR** ja hi és. Opcional.      |




### Cap. 1 — Introducció

Aguanta: problema, contribucions, O1–O6, no-abast, Gantt, 390 h.

**Pregunta dura:** «O1–O6 són SMART?» Són objectius d’*implementació* amb criteri d’acceptació (ruta + test). No tenen indicador numèric excepte O6. **Resposta:** en un TFM de sistema això és estàndard; no els reescrivis a «augmentar NDCG un 12 %» sense mesura.

**Forat menor:** «19 commits / 390 h» convencerà si a la defensa expliques que són *entregues grans*. No cal una taula nova.

### Cap. 2 — Estat de l’art

Aguanta. El forat clàssic («només productes») ja no aplica.

**Pregunta dura:** «Heu *llegit* Lost in the Middle / RAGAS o només els citeu?» Has de poder dir en 20 s què en treus (chunk massa llarg; fidelitat no mesurada).

**No afegir:** LangChain vs LlamaIndex, 15 frameworks més.

### Cap. 3 — Requisits

Aguanta: actors, cas d’ús, RF MoSCoW, RNF, errors, traçabilitat.

**Pregunta dura:** «On són els casos d’ús alternatius / UML complet?» Tens un diagrama de casos d’ús. Si el centre és molt UPM-clàssic, poden voler un cas d’ús *textual* més formal (actor, pre, flux alternatiu). Ja n’hi ha un paràgraf de xat; no cal un capítol extra.

### Cap. 4 — Arquitectura

Aguanta: hexàgon, confiança, E-R, retrieval, decisions.

**Pregunta dura:** «El worker dins FastAPI no és hexagonal / no escala.» Ja està al cap. 5 i a conclusions. Tingues la frase: *simple per al TFM, fràgil en producció*.

### Cap. 5 — Desenvolupament

Aguanta: pipeline 6 etapes, cua, xat/SSE, SM-2.

**Estil:** és el capítol més «guia del repo». Un tribunal simpàtic ho llegeix; un d’impacient salta a figures. No l’inflis.

### Cap. 6 — Resultats (**punt feble científic, fort d’honestedat**)

Això és on es juga la nota d’«avaluació».


| El que tens                                   | El que preguntaran                                                                                                                                               |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 61 pytest, ruff, mypy, 4 Vitest, 2 Playwright | «Per què tan pocs tests de frontend?» — 4 Vitest vs 61 backend. Resposta honesta: fumada E2E; UI coberta per smoke + captures. No prometis cobertura de pàgines. |
| n = 8 consultes, 1 corpus, 1 operador         | «Això no és estadística.» Correcte. p50 descriptiu, no inferència.                                                                                               |
| Sense rellevància / nDCG / recall             | Declarat. No ho afegeixis sense anotar.                                                                                                                          |
| Híbrid vs híbrid+rerank, no vs dens           | El CLI no té dens-only. No diguis que l’híbrid «és millor».                                                                                                      |
| max 3991 ms = cold start                      | Ja explicat; a la defensa insisteix-hi.                                                                                                                          |


**No mesurar groundedness ara** només per omplir: sense protocol és pitjor.

### Cap. 7 — Gestió / ètica / cost

Aguanta després de la reescriptura. Ja no és genèric.

**Pregunta dura:** «Això és un dictamen GDPR?» No. Ho diu el text. Formulari UPC/centre, si n’hi ha, **a part**.

### Cap. 8 — Conclusions

Aguanta: O1–O5 tancats, O6 parcial, futur lligat a límits.

**Estil:** l’últim paràgraf de conclusions encara «ensenya» al tribunal («a la defensa cal dir…»). Pots deixar-ho: és útil. Si vols un to més acadèmic, canvia-ho a «el límit d’aquest treball és…» sense tutelar el lector.

### Bibliografia

~21 cites APA, papers del cap. 2 + docs de stack. Suficient per a un TFM d’enginyeria. No inflar.

### Annexos

A (desplegament), B (API), C (avaluació): el mínim que un membre pot demanar per reproduir. L’annex A encara té línies `\texttt` que desborden: polish barat si queda una tarda.

---



## 4. Què falta de veritat (prioritat)



### Bloqueja el dipòsit (has de fer-ho)

1. **Portada institucional** del centre (CA+EN si la demanen) + unir-la al PDF **al final**.
2. Omplir **autor, tutor, universitat, màster, convocatòria, ciutat** (`metadata.tex`: fet 20/09). Encara cal la **portada institucional EPS** i comprovar la convocatòria amb secretaria.
3. **Declaració d’autoria / originalitat** si la guia la demana (plantilla, no aquest `.tex`).
4. **Formulari d’ètica / sostenibilitat** si el centre el té (UPC i similars). El cap. 7 no el substitueix.
5. Comprovar la **guia del teu màster**: extensió, Times 12, dos cares, traducció d’intro+conclusions a l’anglès (UCM), Gantt obligatori (ja el tens), IEEE vs APA.



### Millora la nota o evita un «però» (opcional, barat)


| Acció                                                | Per què           | No facis                     |
| ---------------------------------------------------- | ----------------- | ---------------------------- |
| Unificar dates (agost vs 1/09) al resum i `metadata` | Coherència formal | Reexecutar tot el benchmark  |
| ½ pàgina d’agraïments si el centre els espera        | Forma             | Un capítol d’agraïments      |
| Retallar 4–5 «no és X» a intro/conclusió             | Estil             | Reescriure caps. 3–6         |
| Trencar `\texttt` de l’annex A                       | Maquetació        | Canviar el contingut         |
| Guió de demo 5 min (paper, no `.tex`)                | Defensa           | Un capítol «manual d’usuari» |




### No falta (no ho afegeixis)

- Baseline «només dens» sense canviar el CLI i mesurar.
- Groundedness / RAGAS sobre el corpus sense protocol d’anotació.
- Estudi amb *n* alumnes.
- Més captures.
- Catàleg LangChain/LlamaIndex.
- Segona taula de productes.
- Inflar Vitest amb tests cosmètics la setmana del dipòsit.
- Tesi de negoci o SLA.

---



## 5. Defensa: 8 preguntes que has de poder contestar en 30 s

1. **Què aporta això que no faci NotebookLM + Anki?** Integració oberta, aïllament RLS, pipeline auditable, biblioteca persistent, SM-2 al domini; no un ranking de producte.
2. **Com sabeu que no al·lucina?** No ho «sabem» amb mètrica. Reduïm superfície (context, cites, prompt). Groundedness obert.
3. **Per què híbrid i no només embeddings?** Apunts = paràfrasi *i* termes rars / números. Sense nDCG; argument de disseny + literatura.
4. **El p50 369 ms demostra qualitat?** No: demostra latència en *aquest* corpus. Constructe dit al cap. 6.
5. **On van els PDF?** Storage; a l’LLM només *k* chunks del context. No «els apunts no surten mai».
6. **9.750 € vs 0,16 USD?** Dues factures: hores acadèmiques vs tokens. No barrejar.
7. **Per què SM-2 i no FSRS?** Auditabilitat al domini; FSRS citat i deixat fora.
8. **Això escala a producció?** No com està: worker dins l’API, rate limit inexistent, Supabase pausable. Dit al cap. 8.

**Demo (5 min, fora de la memòria):** PDF *Listo* → xat amb cita oberta → quiz → planner SM-2. Si falla la xarxa, les captures del cap. 6 són el pla B.

---



## 6. Ordre de tancament

1. Llegir la **guia oficial** del teu centre (una tarda). Marca APA vs IEEE, abstract, ètica, portada, extensió.
2. Omplir **metadades** + plantilla de portada (sense tocar el cos).
3. Unificar **data de lliurament** al resum/`metadata`.
4. (Opcional) polish estil + annex A.
5. **Unir** portada + `tfmbody.pdf` → PDF de dipòsit.
6. Guió de demo + assaig de les 8 preguntes.

El cos tècnic, **no el reobris** tret que el director o la rúbrica demanin una peça concreta (p. ex. intro en anglès).