const html = require('choo/html')

module.exports = (data) => {
  const keys = Object.keys(data)

  return html`
    <dl class="dl-horizontal">
      ${keys.map((key) => html`
        <div>
          <dt>${key}</dt>
          <dd>${data[key]}</dd>
        </div>
      `)}
    </dl>
  `
}
