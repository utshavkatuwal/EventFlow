// Cinematic, art-directed photography per category — Unsplash (stable photo IDs)
// Each category gets 3 curated images for visual diversity; deterministic pick by title hash.
const CATEGORY_PHOTOS = {
  Technology: [
    'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1531482615713-2afd69097998?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1515187029135-18ee286d815b?w=1200&q=80&auto=format&fit=crop',
  ],
  Music: [
    'https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=1200&q=80&auto=format&fit=crop',
  ],
  Business: [
    'https://images.unsplash.com/photo-1556761175-b413da4baf72?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1557804506-669a67965ba0?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=1200&q=80&auto=format&fit=crop',
  ],
  Arts: [
    'https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1561214115-f2f134cc4912?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1554907984-15263bfd63bd?w=1200&q=80&auto=format&fit=crop',
  ],
  Sports: [
    'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1517649763962-0c623066013b?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=1200&q=80&auto=format&fit=crop',
  ],
  Education: [
    'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1523580494863-6f3031224c94?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1544531586-fde5298cdd40?w=1200&q=80&auto=format&fit=crop',
  ],
  Gaming: [
    'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1511512578047-dfb367046420?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1552820728-8b83bb6b773f?w=1200&q=80&auto=format&fit=crop',
  ],
  Career: [
    'https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1553877522-43269d4ea984?w=1200&q=80&auto=format&fit=crop',
  ],
  Workshop: [
    'https://images.unsplash.com/photo-1552664730-d307ca884978?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1531482615713-2afd69097998?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=1200&q=80&auto=format&fit=crop',
  ],
  Conference: [
    'https://images.unsplash.com/photo-1505373877841-8d25f7d46678?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1591115765373-5207764f72e7?w=1200&q=80&auto=format&fit=crop',
  ],
  Community: [
    'https://images.unsplash.com/photo-1511632765486-a01980e01a18?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1582213782179-e0d53f98f2ca?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1593113598332-cd288d649433?w=1200&q=80&auto=format&fit=crop',
  ],
  Food: [
    'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1200&q=80&auto=format&fit=crop',
  ],
  Film: [
    'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1200&q=80&auto=format&fit=crop',
  ],
  Health: [
    'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=1200&q=80&auto=format&fit=crop',
  ],
  Other: [
    'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1511578314322-379afb476865?w=1200&q=80&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=1200&q=80&auto=format&fit=crop',
  ],
};

const HERO_AMBIENT = [
  'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=1600&q=80&auto=format&fit=crop',
  'https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=1600&q=80&auto=format&fit=crop',
  'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1600&q=80&auto=format&fit=crop',
];

function hashStr(s = '') {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  return h;
}

export function getCategoryImage(categoryName, eventTitle = 'Event') {
  const key = CATEGORY_PHOTOS[categoryName] ? categoryName : 'Other';
  const arr = CATEGORY_PHOTOS[key];
  const idx = hashStr(`${categoryName}-${eventTitle}`) % arr.length;
  return arr[idx];
}

export function getCategoryPhotos(categoryName) {
  return CATEGORY_PHOTOS[categoryName] || CATEGORY_PHOTOS.Other;
}

export function getHeroAmbient(seed = 0) {
  return HERO_AMBIENT[seed % HERO_AMBIENT.length];
}

export function getEventImageUrl(event) {
  if (event?.cover_image_url) return event.cover_image_url;
  return getCategoryImage(event?.category_name, event?.title);
}

export function imageOnError(e) {
  try { e.target.onerror = null; } catch {}
  const alt = e.target?.alt || 'Event';
  e.target.src = getCategoryImage('Other', alt);
}
