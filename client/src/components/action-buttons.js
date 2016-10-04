const html = require('choo/html')
const extend = require('xtend')

module.exports = (actions, currentAction, onClickAction) => {
  // Determine classes and click handler for each action
  const actionList = actions.map((action) => {
    const onclick = (e) => onClickAction(action.name)
    const classes = ['btn', 'btn-default', 'btn-lg']
    if (currentAction && action.name === currentAction.name) {
      classes.push('active')
    }

    return extend(action, { classes, onclick })
  })

  return html`
    <div class="btn-group" role="group" aria-label="Actions">
      ${actionList.map((action) => {
        return html`
          <button class="${action.classes.join(' ')}" onclick=${action.onclick} type="button">
            ${action.name}
          </button>
        `
      })}
    </div>
  `
}
