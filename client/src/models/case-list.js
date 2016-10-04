const http = require('choo/http')

const endpoint = 'http://localhost:8000/api/'

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
      const uri = `${endpoint}cases/awaiting/`
      http(uri, { json: true }, (err, response, body) => {
        if (err || response.statusCode !== 200) return done(new Error('Error fetching case list'))
        send('caseList:receive', body.cases, done)
      })
    }
  }
}
