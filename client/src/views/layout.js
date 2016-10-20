const html = require('choo/html')
const domNotifications = require('dom-notifications')

const NavBar = require('../components/nav-bar')

module.exports = (CurrentView) => (state, prev, send) => {
  const notifications = domNotifications()
  const notificationsEl = notifications.element()

  state.ui.notifications.map((notification) => notifications.add(notification))

  return html`
    <main onload=${onLoad}>
      ${NavBar(state.user)}
      ${notificationsEl}
      <div class="container">
        ${CurrentView(state, prev, send)}
      </div>
    </main>
  `

  function onLoad () {
    send('user:fetch')
  }
}
