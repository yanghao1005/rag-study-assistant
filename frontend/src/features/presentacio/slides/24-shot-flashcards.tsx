import { Kicker, Slide, Title } from "../ui";

export function ShotFlashcardsSlide() {
  return (
    <Slide notes="25 min: salta si la demo viu. Conjunts amb títol, editables.">
      <Kicker>Xarxa · pràctica</Kicker>
      <Title>Biblioteca persistent.</Title>
      <figure className="tfm-shot">
        <img src="/presentacio/07-flashcards.png" alt="Biblioteca de flashcards" />
      </figure>
    </Slide>
  );
}
