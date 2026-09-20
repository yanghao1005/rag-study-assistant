import { Frag, Kicker, Lede, Slide, Stack, Title } from "../ui";

export function FutureSlide() {
  return (
    <Slide notes="45 s. Implantació real: worker separat, rate limit de veritat, Supabase no pausat. No prometis dates. El cap. 8 de la memòria.">
      <Kicker>Conclusions · futur</Kicker>
      <Title>El que quedaria, si hi hagués un pas més.</Title>
      <Lede>Són límits d’aquest TFM, no una roadmap comercial.</Lede>
      <Stack>
        <Frag as="li">OCR: avui un PDF escanejat falla de forma honesta</Frag>
        <Frag as="li">Visor: anar a la pàgina de la cita, no només el snippet</Frag>
        <Frag as="li">Protocol de fidelitat (groundedness), no només cites</Frag>
        <Frag as="li">Worker separat del procés HTTP; estudi amb alumnes</Frag>
      </Stack>
    </Slide>
  );
}
