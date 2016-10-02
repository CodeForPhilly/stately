const html = require('choo/html')
const qs = require('sheet-router/qs')

const CaseData = require('../components/case-data')
const CaseHistory = require('../components/case-history')
const ActionButtons = require('../components/action-buttons')
const ActionForm = require('../components/action-form')

module.exports = (state, prev, send) => {
  const { workflowSlug, caseId } = state.params
  const token = qs(window.location.search).token // choo v4 makes this easier

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
      <h1>
        ${state.workflow.name}
        ${state.id ? html`<small>#${state.id}</small>` : ''}
      </h1>
      ${state.id ? CurrentCase(state.data, state.events, state.state) : ''}
      ${availableActions.length > 1
        ? ActionButtons(availableActions, currentAction, onClickAction)
        : ''}
      ${currentAction ? ActionForm(currentAction, onSubmitAction) : ''}
    </div>
  `

  // Separate out current case display layout so we can show it conditionally
  // while maintaining readability
  function CurrentCase (data, events, currentState) {
    return html`
      <div class="row case">
        <div class="col-sm-9 data">
          ${CaseData(data)}
        </div>
        <div class="col-sm-3 events">
          <div class="panel panel-default">
            <div class="panel-body">
              ${CaseHistory(events, currentState)}
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
    send('fetchCase', { workflowSlug, caseId, token })
  }

  function onClickAction (actionName) {
    send('setCurrentAction', actionName)
  }

  function onSubmitAction (actionSlug, payload) {
    if (caseId) {
      send('updateCase', { workflowSlug, actionSlug, payload, caseId, token })
    } else {
      send('createCase', { workflowSlug, payload })
    }
  }
}
