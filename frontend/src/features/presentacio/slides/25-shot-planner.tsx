import { Kicker, Slide, Title } from "../ui";

export function ShotPlannerSlide() {
  return (
    <Slide notes="Salta si la demo viu. SM-2 ja és a #/27.">
      <Kicker>Xarxa · planner</Kicker>
      <Title>SM-2 al domini.</Title>
      <figure className="tfm-shot">
        <img src="/presentacio/08-planner.png" alt="Planner SM-2" />
      </figure>
    </Slide>
  );
}
