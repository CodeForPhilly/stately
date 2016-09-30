const html = require('choo/html')
const qs = require('sheet-router/qs')

const CaseData = require('../components/case-data')
const CaseHistory = require('../components/case-history')
const ActionButtons = require('../components/action-buttons')
const ActionForm = require('../components/action-form')

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
    <div onload=${onLoad}>
      <h1>${state.workflow.name}</h1>
      ${state.id ? CurrentCase(state.data, state.events) : ''}
      ${availableActions.length > 1
        ? ActionButtons(availableActions, currentAction, onClickAction)
        : ''}
      ${currentAction ? ActionForm(currentAction, onSubmitAction) : ''}
    </div>
  `

  function CurrentCase (data, events) {
    return html`
      <div class="row case">
        <div class="col-sm-9 data">
          ${CaseData(data)}
        </div>
        <div class="col-sm-3 events">
          <div class="panel panel-default">
            <div class="panel-body">
              ${CaseHistory(events)}
            </div>
          </div>
        </div>
      </div>
    `
  }

  function findAvailableAction (actionName) {
    return availableActions.find((availableAction) => availableAction.name === actionName)
  }

  function onLoad () {
    send('fetchCase', { workflow, caseId, token })
  }

  function onClickAction (actionName) {
    send('setCurrentAction', actionName)
  }

  function onSubmitAction (payload) {
    send('createCase', { workflow, payload })
  }
}
