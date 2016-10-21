const choo = require('choo')
const http = require('choo/http')
const qs = require('sheet-router/qs')

const Layout = require('./views/layout')
const CaseView = require('./views/case')
const CaseListView = require('./views/case-list')
const HomeView = require('./views/home')
const SignInView = require('./views/sign-in')
const config = require('./config')

const app = choo()

if (process.env.NODE_ENV !== 'production') {
  const log = require('choo-log')
  app.use(log())
}

// If token present, authenticate before firing any other requests.
// Not very chooey but no other option comes to mind
const token = qs(window.location.search).token
if (token) {
  authenticate(token, initialize)
} else {
  initialize()
}

function initialize () {
  app.model(require('./models/ui'))
  app.model(require('./models/user'))
  app.model(require('./models/case'))
  app.model(require('./models/case-list'))

  app.router((route) => [
    route('/', Layout(HomeView)),
    route('/:workflowSlug', Layout(CaseView), [
      route('/:caseId', Layout(CaseView))
    ]),
    route('/cases', Layout(CaseListView)),
    route('/sign-in', Layout(SignInView))
  ])

  const tree = app.start()
  document.body.appendChild(tree)
}

function authenticate (token, callback) {
  const uri = `${config.endpoint}authenticate/?token=${token}`
  const opts = { json: true, withCredentials: true }

  http(uri, opts, (err, response, body) => {
    if (err || response.statusCode !== 200) {
      console.error('Error authenticating')
    }
    callback()
  })
}
