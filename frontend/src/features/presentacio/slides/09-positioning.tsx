import { Card, Kicker, Lede, Slide, Title } from "../ui";

export function PositioningSlide() {
  return (
    <Slide notes="50 s. ITS = tutor que modela l’alumne. SM-2 = calendari. La fórmula és a #/27. No diagnostiquem.">
      <Kicker>Mercat · oportunitat</Kicker>
      <Title>SM-2, no un ITS.</Title>
      <Lede>ITS és un tutor. SM-2 és un calendari. No són el mateix.</Lede>
      <div className="tfm-cards">
        <Card label="ITS" title="Tutor intel·ligent">
          Intelligent Tutoring System: modela què sap l’alumne i adapta el temari. Nosaltres no.
        </Card>
        <Card label="SM-2" title="SuperMemo-2">
          Fórmula de 1990 (Anki la fa servir): si falles, la carta torna en 1 dia; si encertes, espera més.
        </Card>
        <Card label="Aquest TFM" title="Només el calendari">
          No diagnostiquem errors ni tutorem. RAG dóna el fragment; SM-2 decideix el dia.
        </Card>
      </div>
    </Slide>
  );
}
