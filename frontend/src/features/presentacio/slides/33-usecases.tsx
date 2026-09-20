import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function UseCasesSlide() {
  return (
    <Slide notes="50 s. Un gest, una URL. El worker no és un actor humà: acaba l’índex. Usabilitat: castellà de tu, una tasca per pantalla, cites amb nom de fitxer. No enumeris RF.">
      <Kicker>Disseny · l’aplicació</Kicker>
      <Title>Cinc gestos. Una tasca per pantalla.</Title>
      <Lede>L’estudiant inicia. El worker (mateix FastAPI) acaba l’índex.</Lede>
      <div className="tfm-uc">
        <Frag as="article">
          <span>01</span>
          <strong>Assignatures</strong>
          <p>Aïllament del temari</p>
        </Frag>
        <Frag as="article">
          <span>02</span>
          <strong>Pujar PDF</strong>
          <p>Estat: cua → Listo</p>
        </Frag>
        <Frag as="article">
          <span>03</span>
          <strong>Preguntar</strong>
          <p>Resposta amb [1] [2]</p>
        </Frag>
        <Frag as="article">
          <span>04</span>
          <strong>Practicar</strong>
          <p>Cartes i quiz editables</p>
        </Frag>
        <Frag as="article">
          <span>05</span>
          <strong>Repassar</strong>
          <p>El dia el marca SM-2</p>
        </Frag>
      </div>
    </Slide>
  );
}
