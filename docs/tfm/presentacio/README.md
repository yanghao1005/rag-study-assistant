# Presentació HTML

Defensa EPS. La deck viva és al frontend:

`docker compose up` o `pnpm --dir frontend dev` → [http://localhost:3000/presentacio](http://localhost:3000/presentacio)

**44 pantalles** (8 portades de secció + 36 de cos). Els termes (RAG, chunk, embedding, groundedness, SM-2, hexàgon, p50) s’expliquen a la pantalla.

Revisió amb ull de tribunal: [`REVISIO-TRIBUNAL.md`](REVISIO-TRIBUNAL.md).

Cada diapositiva és un fitxer a `frontend/src/features/presentacio/slides/`. L’ordre viu és `slides.ts`.

| Tecla | Acció |
|---|---|
| → · Espai | Fragment / diapo |
| `F` | Pantalla completa |
| `N` / `S` | Notes |
| `Ctrl+P` | PDF |

`index.html` d’aquesta carpeta queda com a còpia estàtica desfasada; no la projectis.
