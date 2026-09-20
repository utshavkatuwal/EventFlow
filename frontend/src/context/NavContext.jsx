import React from 'react';

const NavContext = React.createContext(null);

export function NavProvider({ children }) {
  const [mobileOpen, setMobileOpen] = React.useState(false);

  return (
    <NavContext.Provider value={{ mobileOpen, setMobileOpen }}>
      {children}
    </NavContext.Provider>
  );
}

export function useNav() {
  return React.useContext(NavContext);
}
