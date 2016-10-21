const html = require('choo/html')

module.exports = (labels, selected, onClickButton) => {
  // Determine classes and click handler for each action
  const buttons = labels.map((label) => {
    const onclick = (e) => onClickButton && onClickButton(label)
    const classes = ['btn', 'btn-default', 'btn-lg']
    if (selected && label === selected) {
      classes.push('active')
    }

    return { label, classes, onclick }
  })

  return html`
    <div class="btn-group" role="group">
      ${buttons.map((button) => {
        return html`
          <button class="${button.classes.join(' ')}" onclick=${button.onclick} type="button">
            ${button.label}
          </button>
        `
      })}
    </div>
  `
}
