const choo = require('choo')

const Layout = require('./views/layout')
const InitiateView = require('./views/initiate')

const app = choo()

app.model(require('./models/case'))

app.router((route) => [
  route('/:workflow', Layout(InitiateView))
])

const tree = app.start()
document.body.appendChild(tree)
