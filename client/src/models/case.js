const http = require('choo/http')

const endpoint = 'http://localhost:8000/api/'

module.exports = {
  namespace: 'case',
  state: {
    workflow: '',
    created: null,
    id: null,
    state: {
      name: '',
      actions: []
    },
    data: {},
    events: [],
    currentAction: null
  },
  reducers: {
    receive: (data, state) => {
      return data
    },
    setCurrentAction: (actionName, state) => {
      return { currentAction: actionName }
    }
  },
  effects: {
    fetch: (data, state, send, done) => {
      const { workflowSlug, caseId, token } = data
      let uri = `${endpoint}${workflowSlug}/`
      if (caseId) uri += `${caseId}/`
      if (token) uri += `?token=${token}`

      http(uri, { json: true, withCredentials: true }, (err, response, body) => {
        if (err || response.statusCode !== 200) return done(new Error('Error fetching case'))
        send('case:receive', body, done)
      })
    },
    update: (data, state, send, done) => {
      const { workflowSlug, actionSlug, payload, caseId, token } = data
      let uri = `${endpoint}${workflowSlug}/${caseId}/${actionSlug}/`
      if (token) uri += `?token=${token}`

      http.post(uri, { json: payload, withCredentials: true }, (err, response, body) => {
        if (err || response.statusCode !== 200) return done(new Error('Error updating case'))
        send('case:receive', body, done)
      })
    },
    // create is the same as update except it redirects afterwards
    create: (data, state, send, done) => {
      const { workflowSlug, payload } = data
      const uri = `${endpoint}${workflowSlug}/`

      http.post(uri, { json: payload, withCredentials: true }, (err, response, body) => {
        if (err || response.statusCode !== 200) return done(new Error('Error creating case'))
        send('case:receive', body, () => {
          const newPath = `${workflowSlug}/${body.id}/?token=${body.assignment.token}`
          send('case:redirect', newPath, done)
        })
      })
    },
    redirect: (path, state, send, done) => {
      window.history.pushState({}, null, path)
      send('location:setLocation', { location: path }, done)
    }
  }
}
