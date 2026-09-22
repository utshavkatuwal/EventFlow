import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

/* Every route starts below the navbar. Without this, React Router
   preserves the previous page's scroll position, so e.g. Home (scrolled)
   → Login renders mid-page with the heading hidden behind the navbar.
   Respects hash links (#events) — those scroll to the anchor instead. */
export default function ScrollToTop() {
  const { pathname, hash } = useLocation();
  useEffect(() => {
    if (hash) return;
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' in window ? 'instant' : 'auto' });
  }, [pathname, hash]);
  return null;
}
