# Carenas Astro Template

Plantilla Astro estática para una guía local de Carenas.

## Comandos

```bash
pnpm install
pnpm run dev
pnpm run build
pnpm run preview
```

## Estructura

- `src/data/carenas.json` — datos maestros de lugares, alojamientos, rutas y fuentes.
- `src/assets/photos/` — carpeta para añadir fotos reales de cada ficha.
- `src/pages/lugares/[slug].astro` — ficha dinámica de cada lugar.
- `src/pages/categorias/[category].astro` — listado dinámico por categoría.
- `src/components/SearchBar.astro` — buscador cliente, resultados solo por nombre.
- `scripts/generate-search.js` — genera `public/search-data.json`.

## Añadir fotos

Las fotos se cargan automáticamente por slug:

```text
src/assets/photos/castillo-de-somet.jpg
src/assets/photos/castillo-de-somet-1.jpg
src/assets/photos/castillo-de-somet-2.jpg
```

- `castillo-de-somet.jpg` será la foto principal de la ficha.
- `castillo-de-somet-1.jpg`, `castillo-de-somet-2.jpg`, etc. crearán la galería.
- Si no hay foto, la ficha mantiene una portada limpia con iniciales.

## Deploy Cloudflare Pages

```bash
pnpm run build
npx wrangler pages deploy dist --project-name carenas-astro --branch main
```
