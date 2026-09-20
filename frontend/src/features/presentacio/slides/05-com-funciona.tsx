import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function ComFuncionaRagSlide() {
  return (
    <Slide notes="50 s. Dues fases. La fletxa clau: l’índex ja existeix; en preguntar no reenviem el PDF.">
      <Kicker>Disseny · la IA</Kicker>
      <Title>Dues fases. Un índex al mig.</Title>
      <Lede>Primer es construeix l’índex. Després cada pregunta el consulta. El PDF no torna a entrar.</Lede>
      <div className="tfm-diagram">
        <Frag className="tfm-diagram-lane">
          <span>1 · En pujar · un cop per PDF</span>
          <div className="tfm-nodes">
            <div className="tfm-node">
              <strong>PDF</strong>
              <small>El fitxer teu</small>
            </div>
            <div className="tfm-node">
              <strong>Trossejar</strong>
              <small>Chunks + pàgina</small>
            </div>
            <div className="tfm-node">
              <strong>Representar</strong>
              <small>Vector i paraules</small>
            </div>
            <div className="tfm-node">
              <strong>Índex</strong>
              <small>Ja es pot cercar</small>
            </div>
          </div>
        </Frag>
        <Frag className="tfm-diagram-lane is-ask">
          <span>2 · En preguntar · cada cop</span>
          <div className="tfm-nodes">
            <div className="tfm-node">
              <strong>Pregunta</strong>
              <small>El que vols saber</small>
            </div>
            <div className="tfm-node">
              <strong>Cercar</strong>
              <small>A l’índex, no al PDF</small>
            </div>
            <div className="tfm-node">
              <strong>k trossos</strong>
              <small>Els més pertinents</small>
            </div>
            <div className="tfm-node">
              <strong>LLM + cites</strong>
              <small>Escriu només amb això</small>
            </div>
          </div>
        </Frag>
      </div>
    </Slide>
  );
}
