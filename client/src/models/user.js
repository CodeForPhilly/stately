const http = require('choo/http')
const series = require('run-series')

const config = require('../config')

module.exports = {
  namespace: 'user',
  state: {
    email: ''
  },
  reducers: {
    receive: (data, state) => data
  },
  effects: {
    fetch: (data, state, send, done) => {
      const uri = `${config.endpoint}actor/`
      const opts = { json: true, withCredentials: true }

      http(uri, opts, (err, response, body) => {
        if (err || response.statusCode !== 200) {
          return send('ui:error', 'Error fetching user', done)
        }
        send('user:receive', body, done)
      })
    },
    sendAuthToken: (email, state, send, done) => {
      const uri = `${config.endpoint}send-auth-token/`
      const payload = { email }
      const opts = { json: payload, withCredentials: true }
      const confirmMsg = `An email was sent to ${email} with a link to login`

      http.post(uri, opts, (err, response, body) => {
        if (err || response.statusCode !== 204) {
          return send('ui:error', 'Error sending auth token', done)
        }
        send('ui:info', { message: confirmMsg, duration: 10000 }, done)
      })
    },
    signOut: (data, state, send, done) => {
      const uri = `${config.endpoint}actor/`
      const opts = { withCredentials: true }

      http.del(uri, opts, (err, response, body) => {
        if (err || response.statusCode !== 204) {
          return send('ui:error', 'Error signing out', done)
        }
        const emptyState = module.exports.state

        series([
          (cb) => send('user:receive', emptyState, cb),
          (cb) => send('case:redirect', '/', cb)
        ], done)
      })
    }
  }
}
