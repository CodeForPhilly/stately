const html = require('choo/html')

module.exports = (state, prev, send) => {
  return html`
    <div>
      <h1>Stately</h1>
      <p>
        Welcome! You're signed in as <strong>${state.user.email}</strong>.
        <a href="#" onclick=${signOut}>Not you</a>?
      </p>
    </div>
  `

  function signOut (evt) {
    send('user:signOut')

    evt.preventDefault()
    evt.stopPropagation()
  }
}
