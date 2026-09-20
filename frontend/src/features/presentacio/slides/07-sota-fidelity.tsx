import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function SotaFidelitySlide() {
  return (
    <Slide notes="Al·lucinar = afirmar amb fluïdesa el que no és als apunts. Groundedness = fidelitat: cada frase de la resposta ha d’estar al fragment recuperat. Recuperar el chunk bo no impedeix que l'LLM inventi la xifra del costat.">
      <Kicker>Fidelitat · groundedness</Kicker>
      <Title>Recuperar no prova la frase.</Title>
      <Lede>
        <em className="tfm-hl">Groundedness</em>: cada afirmació de la resposta ha d’estar al context
        recuperat. Al·lucinar és escriure fluïdament el que no hi és.
      </Lede>
      <div className="tfm-compare">
        <Frag as="article">
          <span>Al context</span>
          <strong>El chunk diu A</strong>
          <p>«El capítol 2 tracta de grafs.» Això és el que s’ha recuperat.</p>
        </Frag>
        <Frag as="article" className="is-hl">
          <span>No grounded</span>
          <strong>La resposta diu B</strong>
          <p>«El capítol 2 tracta de xarxes neuronals.» Fluida, i no és al fragment.</p>
        </Frag>
      </div>
    </Slide>
  );
}
