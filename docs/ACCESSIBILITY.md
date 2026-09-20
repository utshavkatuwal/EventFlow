# EventFlow - Accessibility Guidelines

## WCAG 2.1 AA Compliance

Target: WCAG 2.1 Level AA

## Semantic HTML

- Use proper heading hierarchy (h1-h6)
- Use `<main>`, `<nav>`, `<section>`, `<article>`, `<aside>`
- Form labels with `for` attribute matching input `id`
- Button elements for actions, not `<div>` or `<span>`

## Keyboard Navigation

- All interactive elements reachable via Tab
- Visible focus states (2px outline with offset)
- Skip to main content link
- Logical tab order

## Focus Management

```css
:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}
```

## Color Contrast

- Text: 4.5:1 minimum (AA)
- Large text: 3:1 minimum (AA)
- UI components: 3:1 minimum (AA)
- Don't rely on color alone for status

## ARIA

- `aria-label` for icon-only buttons
- `aria-expanded` for dropdowns
- `aria-live` for dynamic content
- `role="dialog"` for modals
- `aria-modal="true"` for modals

## Forms

- Required field indication
- Error messages linked with `aria-describedby`
- Help text with `aria-describedby`
- Native validation where possible

## Responsive Design

- Text resizing up to 200% without loss of function
- No horizontal scrolling at 320px width
- Touch targets minimum 44x44px

## Testing

- axe-core automated testing
- Keyboard-only navigation testing
- Screen reader testing (NVDA, VoiceOver)
- Color contrast analyzer