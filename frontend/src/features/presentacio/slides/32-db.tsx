import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function DbSlide() {
  return (
    <Slide notes="40 s. Tres famílies, no camps. Índex / pràctica / xat. user_id a tot. RLS + filtre al cas d’ús.">
      <Kicker>Disseny · dades</Kicker>
      <Title>Tres famílies. No totes les taules.</Title>
      <Lede>L’assignatura agrupa l’índex, la pràctica i el xat. Cada fila porta l’usuari.</Lede>
      <div className="tfm-db">
        <Frag className="tfm-db-col">
          <span>Índex RAG</span>
          <strong>Documents</strong>
          <p>Chunks per cercar. Cua d’ingestió. El PDF al magatzem.</p>
        </Frag>
        <Frag className="tfm-db-col is-mid">
          <span>Pràctica</span>
          <strong>Conjunts</strong>
          <p>Flashcards i quiz. Ressenyes SM-2. Es poden editar.</p>
        </Frag>
        <Frag className="tfm-db-col">
          <span>Xat</span>
          <strong>Fils</strong>
          <p>Preguntes i respostes amb cites. Historial per assignatura.</p>
        </Frag>
      </div>
    </Slide>
  );
}
