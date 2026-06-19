import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const dataPath = resolve(root, 'src/data/carenas.json');
const outputPath = resolve(root, 'public/search-data.json');

const data = JSON.parse(readFileSync(dataPath, 'utf8'));
const items = data.places.map((place) => ({
  title: place.name,
  url: `/lugares/${place.slug}/`,
}));

mkdirSync(dirname(outputPath), { recursive: true });
writeFileSync(outputPath, `${JSON.stringify(items, null, 2)}\n`, 'utf8');

console.log(`Generated ${items.length} search items`);
