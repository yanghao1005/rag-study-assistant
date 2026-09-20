import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function RagAskSlide() {
  return (
    <Slide notes="La pregunta es vectoritza i es cerca a l’índex. En queden 8 fragments al prompt, no el PDF. L’LLm només veu aquests trossos i ha de citar [n]. Si el tros no hi és, ha de dir-ho.">
      <Kicker>RAG · una pregunta</Kicker>
      <Title>Vuit trossos al prompt. No el PDF.</Title>
      <Lede>
        El model no «obre» el fitxer. Li passem fragments recuperats i li diem: escriu només amb això.
      </Lede>
      <div className="tfm-ask">
        <Frag className="tfm-ask-col">
          <span>01 · Pregunta</span>
          <strong>Què és el potencial d’acció?</strong>
          <p>Es representa com a vector i com a paraules.</p>
        </Frag>
        <Frag className="tfm-ask-col">
          <span>02 · Índex</span>
          <strong>Els trossos més a prop</strong>
          <div className="tfm-mini-chunks">
            <b>[1] Apunts.pdf · p. 12</b>
            <b>[2] Apunts.pdf · p. 13</b>
            <b>[3] Tema3.pdf · p. 4</b>
          </div>
        </Frag>
        <Frag className="tfm-ask-col is-hl">
          <span>03 · LLM</span>
          <strong>Escriu i cita [n]</strong>
          <p>Resposta + [1] [2]. Si no n’hi ha prou, ho diu.</p>
        </Frag>
      </div>
    </Slide>
  );
}
