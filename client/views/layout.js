const html = require('choo/html')

module.exports = (CurrentView) => (state, prev, send) => {
  return html`
    <div class="container">
      ${CurrentView(state, prev, send)}
    </div>
  `
}
