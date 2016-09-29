const choo = require('choo')

const Layout = require('./views/layout')
const CaseView = require('./views/case')

const app = choo()

app.model(require('./models/case'))

app.router((route) => [
  route('/:workflow/:caseId', Layout(CaseView)),
  route('/:workflow', Layout(CaseView))
])

const tree = app.start()
document.body.appendChild(tree)
