import { Frag, Kicker, Lede, Slide, Stack, Title } from "../ui";

export function CloseSlide() {
  return (
    <Slide notes="50 s. Tres fets, un límit, agraeix. Preguntes després. No recitis pytest (ja #/37). Si pregunten p50: #/38, n=8, l’autor. No diguis que millora la nota.">
      <Kicker>Conclusions</Kicker>
      <Title>El cicle, amb límits a la vista.</Title>
      <Lede>PDF privats, cites, pràctica i SM-2. El valor és el sistema, no un notebook.</Lede>
      <Stack center>
        <Frag as="li">El cicle sencer: pujar, preguntar amb [n], practicar, SM-2</Frag>
        <Frag as="li">Hexàgon: canviar de model sense reescriure el xat</Frag>
        <Frag as="li">Híbrid + calendari explicable. No mesurem fidelitat ni «només dens»</Frag>
        <Frag as="li">Preguntes</Frag>
      </Stack>
      <Frag as="p" className="tfm-meta">
        <a href="https://github.com/yanghao1005/rag-study-assistant">
          github.com/yanghao1005/rag-study-assistant
        </a>
      </Frag>
    </Slide>
  );
}
