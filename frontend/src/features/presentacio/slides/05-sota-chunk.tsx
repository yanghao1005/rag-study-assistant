import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function SotaChunkSlide() {
  return (
    <Slide notes="40 s. Chunk = tros indexable. 1200 caràcters, solapament 150. Lost in the Middle (Liu): un tros massa llarg, el model ignora el mig. Per això k=8 al prompt. Sense OCR.">
      <Kicker>Disseny · chunk</Kicker>
      <Title>Un chunk és un tros del PDF.</Title>
      <Lede>
        El model no llegeix el fitxer sencer. El talla en trossos que es solapen 150 caràcters, perquè una
        definició no quedi partida. Màxim 1200. Sense OCR.
      </Lede>
      <Frag className="tfm-chunks-vis">
        <div className="tfm-chunk-bar">
          Chunk 1<small>p. 12</small>
        </div>
        <div className="tfm-chunk-bar">
          Chunk 2<small>solapament 150</small>
        </div>
        <div className="tfm-chunk-bar">
          Chunk 3<small>p. 13</small>
        </div>
      </Frag>
    </Slide>
  );
}
