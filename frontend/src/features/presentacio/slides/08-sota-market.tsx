import { Frag, Kicker, Slide, Title } from "../ui";

export function SotaMarketSlide() {
  return (
    <Slide notes="45 s. Taula fila a fila. ChatGPT: PDF sí, cicle no. Anki: calendari sense apunts. NotebookLM: cites, poc repàs. PaperQA si pregunten: papers, no flashcards.">
      <Kicker>Mercat · comparativa</Kicker>
      <Title>Cada sistema tanca un tros.</Title>
      <Frag className="tfm-table is-tight">
        <table>
          <thead>
            <tr>
              <th />
              <th>PDF propis</th>
              <th>Cites</th>
              <th>Pràctica</th>
              <th>Repàs</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>ChatGPT + fitxers</td>
              <td>sí</td>
              <td>dèbil</td>
              <td>no</td>
              <td>no</td>
            </tr>
            <tr>
              <td>Anki</td>
              <td>no natiu</td>
              <td>no</td>
              <td>sí</td>
              <td>SM-2</td>
            </tr>
            <tr>
              <td>NotebookLM</td>
              <td>sí</td>
              <td>sí</td>
              <td>limitat</td>
              <td>no</td>
            </tr>
            <tr className="is-hl">
              <td>Studyraft</td>
              <td>sí</td>
              <td>sí</td>
              <td>sí</td>
              <td>SM-2</td>
            </tr>
          </tbody>
        </table>
      </Frag>
      <Frag as="p" className="tfm-lede is-wide">
        L’oportunitat: el cicle sencer, sobre apunts teus, amb calendari.
      </Frag>
    </Slide>
  );
}
