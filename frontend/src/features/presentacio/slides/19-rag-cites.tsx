import { Frag, Kicker, Slide, Title } from "../ui";

export function RagCitesSlide() {
  return (
    <Slide notes="Lecture-focused = el retriever no consulta la web. Prompt: «Answer using only the provided context. If the context is insufficient, say so. Cite sources as [n].» Això redueix invenció; no mesura groundedness.">
      <Kicker>RAG · cites</Kicker>
      <Title>Fitxer, pàgines i fragment.</Title>
      <div className="tfm-cites">
        <Frag className="tfm-cite">
          <span>01</span>
          <strong>Fitxer</strong>
          <p>Quin PDF</p>
        </Frag>
        <Frag className="tfm-cite">
          <span>02</span>
          <strong>Pàgines</strong>
          <p>On és</p>
        </Frag>
        <Frag className="tfm-cite">
          <span>03</span>
          <strong>Fragment</strong>
          <p>El text citat</p>
        </Frag>
      </div>
      <Frag as="p" className="tfm-lede is-wide">
        Prompt: only the provided context. Cite [n]. Auditable; no és mètrica de fidelitat.
      </Frag>
    </Slide>
  );
}
