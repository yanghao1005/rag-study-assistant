import { Frag, Kicker, Lede, Slide, Stack, Title } from "../ui";

export function ProblemSlide() {
  return (
    <Slide notes="50 s. Al·lucinar = fluïdesa sense el PDF. Tres forats: LLM nu, cerca sense cites, cartes sense calendari. No és ITS ni cercador web.">
      <Kicker>Motivació</Kicker>
      <Title>Estudiar d’un PDF no és un xat.</Title>
      <Lede>Tampoc un tutor ITS ni un cercador a internet: són apunts teus, amb cites i un calendari.</Lede>
      <Stack center>
        <Frag as="li" className="tfm-problem">
          Un <em>LLM</em> (model de llenguatge) sense buscar al PDF{" "}
          <em>al·lucina</em>: afirma amb fluïdesa el que no hi és.
        </Frag>
        <Frag as="li" className="tfm-problem">
          Un cercador <em>sense cites</em> no es pot comprovar.
        </Frag>
        <Frag as="li" className="tfm-problem">
          Unes cartes <em>sense calendari</em> s’obliden.
        </Frag>
      </Stack>
    </Slide>
  );
}
