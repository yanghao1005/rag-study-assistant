import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function RagIntentSlide() {
  return (
    <Slide notes="40 s. Tres camins abans de cercar. Factual: 8 chunks. Resum: sinopsis. Capítol: filtre pel número al nom del fitxer. No totes les preguntes són «què és X».">
      <Kicker>Disseny · intent</Kicker>
      <Title>Abans de cercar, què vol la pregunta.</Title>
      <Lede>No totes les preguntes són «què és X». El camí de cerca canvia.</Lede>
      <div className="tfm-cards">
        <Frag as="article" className="tfm-card">
          <span>Factual</span>
          <strong>Un concepte</strong>
          <p>Paraules + significat. En queden 8 chunks amb pàgina.</p>
        </Frag>
        <Frag as="article" className="tfm-card">
          <span>Resum</span>
          <strong>De què va</strong>
          <p>Es reescriu la consulta i s’hi posen sinopsis de document.</p>
        </Frag>
        <Frag as="article" className="tfm-card">
          <span>Capítol</span>
          <strong>Tema n</strong>
          <p>Filtre pel número al nom del fitxer, no un veí de «explica».</p>
        </Frag>
      </div>
    </Slide>
  );
}
