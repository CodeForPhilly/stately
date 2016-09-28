const html = require('choo/html')
const getFormData = require('get-form-data')

module.exports = (state, prev, send) => {
  const { workflow } = state.params

  return html`
    <div onload=${onload}>
      <h1>${state.workflow}</h1>
      ${state.state.actions.length === 1
        ? Action(state.state.actions[0])
        : NoActions()}
    </div>
  `

  function onload () {
    send('fetchCase', { workflow })
  }

  function Action (action) {
    return html`
      <form onsubmit=${onsubmit}>
        <fieldset>
          <legend>${action.name}</legend>
          ${action.template.fields.map((field) => Field(field))}
        </fieldset>
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

  function NoActions () {
    return html`
      <p>There are no available actions to take</p>
    `
  }
}

function slugify (text) {
  return text.toString().toLowerCase().trim()
    .replace(/[^a-zA-Z0-9]/g, '_')  // Replace non-alphanumeric chars with _
    .replace(/__+/g, '_')           // Replace multiple _ with single _
    .replace(/^_|_$/i, '')          // Remove leading/trailing _
}
