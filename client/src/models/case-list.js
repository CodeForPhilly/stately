const http = require('choo/http')

const config = require('../config')

module.exports = {
  namespace: 'caseList',
  state: {
    cases: []
  },
  reducers: {
    receive: (cases, state) => {
      return { cases: cases }
    }
  },
  effects: {
    fetch: (data, state, send, done) => {
      const uri = `${config.endpoint}cases/awaiting/`
      http(uri, { json: true, withCredentials: true }, (err, response, body) => {
        if (err || response.statusCode !== 200) return done(new Error('Error fetching case list'))
        send('caseList:receive', body.cases, done)
      })
    }
  }
}
