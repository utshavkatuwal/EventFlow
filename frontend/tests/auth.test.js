describe('Auth Flow', () => {
  test('login form renders', () => {
    cy.visit('/login');
    cy.get('input[type="email"]').should('be.visible');
    cy.get('input[type="password"]').should('be.visible');
    cy.get('button[type="submit"]').should('be.visible');
  });

  test('register form renders', () => {
    cy.visit('/register');
    cy.get('input[name="email"]').should('be.visible');
  });
});
