import React from 'react';
import Navbar from './Navbar';
import './Layout.css';

export default function Layout({ children }) {
  return (
    <>
      <Navbar />
      <main className="main-content">
        {children}
      </main>
    </>
  );
}
