import { Frag, Kicker, Lede, Slide, Stack, Title } from "../ui";

export function ObjectivesSlide() {
  return (
    <Slide notes="50 s. Llegeix les cinc funcionalitats, una frase cadascuna. No O1–O6. Abast a la següent.">
      <Kicker>Objectius</Kicker>
      <Title>El que fa Studyraft.</Title>
      <Lede className="is-wide">Un cicle sobre PDF propis. No un xat genèric.</Lede>
      <Stack center>
        <Frag as="li">Assignatures i els teus PDF</Frag>
        <Frag as="li">Indexar en cua, amb estat a la pantalla</Frag>
        <Frag as="li">Preguntar i citar fitxer i pàgina</Frag>
        <Frag as="li">Flashcards i quiz del mateix índex</Frag>
        <Frag as="li">Calendari SM-2: si falles, torna en 1 dia</Frag>
      </Stack>
    </Slide>
  );
}
