import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function PlanSlide() {
  return (
    <Slide notes="60 s. Git: des 2025–ago 2026, pauses març i juny, tall 8/07 hexagonal. 390 h × 25 € = 9.750 €, oportunitat, no factura. API sostre 1/09/2026: embedding-3-small, gpt-4.1-mini, 0,002 $/pregunta, 0,16 $/100. No negoci.">
      <Kicker>Gestió · pla i diners</Kicker>
      <Title>Hores d’una banda. Tokens de l’altra.</Title>
      <Lede>390 h × 25 € = 9.750 €. L’API d’un estudiant, sobre aquest corpus, són cèntims.</Lede>
      <div className="tfm-cards">
        <Frag as="article" className="tfm-card">
          <span>des – mai</span>
          <strong>Prototip</strong>
          <p>LangChain. Es va arxivar: no es podia testar sense claus.</p>
        </Frag>
        <Frag as="article" className="tfm-card">
          <span>juliol</span>
          <strong>Hexàgon</strong>
          <p>75 h. Esquema, ports, API. El nucli actual.</p>
        </Frag>
        <Frag as="article" className="tfm-card">
          <span>agost</span>
          <strong>Producte + memòria</strong>
          <p>UI del cicle, planner, LaTeX. 9.750 € no és una factura.</p>
        </Frag>
      </div>
      <Frag as="p" className="tfm-arch-why">
        0,16 $ / 100 preguntes (sostre). Recerca, no explotació. Rerank apagat.
      </Frag>
    </Slide>
  );
}
