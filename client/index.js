const choo = require('choo')
const html = require('choo/html')

const formView = require('./views/form')

const app = choo()

app.model(require('./models/case'))

app.router((route) => [
  route('/:schema', formView)
])

const tree = app.start({ hash: true })
document.body.appendChild(tree)
