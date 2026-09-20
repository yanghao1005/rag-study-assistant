import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function ArchFlowSlide() {
  return (
    <Slide notes="40 s. Camina les tres caixes. El navegador no truca OpenAI. El cas d'ús demana fragments per user_id; l'adapter executa.">
      <Kicker>Disseny · una pregunta</Kicker>
      <Title>La pregunta passa pel cas d’ús.</Title>
      <Lede>Next.js no parla amb ChatGPT. El calendari SM-2 no el decideix el model.</Lede>
      <div className="tfm-arch">
        <Frag className="tfm-arch-box">
          <span>Porta HTTP</span>
          <strong>Tu preguntes</strong>
          <p>L’app envia el text amb el JWT. El servidor comprova qui ets.</p>
        </Frag>
        <span className="tfm-arch-arrow" aria-hidden>
          →
        </span>
        <Frag className="tfm-arch-box is-mid">
          <span>Cas d’ús</span>
          <strong>8 trossos, després escriu</strong>
          <p>No diu «crida OpenAI». Demana fragments d’aquest usuari via un port.</p>
        </Frag>
        <span className="tfm-arch-arrow" aria-hidden>
          →
        </span>
        <Frag className="tfm-arch-box">
          <span>Adapters</span>
          <strong>Cerca i redacta</strong>
          <p>pgvector + FTS. L’LLM escriu. Torna el text amb [1] [2].</p>
        </Frag>
      </div>
    </Slide>
  );
}
