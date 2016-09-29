const html = require('choo/html')
const getFormData = require('get-form-data')
const qs = require('sheet-router/qs')
const Timeago = require('timeago.js')
const extend = require('xtend')

const timeago = new Timeago()

module.exports = (state, prev, send) => {
  const { workflow, caseId } = state.params
  const token = qs(window.location.search).token

  // Determine what to show in action section
  const availableActions = state.state.actions
  let currentAction
  if (state.currentAction) {
    currentAction = findAvailableAction(state.currentAction)
  } else if (availableActions.length === 1) {
    currentAction = availableActions[0]
  }

  return html`
    <div onload=${onload}>
      <h1>${state.workflow.name}</h1>
      ${state.id ? Case(state.data, state.events) : ''}
      ${availableActions.length > 1
        ? ActionButtons(availableActions, currentAction)
        : ''}
      ${currentAction ? Action(currentAction) : ''}
    </div>
  `

  function findAvailableAction (actionName) {
    return availableActions.find((availableAction) => availableAction.name === actionName)
  }

  function onload () {
    send('fetchCase', { workflow, caseId, token })
  }

  function Case (data, events) {
    return html`
      <div class="row case">
        <div class="col-md-9 data">
          ${CaseData(data)}
        </div>
        <div class="col-md-3 events">
          <div class="panel panel-default">
            <div class="panel-body">
              ${CaseHistory(events)}
            </div>
          </div>
        </div>
      </div>
    `
  }

  function CaseData (data) {
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

  function CaseHistory (events) {
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

  function ActionButtons (actions, currentAction) {
    // Determine classes and click handler for each action
    const actionList = actions.map((action) => {
      const onclick = (e) => send('setCurrentAction', action.name)
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

  function Action (action) {
    return html`
      <form onsubmit=${onsubmit}>
        ${typeof action.template === 'object'
          ? html`
              <fieldset>
                <legend>${action.name}</legend>
                ${action.template.fields.map((field) => Field(field))}
              </fieldset>
            `
          : ''}
        <button type="submit" class="btn btn-primary">${action.name}</button>
      </form>
    `
  }

  function onsubmit (e) {
    const payload = getFormData(e.target)
    send('createCase', { workflow, payload })
    e.preventDefault()
  }

  function Field (field) {
    const slug = slugify(field.name)
    switch (field.field_type) {
      // case paragraph, option, etc.
      default:
        return html`
          <div class="form-group">
            <label for=${slug}>${field.name}</label>
            <input type="${field.field_type}" name=${slug} id=${slug} class="form-control" />
            ${field.description ? html`<p class="help-block">${field.description}</p>` : ''}
          </div>
        `
    }
  }
}

function slugify (text) {
  return text.toString().toLowerCase().trim()
    .replace(/[^a-zA-Z0-9]/g, '_')  // Replace non-alphanumeric chars with _
    .replace(/__+/g, '_')           // Replace multiple _ with single _
    .replace(/^_|_$/i, '')          // Remove leading/trailing _
}
