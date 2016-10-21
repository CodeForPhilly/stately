const html = require('choo/html')
const css = require('sheetify')
const Timeago = require('timeago.js')

const timeago = new Timeago()

const prefix = css`
  tbody tr {
    cursor: pointer;
  }
`

module.exports = (state, prev, send) => {
  return html`
    <div onload=${onLoad} class=${prefix}>
      <h1>Cases</h1>
      <table class="table table-hover">
        <thead>
          <tr>
            <th>#</th>
            <th>Workflow</th>
            <th>Created</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
        ${state.caseList.cases.map((case_) => html`
          <tr onclick=${navigate(case_.workflow.slug, case_.id)}>
            <td>${case_.id}</td>
            <td>${case_.workflow.name}</td>
            <td><abbr title=${case_.created}>${timeago.format(case_.created)}</abbr></td>
            <td>${case_.state.name}</td>
          </tr>
        `)}
        </tbody>
      </ul>
    </div>
  `

  function onLoad () {
    send('caseList:fetch')
  }

  function navigate (workflowSlug, id) {
    return function (event) {
      const path = `/${workflowSlug}/${id}`
      send('case:redirect', path)
      event.preventDefault()
    }
  }
}
