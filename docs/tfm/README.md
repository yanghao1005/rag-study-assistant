# Memòria TFM (LaTeX)

Font de la memòria de **Studyraft** (assistent d'estudi RAG).
Guia de què redactar: [`ESTRUCTURA.md`](ESTRUCTURA.md).
Revisió amb ull de tribunal (què falta / què millorar): [`REVISIO-TRIBUNAL.md`](REVISIO-TRIBUNAL.md).
Defensa (deck): [`presentacio/REVISIO-TRIBUNAL.md`](presentacio/REVISIO-TRIBUNAL.md).

Cos en **català**.

## Compilar el PDF

Requisit: MiKTeX (aquest equip ja té `pdflatex`, `latexmk` i `biber`).

```powershell
cd docs\tfm
.\compile.ps1
```

El PDF queda a `docs/tfm/build/memoria.pdf`.

## Resum EPS (2 pàgines)

Plantilla oficial de dipòsit (`Resum-TFG-TFM-Nom-Cognoms.dot`): màxim 2 pàgines, dues columnes, Times New Roman.

```powershell
cd docs\tfm\resum-eps
.\compile.ps1
```

El PDF queda a `docs/tfm/build/Resum-TFG-TFM-Hao-Yang.pdf`. Dades de capçalera: `resum-eps/dades.tex`.

Manual:

```powershell
cd docs\tfm
latexmk -pdf -outdir=build main.tex
Copy-Item build\main.pdf build\memoria.pdf -Force
```

Neteja:

```powershell
latexmk -C -outdir=build main.tex
```

## Portada

La portada és la plantilla oficial EPS (`Portada-TFM-Nom-Cognoms.odt`), copiada a `front/portada-oficial.odt`. `compile.ps1` la converteix a PDF amb LibreOffice i `main.tex` l'inclou com a primera pàgina.
