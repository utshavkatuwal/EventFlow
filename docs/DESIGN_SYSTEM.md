# EventFlow - Design System Documentation

## Colors

```css
:root {
  --color-bg: #f6f5f2;
  --color-surface: #ffffff;
  --color-text: #1a1a1a;
  --color-text-secondary: #6b6b6b;
  --color-text-tertiary: #9b9b9b;
  --color-border: #e5e3df;
  --color-border-light: #f0eeeb;
  --color-accent: #c45a28;
  --color-accent-hover: #a84c20;
  --color-accent-light: #fdf3ec;
  --color-error: #c0392b;
  --color-success: #27795f;
  --color-success-light: #edf5f1;
  --color-warning: #b7791f;
}
```

## Typography

```css
--font-sans: "Noto Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;

--font-size-xs: 0.75rem;
--font-size-sm: 0.875rem;
--font-size-base: 1rem;
--font-size-md: 1.125rem;
--font-size-lg: 1.25rem;
--font-size-xl: 1.5rem;
--font-size-2xl: 2rem;
--font-size-3xl: 2.5rem;
```

## Spacing

```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 24px;
--space-6: 32px;
--space-7: 48px;
--space-8: 64px;
```

## Border Radius

```css
--radius-sm: 6px;
--radius-md: 10px;
--radius-lg: 16px;
```

## Components

### Button Variants
- `.btn-primary` - Accent background, white text
- `.btn-secondary` - Transparent, border
- `.btn-sm` / `.btn-md` / `.btn-lg` - Size variants

### Card
- `.event-card` - Standard event card
- `.ticket-card` - Ticket display card

### Status Badges
- `.status-badge.status-valid` - Green
- `.status-badge.status-used` - Green
- `.status-badge.status-cancelled` - Red
- `.status-badge.status-draft` - Yellow
- `.status-badge.status-pending_review` - Yellow
- `.status-badge.status-approved` - Green
- `.status-badge.status-published` - Green
- `.status-badge.status-rejected` - Red

### Form Elements
- Consistent input/select/textarea styling
- Focus states with accent outline
- Error states with red border

## Responsive Breakpoints

```css
/* Mobile first */
@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
```