import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function ItsHowSlide() {
  return (
    <Slide notes="ITS = Intelligent Tutoring System. Bucle: exercici → resposta → diagnosi del que no sap → següent item adaptat (AutoTutor / VanLehn). Studyraft talla al pas 4: no hi ha model de l’alumne. SM-2 només mou la data.">
      <Kicker>ITS · com funciona</Kicker>
      <Title>Un tutor que adapta el temari.</Title>
      <Lede>
        Intelligent Tutoring System: compara la resposta amb un model de què sap l’alumne. Nosaltres no.
      </Lede>
      <div className="tfm-steps4">
        <Frag as="article" className="tfm-card">
          <span>01</span>
          <strong>Exercici</strong>
          <p>El sistema presenta un problema del temari.</p>
        </Frag>
        <Frag as="article" className="tfm-card">
          <span>02</span>
          <strong>Resposta</strong>
          <p>L’alumne contesta. El tutor llegeix l’error, no només un 0/1.</p>
        </Frag>
        <Frag as="article" className="tfm-card">
          <span>03</span>
          <strong>Diagnosi</strong>
          <p>Actualitza el model: què no sap, quina concepció errònia.</p>
        </Frag>
        <Frag as="article" className="tfm-card is-out">
          <span>04 · Fora</span>
          <strong>Adaptar</strong>
          <p>El següent item depèn del forat. Studyraft no fa aquest pas.</p>
        </Frag>
      </div>
    </Slide>
  );
}
