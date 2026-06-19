const photoModules = import.meta.glob('../assets/photos/*.{jpg,jpeg,png,webp,avif}', {
  eager: true,
  query: '?url',
});

const extensions = ['jpg', 'jpeg', 'png', 'webp', 'avif'];

export function getPhoto(slug: string, suffix = '') {
  const base = suffix ? `${slug}-${suffix}` : slug;

  for (const ext of extensions) {
    const module = photoModules[`../assets/photos/${base}.${ext}`] as { default?: string } | undefined;
    if (module?.default) return module.default;
  }

  return undefined;
}

export function getGallery(slug: string, configured: string[] = []) {
  if (configured?.length) return configured;

  const gallery: string[] = [];
  for (let index = 1; index <= 8; index += 1) {
    const photo = getPhoto(slug, String(index));
    if (!photo) break;
    gallery.push(photo);
  }

  return gallery;
}
