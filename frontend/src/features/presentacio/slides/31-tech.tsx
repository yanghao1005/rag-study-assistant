import { Frag, Kicker, Lede, Slide, Title } from "../ui";

export function TechSlide() {
  return (
    <Slide notes="50 s. Llegeix cada fila: què i per què. LangChain → hexàgon: tests sense claus. Pinecone → Supabase: RLS. FSRS → SM-2: auditable. SPA → Next SSR: cookies.">
      <Kicker>Disseny · tecnologies</Kicker>
      <Title>Què s’ha triat, i per què.</Title>
      <Lede>Cada fila és una alternativa descartada. El juliol s’arxiva LangChain.</Lede>
      <Frag className="tfm-table is-tight">
        <table>
          <thead>
            <tr>
              <th>Tria</th>
              <th>En lloc de</th>
              <th>Perquè</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Hexàgon + FastAPI</td>
              <td>LangChain d’una peça</td>
              <td>Tests sense claus; canviar de model</td>
            </tr>
            <tr>
              <td>Supabase + pgvector</td>
              <td>Pinecone / Weaviate</td>
              <td>Auth, SQL, Storage i RLS al mateix lloc</td>
            </tr>
            <tr>
              <td>SM-2 al domini</td>
              <td>FSRS / Anki Connect</td>
              <td>Fórmula pura, suficient per a l’MVP</td>
            </tr>
            <tr>
              <td>Next.js SSR</td>
              <td>SPA pura</td>
              <td>Cookies de sessió i rutes protegides</td>
            </tr>
          </tbody>
        </table>
      </Frag>
    </Slide>
  );
}
