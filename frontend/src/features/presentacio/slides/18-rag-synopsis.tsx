import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function RagSynopsisSlide() {
  return (
    <Slide notes="25 min: salta. Jeràrquic: 4–6 frases del document. No és un agent.">
      <Kicker>RAG · sinopsi</Kicker>
      <Title>Un resum del PDF, no només una frase veïna.</Title>
      <Lede>En pujar, un LLM escriu 4–6 frases del document. «De què va el tema?» llegeix el temari, no una sola diapositiva.</Lede>
      <Frag as="p" className="tfm-lede">
        Si es desactiva, els chunks continuen sent vàlids. No és un agent.
      </Frag>
    </Slide>
  );
}
