import { Kicker, Slide, Title } from "../ui";

export function ShotQuizSlide() {
  return (
    <Slide notes="25 min: salta si la demo viu. El quiz fa el mateix camí de retrieval. Conjunt editable, no un test efímer.">
      <Kicker>Xarxa · quiz</Kicker>
      <Title>El mateix índex, un test.</Title>
      <figure className="tfm-shot">
        <img src="/presentacio/06-quiz.png" alt="Qüestionari generat des dels apunts" />
      </figure>
    </Slide>
  );
}
