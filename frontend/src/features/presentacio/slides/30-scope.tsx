import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function ScopeSlide() {
  return (
    <Slide notes="40 s. Dins / fora. No recitis taules. Groundedness es mesura o no a #/25, no és no-abast de producte.">
      <Kicker>Objectius · abast</Kicker>
      <Title>Què entra. Què no.</Title>
      <Lede>El detall és a la memòria. Aquí, el perímetre.</Lede>
      <div className="tfm-compare">
        <Frag as="article" className="is-hl">
          <span>Dins</span>
          <strong>El MVP</strong>
          <p>PDF amb text extraïble. Un estudiant. OpenAI o Gemini. Docker local. UI en castellà de tu.</p>
        </Frag>
        <Frag as="article">
          <span>Fora</span>
          <strong>No és aquest TFM</strong>
          <p>OCR, visor PDF, export Anki, tutor ITS, estudi amb alumnes, producció multiregió.</p>
        </Frag>
      </div>
    </Slide>
  );
}
