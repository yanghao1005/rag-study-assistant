import { Slide, Title } from "../ui";

export function makeSection(n: string, title: string, beats: string[], notes: string) {
  function SectionCover() {
    return (
      <Slide
        variant="section"
        notes={`10 s. Portada de secció ${n}. Llegeix el títol i els mots. No desenvolupis. ${notes}`}
      >
        <p className="tfm-section-n">{n}</p>
        <Title>{title}</Title>
        <ul className="tfm-section-beats">
          {beats.map((beat) => (
            <li key={beat}>{beat}</li>
          ))}
        </ul>
      </Slide>
    );
  }
  SectionCover.displayName = `Section${n}`;
  return SectionCover;
}
