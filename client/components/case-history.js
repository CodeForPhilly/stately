const html = require('choo/html')
const Timeago = require('timeago.js')

const timeago = new Timeago()

module.exports = (events) => {
  return html`
    <ul>
      ${events.map((event) => html`
        <li>
          Action name
          <abbr title=${event.timestamp}>
            ${timeago.format(event.timestamp)}
          </abbr>
        </li>
      `)}
    </ul>
  `
}
