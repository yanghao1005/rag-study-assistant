import { Frag, Kicker, Slide, Title } from "../ui";

export function RagConfigSlide() {
  return (
    <Slide notes="25 min: salta (una frase a #/30: rerank OFF). Rerank: un LLM rellegeix. Agentic: una reescriptura. Tots dos OFF per defecte.">
      <Kicker>RAG · què està encès</Kicker>
      <Title>El camí per defecte, sense extres cars.</Title>
      <Frag className="tfm-table">
        <table>
          <thead>
            <tr>
              <th>Peça</th>
              <th>Estat</th>
              <th>Per què</th>
            </tr>
          </thead>
          <tbody>
            <tr className="is-hl">
              <td>Híbrid (significat + paraules + RRF)</td>
              <td>sempre</td>
              <td>Paràfrasi i còpia del PDF</td>
            </tr>
            <tr className="is-hl">
              <td>Intent (resum / capítol / fet)</td>
              <td>sempre</td>
              <td>Abans de cercar</td>
            </tr>
            <tr className="is-hl">
              <td>Sinopsi del PDF</td>
              <td>defecte ON</td>
              <td>Preguntes àmplies</td>
            </tr>
            <tr>
              <td>Rerank LLM / agentic</td>
              <td>defecte OFF</td>
              <td>Un LLM extra: lent i car</td>
            </tr>
          </tbody>
        </table>
      </Frag>
    </Slide>
  );
}
