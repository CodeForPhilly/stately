const html = require('choo/html')

const CaseData = require('../components/case-data')
const CaseHistory = require('../components/case-history')
const ActionButtons = require('../components/action-buttons')
const ActionForm = require('../components/action-form')

module.exports = (state, prev, send) => {
  const { workflowSlug, caseId } = state.params

  // Determine what to show in action section
  const availableActions = state.case.state.actions
  let currentAction
  if (state.case.currentAction) {
    currentAction = findAvailableAction(state.case.currentAction)
  } else if (availableActions.length === 1) {
    currentAction = availableActions[0]
  }

  return html`
    <div onload=${onLoad}>
      <h1>
        ${state.case.workflow.name}
        ${state.case.id ? html`<small>#${state.case.id}</small>` : ''}
      </h1>
      ${state.case.id ? CurrentCase(state.case.data, state.case.events, state.case.state) : ''}
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
          ${CaseHistory(events, currentState)}
        </div>
      </div>
    `
  }

  function findAvailableAction (actionName) {
    return availableActions.find((availableAction) => availableAction.name === actionName)
  }

  function onLoad () {
    send('case:fetch', { workflowSlug, caseId })
  }

  function onClickAction (actionName) {
    send('case:setCurrentAction', actionName)
  }

  function onSubmitAction (actionSlug, payload) {
    if (caseId) {
      send('case:update', { workflowSlug, actionSlug, payload, caseId })
    } else {
      send('case:create', { workflowSlug, payload })
    }
    send('case:setCurrentAction') // unset currentAction
  }
}
