import { Kicker, Lede, Meta, Slide, Title } from "../ui";

export function CoverSlide() {
  return (
    <Slide notes="Cronòmetre: 20 min xerrada + 5 demo = 25, topall 30. Portades 10 s. Motivació 2. Objectius 1,5. Mercat 2. Disseny ~10: no saltis Gao #/18, chunks #/20, ingestió #/21, híbrid #/23, SM-2 #/27. Demo 5. Avaluació #/37–#/39 (tests, p50, límits). Pla #/41 1 min. Futur #/43 + tancament #/44. Salta captures #/31–#/35 si la demo viu. N = notes.">
      <Kicker>Treball de Fi de Màster · EPS · Universitat de Lleida</Kicker>
      <Title as="h1">Studyraft</Title>
      <Lede>Assistent d’estudi RAG sobre documents propis. Un cicle, no un xat.</Lede>
      <Meta>
        <strong>Hao Yang</strong>
        <br />
        Màster universitari en Enginyeria Informàtica
        <br />
        Director: Jordi Planes Cid · setembre 2026
      </Meta>
    </Slide>
  );
}
