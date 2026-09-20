import { Kicker, Slide, Title } from "../ui";

export function ShotChatSlide() {
  return (
    <Slide notes="25 min: salta si la demo viu. Contactes al fragment tapats com a la memòria.">
      <Kicker>Xarxa · xat</Kicker>
      <Title>Resposta amb evidència.</Title>
      <figure className="tfm-shot">
        <img src="/presentacio/05-chat.png" alt="Xat amb cites" />
      </figure>
    </Slide>
  );
}
