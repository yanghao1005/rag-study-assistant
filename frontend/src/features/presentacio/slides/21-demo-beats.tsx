import { Frag, Kicker, Slide, Stack, Title } from "../ui";

export function DemoBeatsSlide() {
  return (
    <Slide notes="Guió de 5 min. No generis de zero. Wi‑Fi UdL = pla B. Producte en castellà. SM-2 ja dit a #/27. Després tests #/37, p50 #/38, límits #/39.">
      <Kicker>Demo · guió</Kicker>
      <Title>El mateix PDF. Quatre batecs.</Title>
      <Stack>
        <Frag as="li">Documents en estat Listo</Frag>
        <Frag as="li">Pregunta factual → fitxer i pàgines</Frag>
        <Frag as="li">Quiz o flashcards des del mateix índex</Frag>
        <Frag as="li">Ressenya SM-2: si falles, interval 1 dia</Frag>
      </Stack>
    </Slide>
  );
}
