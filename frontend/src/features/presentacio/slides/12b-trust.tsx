import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function TrustSlide() {
  return (
    <Slide notes="40 s. El fitxer no va sencer a l’LLM: k=8 (resum fins a 12). Storage + prompt + user_id. Service role salta RLS: el backend ha de filtrar. No dictamen GDPR.">
      <Kicker>Disseny · seguretat</Kicker>
      <Title>El PDF no va a l&apos;LLM.</Title>
      <Lede>
        El fitxer queda al magatzem. A cada pregunta només surten k trossos cap al model. El backend
        usa service role: cal filtrar per usuari.
      </Lede>
      <div className="tfm-cards">
        <Frag as="article" className="tfm-card">
          <span>Storage</span>
          <strong>Els bytes</strong>
          <p>El fitxer queda al magatzem. No es reenvia sencer a cada pregunta.</p>
        </Frag>
        <Frag as="article" className="tfm-card">
          <span>Prompt</span>
          <strong>k fragments</strong>
          <p>Factual: 8. Un resum pot arribar a 12. No «els apunts no surten mai».</p>
        </Frag>
        <Frag as="article" className="tfm-card">
          <span>Qui veu què</span>
          <strong>RLS + filtre</strong>
          <p>Service role salta RLS. El cas d’ús filtra user_id. RLS cobreix el client directe.</p>
        </Frag>
      </div>
    </Slide>
  );
}
