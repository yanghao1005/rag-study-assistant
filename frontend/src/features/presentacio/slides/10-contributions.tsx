import { Frag, Kicker, Slide, Stack, Title } from "../ui";

export function ContributionsSlide() {
  return (
    <Slide notes="25 min: salta o 20 s. El 8/07 s’arxiva el prototip LangChain. Hexàgon: tests sense claus. Objectius a #/20.">
      <Kicker>Contribucions</Kicker>
      <Title>Què queda al producte</Title>
      <Stack>
        <Frag as="li">Hexàgon després del prototip LangChain (juliol 2026)</Frag>
        <Frag as="li">Ingestió per etapes, relançable (el navegador no espera el parse)</Frag>
        <Frag as="li">RAG híbrid + intent + sinopsi + cites</Frag>
        <Frag as="li">Biblioteca de pràctica i planner SM-2</Frag>
        <Frag as="li">Login, UI del cicle i privacitat per usuari</Frag>
      </Stack>
    </Slide>
  );
}
