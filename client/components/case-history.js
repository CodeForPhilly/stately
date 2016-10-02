const html = require('choo/html')
const Timeago = require('timeago.js')

const timeago = new Timeago()

module.exports = (events, currentState) => {
  return html`
    <ul class="list-group">
      ${events.map((event) => html`
        <li class="list-group-item">
          ${event.action.name}
          <span class="actor">${event.actor}</span>
          <abbr title=${event.timestamp}>
            ${timeago.format(event.timestamp)}
          </abbr>
        </li>
      `)}
      <li class="list-group-item"><b>${currentState.name}</b></li>
    </ul>
  `
}
