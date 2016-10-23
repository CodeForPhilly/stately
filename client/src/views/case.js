const html = require('choo/html')

const CaseData = require('../components/case-data')
const CaseHistory = require('../components/case-history')
const ButtonGroup = require('../components/button-group')
const ActionForm = require('../components/action-form')

module.exports = (state, prev, send) => {
  const { workflowSlug, caseId } = state.params

  // Fetch the case here instead of onload because this view is reused by
  // all cases / case types, and onload is only called when it's first mounted
  if (workflowSlug !== prev.params.workflowSlug || caseId !== prev.params.caseId) {
    console.log(state.params, prev.params)
    send('case:fetch', { workflowSlug, caseId })
  }

  // Determine what to show in action section
  const availableActions = state.case.state.actions
  const availableActionNames = availableActions.map((action) => action.name)
  let currentAction
  if (state.case.currentAction) {
    currentAction = findAvailableAction(state.case.currentAction)
  } else if (availableActions.length === 1) {
    currentAction = availableActions[0]
  }
  const currentActionName = currentAction && currentAction.name

  return html`
    <div>
      <h1>
        ${state.case.workflow.name}
        ${state.case.id ? html`<small>#${state.case.id}</small>` : ''}
      </h1>
      ${state.case.id ? CurrentCase(state.case.data, state.case.events, state.case.state) : ''}
      ${availableActions.length > 1
        ? ButtonGroup(availableActionNames, currentActionName, onClickAction)
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
