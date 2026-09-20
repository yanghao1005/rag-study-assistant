import { Card, Kicker, Lede, Slide, Title } from "../ui";

export function RagPhasesSlide() {
  return (
    <Slide notes="25 min: salta. El mateix índex alimenta xat, flashcards i quiz: ja es veu a la demo.">
      <Kicker>RAG · Studyraft</Kicker>
      <Title>El mateix índex per preguntar i practicar.</Title>
      <Lede>Des d’aquí, el sistema. Ja no definim RAG: mostrem què fa aquest producte.</Lede>
      <div className="tfm-split">
        <Card label="En pujar" title="Construir l’índex">
          Parse, chunks (vector + FTS) i sinopsi de 4–6 frases. Fora de l’HTTP.
        </Card>
        <Card label="En preguntar" title="Consultar l’índex">
          Intent, híbrid, cites. El PDF no es reenvia. El quiz fa el mateix camí.
        </Card>
      </div>
    </Slide>
  );
}
