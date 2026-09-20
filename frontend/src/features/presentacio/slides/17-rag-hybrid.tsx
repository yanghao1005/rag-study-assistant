import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function RagHybridSlide() {
  return (
    <Slide notes="50 s. No reexpliquis embedding. RRF: 1/(60+posició), k=60 Cormack. El bench va mesurar k=10 al CLI (#/38); el producte deixa 8. Rerank OFF. No dens-only.">
      <Kicker>RAG · híbrid</Kicker>
      <Title>Vint densos, vint lèxics, vuit al prompt.</Title>
      <Lede>
        RRF (Reciprocal Rank Fusion): qui surt amunt a les dues llistes, puja. Al prompt en deixem 8, no
        20: un context llarg perd el fet al mig.
      </Lede>
      <div className="tfm-flow">
        <Frag className="tfm-flow-row">
          <span className="tfm-chip">Pregunta</span>
          <span className="tfm-arrow">→</span>
          <span className="tfm-chip">Intent</span>
          <span className="tfm-arrow">→</span>
          <span className="tfm-chip">20 dens + 20 text</span>
          <span className="tfm-arrow">→</span>
          <span className="tfm-chip">RRF</span>
          <span className="tfm-arrow">→</span>
          <span className="tfm-chip">8 al LLM</span>
        </Frag>
      </div>
      <Frag as="p" className="tfm-formula">
        puntuació = Σ 1 / (<b>60</b> + posició)
      </Frag>
    </Slide>
  );
}
