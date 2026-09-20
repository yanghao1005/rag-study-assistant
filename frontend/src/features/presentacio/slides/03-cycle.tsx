import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function CycleSlide() {
  return (
    <Slide notes="50 s. Quatre baules, una frase cadascuna. Indexar/recuperar = RAG. Generar = xat o cartes. Repassar = SM-2, 1 dia si falles.">
      <Kicker>Motivació · el cicle</Kicker>
      <Title>Quatre baules encadenades.</Title>
      <Lede>Indexar, recuperar, generar, repassar. Un sistema, no un xat.</Lede>
      <div className="tfm-cycle">
        <Frag className="tfm-step">
          <span>01</span>
          <strong>Indexar</strong>
          <p>Trossejar el PDF</p>
        </Frag>
        <Frag className="tfm-step">
          <span>02</span>
          <strong>Recuperar</strong>
          <p>Trobar el fragment</p>
        </Frag>
        <Frag className="tfm-step">
          <span>03</span>
          <strong>Generar</strong>
          <p>Resposta o cartes</p>
        </Frag>
        <Frag className="tfm-step">
          <span>04</span>
          <strong>Repassar</strong>
          <p>Calendari SM-2</p>
        </Frag>
      </div>
    </Slide>
  );
}
