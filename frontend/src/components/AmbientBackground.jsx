import React, { useEffect, useRef } from 'react';

export default function AmbientBackground({ intensity = 1 }) {
  const ref = useRef(null);

  useEffect(() => {
    const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
    if (reduce) return;
    let raf = 0;
    let tx = 0, ty = 0, cx = 0, cy = 0;
    const onMove = (e) => {
      tx = (e.clientX / window.innerWidth - 0.5) * 26 * intensity;
      ty = (e.clientY / window.innerHeight - 0.5) * 20 * intensity;
    };
    const loop = () => {
      cx += (tx - cx) * 0.045;
      cy += (ty - cy) * 0.045;
      if (ref.current) ref.current.style.setProperty('--mx', `${cx.toFixed(2)}px`);
      if (ref.current) ref.current.style.setProperty('--my', `${cy.toFixed(2)}px`);
      raf = requestAnimationFrame(loop);
    };
    window.addEventListener('mousemove', onMove, { passive: true });
    raf = requestAnimationFrame(loop);
    return () => { window.removeEventListener('mousemove', onMove); cancelAnimationFrame(raf); };
  }, [intensity]);

  return (
    <div ref={ref} className="ambient-stage" aria-hidden="true" style={{ ['--mx']: '0px', ['--my']: '0px' }}>
      <div className="ambient-blob ambient-blob-a" style={{ transform: 'translate3d(var(--mx), var(--my), 0)' }} />
      <div className="ambient-blob ambient-blob-b" />
      <div className="ambient-blob ambient-blob-c" />
      <div className="ambient-grain" />
      <style>{`
        .ambient-blob-a { translate: var(--mx) var(--my); }
      `}</style>
    </div>
  );
}
