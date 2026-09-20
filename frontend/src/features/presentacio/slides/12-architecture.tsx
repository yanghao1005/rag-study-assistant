import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function ArchitectureSlide() {
  return (
    <Slide notes="50 s. Hexàgon, no metàfora buida: entrypoints / ports+casos d'ús / adapters. El worker és una porta al mateix FastAPI, no el nucli. Gemini = canviar l'adapter de la dreta.">
      <Kicker>Disseny · arquitectura</Kicker>
      <Title>El nucli no coneix HTTP.</Title>
      <Lede>Arquitectura hexagonal: portes, casos d’ús, adapters. El domini no fa I/O.</Lede>
      <div className="tfm-arch">
        <Frag className="tfm-arch-box">
          <span>Entrypoints</span>
          <strong>Tres portes</strong>
          <p>HTTP, CLI i worker. El worker viu al mateix FastAPI: simple al TFM, fràgil en producció.</p>
        </Frag>
        <span className="tfm-arch-arrow" aria-hidden>
          →
        </span>
        <Frag className="tfm-arch-box is-mid">
          <span>Nucli</span>
          <strong>Ports i casos d’ús</strong>
          <p>Cercar, escriure, SM-2. No importa FastAPI ni OpenAI. Es testa amb fakes.</p>
        </Frag>
        <span className="tfm-arch-arrow" aria-hidden>
          →
        </span>
        <Frag className="tfm-arch-box">
          <span>Adapters</span>
          <strong>Postgres i LLM</strong>
          <p>Supabase, Storage, gpt-4.1-mini. Canviar a Gemini no reescriu el xat.</p>
        </Frag>
      </div>
    </Slide>
  );
}
