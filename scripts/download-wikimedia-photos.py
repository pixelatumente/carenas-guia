#!/usr/bin/env python3
"""Download Wikimedia Commons photos for Carenas Guía.

Uses the MediaWiki API, saves images under src/assets/photos, and writes
attribution.md with source, author and license data.
"""

from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "src" / "assets" / "photos"
ATTRIBUTION = OUT_DIR / "attribution.md"
API = "https://commons.wikimedia.org/w/api.php"

HEADERS = {
    "User-Agent": "CarenasGuiaPhotoDownloader/1.0 (https://carenas-astro.pages.dev/)",
}

# Exact Commons files only. Esto evita que búsquedas ambiguas traigan fotos de otros sitios.
# Por defecto no usamos búsqueda abierta para evitar falsos positivos.
USE_SEARCH_FALLBACK = False

EXACT_FILES = {
    "carenas": "File:Carenas (Aragón).jpg",
    "embalse-de-la-tranquera": "File:Embalse de la Tranquera, Zaragoza, España, 2015-01-08, DD 03-08 PAN.JPG",
    "monasterio-de-piedra": "File:007555 - Monasterio de Piedra (8818525998).jpg",
    "jaraba": "File:Antiguo corral-jaraba-10-2010 02.JPG",
    "nuevalos": "File:Nuévalos, Zaragoza, España, 2016-01-05, DD 04-06 HDR.JPG",
}

PHOTO_PLAN = [
    {"slug": "carenas", "queries": ["Carenas Zaragoza", "Carenas pueblo"]},
    {"slug": "castillo-de-somet", "queries": ["Castillo de Somet", "Castillo de Somet Carenas"]},
    {"slug": "embalse-de-la-tranquera", "queries": ["Embalse de La Tranquera", "La Tranquera reservoir"]},
    {"slug": "monasterio-de-piedra", "queries": ["Monasterio de Piedra Nuévalos", "Monasterio de Piedra"]},
    {"slug": "suite-rural-carenas", "queries": ["Suite Rural Carenas"]},
    {"slug": "ruta-carenas-embalse-la-tranquera", "queries": ["Embalse de La Tranquera senderismo", "Carenas Embalse de La Tranquera ruta"], "reuse": "embalse-de-la-tranquera"},
    {"slug": "ruta-castillo-de-somet-embalse-la-tranquera", "queries": ["Castillo de Somet Embalse de La Tranquera", "Castillo de Somet Carenas"], "reuse": "castillo-de-somet"},
    {"slug": "ayuntamiento-carenas", "queries": ["Ayuntamiento de Carenas", "Carenas town hall"]},
    {"slug": "iglesia-nuestra-senora-asuncion", "queries": ["Iglesia Nuestra Señora de la Asunción Carenas", "Iglesia de la Asunción Carenas"]},
    {"slug": "ermita-de-santa-ana", "queries": ["Ermita de Santa Ana Carenas", "Ermita Santa Ana Carenas"]},
    {"slug": "jaraba", "queries": ["Jaraba Zaragoza", "Jaraba pueblo"]},
    {"slug": "nuevalos", "queries": ["Nuévalos Zaragoza", "Nuévalos pueblo"]},
    {"slug": "valle-del-rio-piedra", "queries": ["Valle del Río Piedra Carenas", "Valle del Rio Piedra"]},
    {"slug": "casa-rural-los-pedregales", "queries": ["Casa Rural Los Pedregales Carenas", "Los Pedregales Carenas"]},
]


def api_get(params: dict) -> dict:
    url = f"{API}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def strip_html(value: str | None) -> str:
    if not value:
        return ""
    text = re.sub(r"<[^>]+>", "", value)
    text = text.replace("&quot;", '"').replace("&amp;", "&")
    return text.strip()


def search_files(query: str, limit: int = 12) -> list[dict]:
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrnamespace": 6,
        "gsrwhat": "text",
        "gsrsearch": query,
        "gsrlimit": limit,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|mime|size",
        "iiurlwidth": 1600,
        "origin": "*",
    }
    data = api_get(params)
    pages = data.get("query", {}).get("pages", {})
    files: list[dict] = []

    for page in pages.values():
        info_list = page.get("imageinfo") or []
        if not info_list:
            continue
        info = info_list[0]
        filename = page.get("title", "")
        mime = info.get("mime", "")
        width = int(info.get("width") or 0)
        size = int(info.get("size") or 0)
        ext = filename.rsplit(".", 1)[-1].lower()

        if ext not in {"jpg", "jpeg", "png", "webp"}:
            continue
        if mime not in {"image/jpeg", "image/png", "image/webp"}:
            continue
        if width < 900 or size < 120_000:
            continue

        files.append({
            "filename": filename,
            "url": info.get("thumburl") or info.get("url"),
            "width": width,
            "height": int(info.get("height") or 0),
            "size": size,
            "source_url": f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(filename.replace(' ', '_'))}",
            "metadata": info.get("extmetadata") or {},
        })

    files.sort(key=lambda item: (item["width"] * item["height"]), reverse=True)
    return files


