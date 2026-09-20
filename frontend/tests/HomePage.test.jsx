import React from 'react';
import { render, screen } from '@testing-library/react';
import HomePage from '../pages/HomePage';

describe('HomePage', () => {
  test('renders hero heading', () => {
    render(<HomePage />);
    expect(screen.getByText('Discover Events in Nepal')).toBeInTheDocument();
  });
});
