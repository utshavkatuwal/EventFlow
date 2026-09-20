describe('Dashboard', () => {
  test('user dashboard renders after login', () => {
    cy.visit('/user/dashboard');
    // Should redirect to login if not authenticated
  });

  test('organizer dashboard renders', () => {
    cy.visit('/organizer/dashboard');
  });
});
