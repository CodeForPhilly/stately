const http = require('choo/http')
const series = require('run-series')

const config = require('../config')

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
      let uri = `${config.endpoint}${workflowSlug}/`
      if (caseId) uri += `${caseId}/`
      if (token) uri += `?token=${token}`
      const opts = { json: true, withCredentials: true }

      http(uri, opts, (err, response, body) => {
        if (err || response.statusCode !== 200) return done(new Error('Error fetching case'))
        send('case:receive', body, done)
      })
    },
    update: (data, state, send, done) => {
      const { workflowSlug, actionSlug, payload, caseId, token } = data
      let uri = `${config.endpoint}${workflowSlug}/${caseId}/${actionSlug}/`
      if (token) uri += `?token=${token}`
      const opts = { json: payload, withCredentials: true }

      http.post(uri, opts, (err, response, body) => {
        if (err || response.statusCode !== 200) return done(new Error('Error updating case'))

        series([
          (cb) => send('case:receive', body, cb),
          (cb) => send('ui:notify', { message: 'Case updated successfully', type: 'success' }, cb)
        ], done)
      })
    },
    // create is the same as update except it redirects afterwards
    create: (data, state, send, done) => {
      const { workflowSlug, payload } = data
      const uri = `${config.endpoint}${workflowSlug}/`
      const opts = { json: payload, withCredentials: true }

      http.post(uri, opts, (err, response, body) => {
        if (err || response.statusCode !== 200) return done(new Error('Error creating case'))
        const newPath = `${workflowSlug}/${body.id}/`

        series([
          (cb) => send('case:receive', body, cb),
          (cb) => send('case:redirect', newPath, cb),
          (cb) => send('ui:notify', { message: 'Case created successfully', type: 'success' }, cb)
        ], done)
      })
    },
    redirect: (path, state, send, done) => {
      window.history.pushState({}, null, path)
      send('location:setLocation', { location: path }, done)
    }
  }
}
