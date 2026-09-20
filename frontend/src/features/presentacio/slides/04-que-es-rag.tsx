import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function QueEsRagSlide() {
  return (
    <Slide notes="45 s. Lewis 2020. Llegeix les dues columnes. Gao és la següent: el retriever mana.">
      <Kicker>Disseny · la IA</Kicker>
      <Title>Buscar al PDF. Després escriure.</Title>
      <Lede>
        RAG = Retrieval-Augmented Generation (Lewis 2020): recuperació + generació. L&apos;LLM és el model
        que escriu.
      </Lede>
      <div className="tfm-compare">
        <Frag as="article">
          <span>Sense RAG</span>
          <strong>Només paràmetres</strong>
          <p>Pregunta → LLM. El model no ha vist <em>aquest</em> PDF. Si inventa, no s’audita.</p>
        </Frag>
        <Frag as="article" className="is-hl">
          <span>Amb RAG</span>
          <strong>Context extern</strong>
          <p>Pregunta → fragments recuperats → LLM. La resposta ha de sortir d’aquest context.</p>
        </Frag>
      </div>
    </Slide>
  );
}
