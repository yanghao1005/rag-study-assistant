import { Card, Kicker, Lede, Slide, Title } from "../ui";

export function SotaRagSlide() {
  return (
    <Slide notes="45 s. Gao et al. 2024 = survey (arXiv:2312.10997), no un algoritme. Lewis bateja RAG; Gao: el retriever mana; la fluïdesa amaga al·lucinacions. Per això no perseguim un LLM fronterer.">
      <Kicker>Disseny · Gao 2024</Kicker>
      <Title>Gao 2024: el retriever mana.</Title>
      <Lede>
        Gao et al. és una enquesta de RAG per a LLM. No un model nou. Lewis 2020 bateja el patró; Gao
        diu on falla.
      </Lede>
      <div className="tfm-cards">
        <Card label="Què és" title="Un survey">
          Recull com es munten els RAG. No proposa un algoritme que implementem.
        </Card>
        <Card label="Retriever" title="Els fragments">
          Si recuperes malament, un model gros no ho salva. Per això no perseguim un LLM fronterer.
        </Card>
        <Card label="Fluïdesa" title="No és prova">
          Avaluar si «sona bé» amaga al·lucinacions ben escrites. Cal el fragment, no només l’estil.
        </Card>
      </div>
    </Slide>
  );
}
