const html = require('choo/html')

require('brutusin-json-forms/dist/js/brutusin-json-forms')
const BrutusinForms = window.brutusin['json-forms']

module.exports = (state, prev, send) => {
  const formContainerEl = document.createElement('form')
  const bf = BrutusinForms.create(state.case.schema)
  bf.render(formContainerEl)

  // Add submit button & hook submit event (hacky, but the lib doesn't have an alternative)
  const formEl = formContainerEl.querySelector('form')
  formEl.onsubmit = onsubmit
  const submitButton = html`<button type="submit" class="btn btn-primary">Submit</button>`
  formEl.appendChild(submitButton)

  return html`
    <div class="container" onload=${onload}>
      ${formContainerEl}
    </div>
  `
  
  function onload () {
    send('case:getSchema', state.params.schema)
  }
  
  function onsubmit (e) {
    const formData = bf.getData()
    console.log(formData)
    e.preventDefault()
  }
}

// Enable bootstrap theme
BrutusinForms.addDecorator((element, schema) => {
    if (element.tagName) {
        var tagName = element.tagName.toLowerCase()
        if (tagName === 'input' && element.type !== 'checkbox' || tagName === 'textarea') {
            element.classList.add('form-control')
        } else if (tagName === 'select') {
            element.classList.add('chosen-select', 'form-control')
        } else if (tagName === "button") {
            if (element.classList.contains('remove')) {
                element.classList.add('glyphicon', 'glyphicon-remove')
                while (element.firstChild) {
                    element.removeChild(element.firstChild)
                }
            }
            element.classList.add('btn', 'btn-primary', 'btn-xs')
        } else if (tagName === 'form') {
            element.classList.add('form-inline')
        }
    }
})
