import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function GroundednessLimitSlide() {
  return (
    <Slide notes="50 s. Groundedness = cada frase al tros? No ho mesurem. Sí: prompt tancat (peu), cites, sense web. Un % sense jutge no es defensa.">
      <Kicker>Disseny · fidelitat</Kicker>
      <Title>Recuperar no prova la frase.</Title>
      <Lede>
        Groundedness: cada frase és al tros? No ho mesurem. Sí que tanquem el prompt al context.
      </Lede>
      <div className="tfm-compare">
        <Frag as="article" className="is-hl">
          <span>El que sí</span>
          <strong>Limitar la invenció</strong>
          <p>Només els 8 trossos. Cites [n]. No busquem a internet.</p>
        </Frag>
        <Frag as="article">
          <span>El que no</span>
          <strong>Un percentatge</strong>
          <p>Sense jutge ni rúbrica, un número de fidelitat no es pot defensar.</p>
        </Frag>
      </div>
      <Frag as="p" className="tfm-arch-why">
        Prompt: només el context; si no n’hi ha prou, dir-ho; citar [n].
      </Frag>
    </Slide>
  );
}
