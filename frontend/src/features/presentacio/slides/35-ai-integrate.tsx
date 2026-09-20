import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function AiIntegrateSlide() {
  return (
    <Slide notes="40 s. Significat + paraules. La fórmula 20+20→8 és a #/23. Rerank OFF. Fidelitat a #/25.">
      <Kicker>Disseny · la IA</Kicker>
      <Title>Cercar de dues maneres. Citar sempre.</Title>
      <Lede>No enviem el PDF sencer. Vuit trossos al prompt, amb fitxer i pàgina.</Lede>
      <div className="tfm-cards">
        <Frag as="article" className="tfm-card">
          <span>Significat</span>
          <strong>Paràfrasi</strong>
          <p>L’estudiant pregunta amb les seves paraules. El vector enganxa el concepte.</p>
        </Frag>
        <Frag as="article" className="tfm-card">
          <span>Paraules</span>
          <strong>Còpia del PDF</strong>
          <p>Sigles i títols tal com surten a l’apunt. Postgres FTS, no un cercador web.</p>
        </Frag>
        <Frag as="article" className="tfm-card">
          <span>Evidència</span>
          <strong>Fitxer · pàgina · [n]</strong>
          <p>El model només escriu amb el context. Rerank apagat: menys cost i menys espera.</p>
        </Frag>
      </div>
      <Frag as="p" className="tfm-arch-why">
        Postgres FTS, no BM25. La fusió RRF (20+20→8) és a la diapo següent.
      </Frag>
    </Slide>
  );
}
