const html = require('choo/html')
const Timeago = require('timeago.js')

const timeago = new Timeago()

module.exports = (events, currentState) => {
  return html`
    <ul>
      ${events.map((event) => html`
        <li>
          ${event.action.name}
          <abbr title=${event.timestamp}>
            ${timeago.format(event.timestamp)}
          </abbr>
        </li>
      `)}
      <li><b>${currentState.name}</b></li>
    </ul>
  `
}
