import { Frag, Kicker, Slide, Stack, Title } from "../ui";

export function LimitsSlide() {
  return (
    <Slide notes="O6 parcial. n=8, l’autor, apunts propis. 369 ms no és el xat: falta ingestió i SSE+LLM. Ètica: PDF privats, RLS, fragments; no dictamen GDPR. OCR = PDF escanejat.">
      <Kicker>Avaluació · límits</Kicker>
      <Title>Què no afirma aquesta avaluació</Title>
      <Stack center>
        <Frag as="li">n = 8, un operador (l’autor), apunts propis: p50 descriptiu</Frag>
        <Frag as="li">Sense dens-only, sense groundedness, sense rellevància</Frag>
        <Frag as="li">Sense temps d’ingestió ni del xat sencer (SSE + LLM)</Frag>
        <Frag as="li">Worker a l’API · rate limit de paper · sense OCR · sense alumnes</Frag>
      </Stack>
    </Slide>
  );
}
