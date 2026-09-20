import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function SotaSignalsSlide() {
  return (
    <Slide notes="Embedding = vector de significat. FTS = full-text search a Postgres (tsvector), no un BM25 de Lucene; l’argument és el mateix: paraules literals. RRF = fusió de rànquings.">
      <Kicker>Recuperar · dos senyals</Kicker>
      <Title>Per significat i per paraules.</Title>
      <Lede>
        Un embedding és un vector de sentit. El lèxic és FTS de Postgres, no un BM25 de Lucene: cerca
        les paraules tal com surten al PDF.
      </Lede>
      <div className="tfm-signals">
        <Frag as="article" className="tfm-signal">
          <span>Dens</span>
          <strong>Significat</strong>
          <p>«Què és el potencial d’acció?» enganxa encara que no copiïs el PDF.</p>
        </Frag>
        <Frag as="article" className="tfm-signal">
          <span>Lèxic</span>
          <strong>Paraules</strong>
          <p>Sigles, fórmules, Na⁺, «tema 3». El que l’estudiant copia tal qual.</p>
        </Frag>
        <Frag as="article" className="tfm-signal">
          <span>RRF</span>
          <strong>Fusió</strong>
          <p>Uneix les dues llistes sense entrenar un model. Qui surt amunt a totes dues, puja.</p>
        </Frag>
      </div>
    </Slide>
  );
}
