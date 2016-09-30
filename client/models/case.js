const http = require('choo/http')

const endpoint = 'http://localhost:8000/api/'

module.exports = {
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
    receiveCase: (data, state) => {
      return data
    },
    setCurrentAction: (actionName, state) => {
      return { currentAction: actionName }
    }
  },
  effects: {
    fetchCase: (data, state, send, done) => {
      const { workflowSlug, caseId, token } = data
      let uri = `${endpoint}${workflowSlug}/`
      if (caseId) uri += `${caseId}/`
      if (token) uri += `?token=${token}`

      http(uri, { json: true }, (err, response, body) => {
        if (err || response.statusCode !== 200) {
          return done(new Error('Error fetching case'))
        }
        send('receiveCase', body, done)
      })
    },
    updateCase: (data, state, send, done) => {
      const { workflowSlug, actionSlug, payload, caseId, token } = data
      let uri = `${endpoint}${workflowSlug}/`
      if (caseId) uri += `${caseId}/`
      if (actionSlug) uri += `${actionSlug}/`
      if (token) uri += `?token=${token}`

      http.post(uri, { json: payload }, (err, response, body) => {
        if (err || response.statusCode !== 200) {
          return done(new Error('Error updating case'))
        }
        send('receiveCase', body, done)
      })
    }
  }
}
