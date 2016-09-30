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
      <div class="row case">
        <div class="col-md-9 data">
          ${state.id ? CaseData(state.data) : ''}
        </div>
        <div class="col-md-3 events">
          <div class="panel panel-default">
            <div class="panel-body">
              ${state.id ? CaseHistory(state.events) : ''}
            </div>
          </div>
        </div>
      </div>
      ${availableActions.length > 1
        ? ActionButtons(availableActions, currentAction, onClickAction)
        : ''}
      ${currentAction ? ActionForm(currentAction, onSubmitAction) : ''}
    </div>
  `

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
