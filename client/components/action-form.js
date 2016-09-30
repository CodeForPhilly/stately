const html = require('choo/html')
const getFormData = require('get-form-data')

const Field = require('./field')

module.exports = (action, onSubmitAction) => {
  return html`
    <form onsubmit=${onSubmit}>
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

  function onSubmit (e) {
    if (onSubmitAction) {
      const formData = getFormData(e.target)
      onSubmitAction(formData)
    }
    e.preventDefault()
  }
}
