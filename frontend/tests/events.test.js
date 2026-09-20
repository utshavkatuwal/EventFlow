describe('Event Discovery', () => {
  test('events page renders', () => {
    cy.visit('/events');
    cy.get('h1').should('contain', 'All Events');
  });

  test('event detail renders', () => {
    cy.visit('/events/1');
    cy.get('h1').should('exist');
  });
});