def get_exact_file(filename: str) -> dict | None:
    params = {
        "action": "query",
        "format": "json",
        "titles": filename,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|mime|size",
        "iiurlwidth": 1600,
        "origin": "*",
    }
    data = api_get(params)
    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()))
    info_list = page.get("imageinfo") or []
    if not info_list:
        return None

    info = info_list[0]
    ext = filename.rsplit(".", 1)[-1].lower()
    mime = info.get("mime", "")
    if ext not in {"jpg", "jpeg", "png", "webp"}:
        return None
    if mime not in {"image/jpeg", "image/png", "image/webp"}:
        return None

    return {
        "filename": page.get("title", filename),
        "url": info.get("thumburl") or info.get("url"),
        "width": int(info.get("width") or 0),
        "height": int(info.get("height") or 0),
        "size": int(info.get("size") or 0),
        "source_url": f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(filename.replace(' ', '_'))}",
        "metadata": info.get("extmetadata") or {},
    }


def choose_file(slug: str, queries: list[str]) -> dict | None:
    seen = set()
    for query in queries:
        for item in search_files(query):
            if item["filename"] in seen:
                continue
            seen.add(item["filename"])
            return item
    return None


def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=60) as response:
        destination.write_bytes(response.read())


def metadata_text(item: dict) -> dict[str, str]:
    meta = item.get("metadata") or {}

    def value(key: str) -> str:
        return strip_html((meta.get(key) or {}).get("value"))

    artist = value("Artist") or value("Credit") or "Wikimedia Commons contributor"
    license_name = value("License") or value("LicenseShortName") or "Unknown license"
    description = value("ImageDescription") or value("ObjectName") or item["filename"]
    date = value("DateTimeOriginal")

    return {
        "title": item["filename"],
        "artist": artist,
        "license": license_name,
        "description": description,
        "date": date,
        "source_url": item["source_url"],
    }


def copy_existing(src_slug: str, dst_slug: str) -> bool:
    candidates = []
    for ext in ["jpg", "jpeg", "png", "webp"]:
        path = OUT_DIR / f"{src_slug}.{ext}"
        if path.exists():
            candidates.append(path)
    if not candidates:
        return False

    src = candidates[0]
    dst = OUT_DIR / f"{dst_slug}{src.suffix}"
    if dst.exists():
        return True
    dst.write_bytes(src.read_bytes())
    return True


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    downloaded: list[dict] = []
    reused: list[str] = []
    missing: list[str] = []

    for entry in PHOTO_PLAN:
        slug = entry["slug"]
        existing = any((OUT_DIR / f"{slug}.{ext}").exists() for ext in ["jpg", "jpeg", "png", "webp"])
        if existing:
            print(f"SKIP {slug}: already exists")
            continue

        if entry.get("reuse") and copy_existing(entry["reuse"], slug):
            reused.append(slug)
            print(f"REUSE {slug} <- {entry['reuse']}")
            continue

        exact = EXACT_FILES.get(slug)
        item = get_exact_file(exact) if exact else None
        if not item and USE_SEARCH_FALLBACK:
            item = choose_file(slug, entry["queries"])
        if not item or not item.get("url"):
            missing.append(slug)
            print(f"MISSING {slug}")
            continue

        ext = Path(item["filename"]).suffix.lower().lstrip(".")
        if ext == "jpeg":
            ext = "jpg"
        destination = OUT_DIR / f"{slug}.{ext}"

        if destination.exists():
            print(f"SKIP {slug}: destination exists")
            continue

        print(f"DOWNLOAD {slug} <- {item['filename']}")
        download(item["url"], destination)
        downloaded.append({**entry, **metadata_text(item), "saved_as": destination.name})
        time.sleep(0.35)

    lines = [
        "# Atribución de fotos de Wikimedia Commons",
        "",
        "Fotos descargadas automáticamente desde Wikimedia Commons para Carenas Guía.",
        "",
    ]

    if downloaded:
        lines.append("## Descargadas")
        lines.append("")
        for item in downloaded:
            lines.extend([
                f"### {item['saved_as']}",
                "",
                f"- Archivo original: {item['title']}",
                f"- Autoría: {item['artist']}",
                f"- Licencia: {item['license']}",
                f"- Fecha: {item['date'] or 'No indicada'}",
                f"- Descripción: {item['description']}",
                f"- Fuente: {item['source_url']}",
                "",
            ])

    if reused:
        lines.append("## Reutilizadas")
        lines.append("")
        for slug in reused:
            lines.append(f"- {slug} reutiliza la foto de otro lugar para evitar duplicar descargas.")
        lines.append("")

    if missing:
        lines.append("## No encontradas")
        lines.append("")
        for slug in missing:
            lines.append(f"- {slug}")
        lines.append("")

    ATTRIBUTION.write_text("\n".join(lines), encoding="utf-8")

    print("\nResumen:")
    print(f"- Descargadas: {len(downloaded)}")
    print(f"- Reutilizadas: {len(reused)}")
    print(f"- No encontradas: {len(missing)}")
    print(f"- Atribución: {ATTRIBUTION}")

    if missing:
        print("\nFaltan:", ", ".join(missing))


if __name__ == "__main__":
    main()
