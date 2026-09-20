import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function CostSlide() {
  return (
    <Slide notes="Tres comptes. 9.750 € = 390 h × 25 €, dedicació Git, no factura. Models: embedding-3-small i gpt-4.1-mini. 0,16 USD = 100 preguntes/mes, sostre 1/09/2026. No barregeu hores i API. No és dictamen GDPR.">
      <Kicker>Gestió · tres comptes</Kicker>
      <Title>No barregeu hores i tokens.</Title>
      <Lede>
        390 h són estimació Git, no un timesheet. L’API d’un estudiant, sobre aquest corpus, són cèntims.
      </Lede>
      <div className="tfm-metrics tfm-metrics-3">
        <Frag className="tfm-metric">
          <b>390 h</b>
          <span>dedicació · 9.750 €</span>
        </Frag>
        <Frag className="tfm-metric">
          <b>0,16 $</b>
          <span>100 preguntes / mes</span>
        </Frag>
        <Frag className="tfm-metric">
          <b>0,002 $</b>
          <span>una pregunta (sostre)</span>
        </Frag>
      </div>
      <Frag as="p" className="tfm-lede is-wide">
        Models: embedding-3-small i gpt-4.1-mini. Sostre 1/09/2026. Allotjament pausable; no dictamen GDPR.
      </Frag>
    </Slide>
  );
}
