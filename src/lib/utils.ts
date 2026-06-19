import data from '../data/carenas.json';

export const site = data.site;
export const categories = data.categories;
export const places = data.places;

export function slugify(value: string): string {
  return value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

export function findPlace(slug: string) {
  return places.find((place) => place.slug === slug);
}

export function placesByType(type: string) {
  return places.filter((place) => place.type === type);
}

export function featuredPlaces(limit = 6) {
  return places
    .filter((place) => place.priority === 'high')
    .slice(0, limit);
}

export function relatedPlaces(place: any, limit = 4) {
  return places
    .filter((item) => item.slug !== place.slug && item.type === place.type)
    .slice(0, limit);
}

export function formatHours(hours: string[]) {
  if (!hours || hours.length === 0) return ['Horario pendiente de verificar'];
  return hours;
}

export function initials(name: string) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0])
    .join('')
    .toUpperCase();
}

export function categoryCount(type: string) {
  return places.filter((place) => place.type === type).length;
}
