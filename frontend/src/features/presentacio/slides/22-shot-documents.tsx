import { Kicker, Slide, Title } from "../ui";

export function ShotDocumentsSlide() {
  return (
    <Slide notes="Salta si la demo viu. L’assignatura de la barra no és un corpus de paper.">
      <Kicker>Xarxa · documents</Kicker>
      <Title>Indexats. Listo.</Title>
      <figure className="tfm-shot">
        <img src="/presentacio/04-documents.png" alt="Documents indexats en estat Listo" />
      </figure>
    </Slide>
  );
}
