import React from 'react';
import { useLocation } from 'react-router-dom';
import '../styles/Breadcrumbs.css';

export default function Breadcrumbs() {
  const location = useLocation();
  const paths = location.pathname.split('/').filter(Boolean);
  
  if (paths.length <= 1) return null;
  
  return (
    <nav aria-label="Breadcrumb" className="breadcrumbs">
      <a href="/">Home</a>
      {paths.map((path, i) => {
        const href = '/' + paths.slice(0, i + 1).join('/');
        const isLast = i === paths.length - 1;
        return (
          <React.Fragment key={href}>
            <span className="breadcrumb-separator">/</span>
            {isLast ? (
              <span className="breadcrumb-current">{path}</span>
            ) : (
              <a href={href}>{path}</a>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
}
