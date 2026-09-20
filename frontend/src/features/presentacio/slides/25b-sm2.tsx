import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function Sm2Slide() {
  return (
    <Slide notes="50 s. Explica la línia de fallada: 1 dia, no «avui». UI: de nou=1, difícil=3, bé=4, fàcil=5. No és un ITS: no diagnostica. La demo després ho ensenya.">
      <Kicker>Disseny · SM-2</Kicker>
      <Title>El calendari s’allarga si encertes.</Title>
      <Lede className="is-wide">
        SM-2 = SuperMemo-2 (Wozniak 1990). No tutora: només decideix <em>quin dia</em> torna la carta.
      </Lede>
      <div className="tfm-timeline">
        <Frag className="tfm-time is-fail">
          <span>Fallada q &lt; 3</span>
          <b>1 dia</b>
          <p>Repeticions a 0. A la UI, «de nou».</p>
        </Frag>
        <Frag className="tfm-time">
          <span>1r encert</span>
          <b>+1 dia</b>
          <p>q ≥ 3. Primera vegada.</p>
        </Frag>
        <Frag className="tfm-time">
          <span>2n encert</span>
          <b>+6 dies</b>
          <p>Encara no multiplica.</p>
        </Frag>
        <Frag className="tfm-time">
          <span>Després</span>
          <b>I × ease</b>
          <p>round(I × ease). Ease mínim 1,3.</p>
        </Frag>
      </div>
    </Slide>
  );
}
