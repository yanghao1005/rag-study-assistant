import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function DemoSlide() {
  return (
    <Slide notes="5 min. Alt+Tab. PDF Listo. SM-2 ja l’has explicat a #/27: aquí només el mostres. Després avaluació #/37–#/39, pla #/41 i futur #/43. Si peta: captures #/31–#/35.">
      <Kicker>Demo</Kicker>
      <Title>Un sol recorregut. Local.</Title>
      <Lede>Si va, saltem les captures. La UI és en castellà de tu; això, en català.</Lede>
      <div className="tfm-verbs">
        <Frag>Indexar</Frag>
        <Frag>Preguntar</Frag>
        <Frag>Practicar</Frag>
        <Frag>Repassar</Frag>
      </div>
    </Slide>
  );
}
