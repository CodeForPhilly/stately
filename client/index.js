const choo = require('choo')
const html = require('choo/html')
const http = require('choo/http')
require('json-editor')
const JSONEditor = window.JSONEditor // no commmonjs support :(

const app = choo()

app.model({
  state: {
    schema: {}
  },
  reducers: {
    receiveSchema: (data, state) => {
      return { schema: data }
    },
    setName: (newName, state) => {
      return { name: newName }
    }
  },
  effects: {
    getSchema: (schema, state, send, done) => {
      http(`./fixtures/${schema}.json`, { json: true }, (err, response, body) => {
        if (err || response.statusCode !== 200) return done(new Error('Error fetching schema'))
        send('receiveSchema', body, done)
      })
    }
  }
})

const view = (state, prev, send) => {
  const formEl = document.createElement('div')
  const formOpts = {
    theme: 'bootstrap3',
    schema: state.schema
  }
  const editor = new JSONEditor(formEl, formOpts)
  console.log(editor)

  return html`
    <div class="container" onload=${onload}>
      ${formEl}
      <pre>${JSON.stringify(state.schema, null, 2)}</pre>
    </div>
  `
  
  function onload () {
    send('getSchema', state.params.schema)
  }
}

app.router((route) => [
  route('/:schema', view)
])

const tree = app.start({ hash: true })
document.body.appendChild(tree)
