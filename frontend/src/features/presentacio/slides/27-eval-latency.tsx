import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function EvalLatencySlide() {
  return (
    <Slide notes="p50 = mediana. n=8, un operador (l’autor), apunts propis, només factuals: no és inferència. El rerank puja 369 → 1608 ms. k=10 al CLI, k=8 al producte. 369 ms = embedding + híbrid, no el xat. Max híbrid = fred; rerank mesurat calent: es compara el p50.">
      <Kicker>Avaluació · latència · 31/08/2026</Kicker>
      <Title>La mediana apaga el rerank.</Title>
      <Lede className="is-wide">
        p50 = mediana. 8 factuals, 114 chunks, un operador (l’autor, apunts propis). k = 10 al CLI; 8 al
        producte.
      </Lede>
      <Frag className="tfm-table">
        <table>
          <thead>
            <tr>
              <th>Política</th>
              <th>p50</th>
              <th>max</th>
            </tr>
          </thead>
          <tbody>
            <tr className="is-hl">
              <td>Híbrid (RRF)</td>
              <td>369 ms</td>
              <td>3991 ms</td>
            </tr>
            <tr>
              <td>Híbrid + rerank LLM</td>
              <td>1608 ms</td>
              <td>2745 ms</td>
            </tr>
          </tbody>
        </table>
      </Frag>
      <Frag as="p" className="tfm-arch-why">
        3991 ms = fred. Es compara el p50, no el max. No és el xat.
      </Frag>
    </Slide>
  );
}
