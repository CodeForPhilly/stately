const choo = require('choo')

const Layout = require('./views/layout')
const CaseView = require('./views/case')
const HomeView = require('./views/home')

const app = choo()

if (process.env.NODE_ENV !== 'production') {
  const log = require('choo-log')
  app.use(log())
}

app.model(require('./models/case'))

app.router((route) => [
  route('/', Layout(HomeView)),
  route('/:workflowSlug', Layout(CaseView), [
    route('/:caseId', Layout(CaseView))
  ])
])

const tree = app.start()
document.body.appendChild(tree)
