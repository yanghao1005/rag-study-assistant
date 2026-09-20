import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function RagIngestSlide() {
  return (
    <Slide notes="50 s. La UI torna amb «en cua». Worker al mateix FastAPI: simple al TFM, fràgil en producció. Parse buit = error, no s’inventa OCR. Relançable per etapa.">
      <Kicker>Disseny · ingestió</Kicker>
      <Title>Sis etapes. Relançables.</Title>
      <Lede>
        Un worker (procés de fons) fa la feina lenta. Viu al mateix FastAPI: simple per al TFM, fràgil
        en producció.
      </Lede>
      <div className="tfm-pipeline">
        <Frag as="span" className="tfm-pipe">
          baixar
        </Frag>
        <Frag as="span" className="tfm-arrow">
          →
        </Frag>
        <Frag as="span" className="tfm-pipe">
          parse
        </Frag>
        <Frag as="span" className="tfm-arrow">
          →
        </Frag>
        <Frag as="span" className="tfm-pipe">
          trossejar
        </Frag>
        <Frag as="span" className="tfm-arrow">
          →
        </Frag>
        <Frag as="span" className="tfm-pipe">
          embedding
        </Frag>
        <Frag as="span" className="tfm-arrow">
          →
        </Frag>
        <Frag as="span" className="tfm-pipe">
          desar
        </Frag>
        <Frag as="span" className="tfm-arrow">
          →
        </Frag>
        <Frag as="span" className="tfm-pipe">
          sinopsi
        </Frag>
      </div>
      <Frag as="p" className="tfm-lede">
        Parse buit = error honest. Sense OCR. Cada etapa deixa traça.
      </Frag>
    </Slide>
  );
}
