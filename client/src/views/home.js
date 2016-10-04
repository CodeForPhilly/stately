const html = require('choo/html')

module.exports = (state, prev, send) => {
  return html`
    <div>
      <h1>Stately</h1>
      <ul>
        <li><a href="/cases">Case List</a></li>
        <li><a href="/travel-request">Travel Request</a></li>
      </ul>
    </div>
  `
}
