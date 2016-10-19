const html = require('choo/html')

const NavBar = require('../components/nav-bar')

module.exports = (CurrentView) => (state, prev, send) => {
  return html`
    <main onload=${onLoad}>
      ${NavBar(state.user)}
      <div class="container">
        ${CurrentView(state, prev, send)}
      </div>
    </main>
  `

  function onLoad () {
    send('user:fetch')
  }
}
