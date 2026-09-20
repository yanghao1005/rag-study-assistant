import { Frag, Kicker, Slide, Title } from "../ui";

export function EvalTestsSlide() {
  return (
    <Slide notes="Zero *errors* ruff/mypy (77 fitxers). tsc --noEmit OK 31/08. Vitest = contractes de client, no cada pantalla. Playwright = landing i login, sí a la CI del frontend; no executa xat ni RAG. E5 el demostra la demo.">
      <Kicker>Avaluació · programari</Kicker>
      <Title>Es prova com a sistema.</Title>
      <div className="tfm-metrics">
        <Frag className="tfm-metric">
          <b>63</b>
          <span>pytest · 1/09</span>
        </Frag>
        <Frag className="tfm-metric">
          <b>0</b>
          <span>errors ruff / mypy</span>
        </Frag>
        <Frag className="tfm-metric">
          <b>4</b>
          <span>Vitest · contractes</span>
        </Frag>
        <Frag className="tfm-metric">
          <b>2</b>
          <span>Playwright smoke</span>
        </Frag>
      </div>
      <Frag as="p" className="tfm-lede is-wide">
        Quatre Vitest no cobreixen cada pantalla. Playwright smoke sí és a la CI; no executa el RAG.
      </Frag>
    </Slide>
  );
}
