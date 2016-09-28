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
    events: []
  },
  reducers: {
    receiveCase: (data, state) => {
      return data
    }
  },
  effects: {
    fetchCase: (data, state, send, done) => {
      const { workflow, id } = data
      const uri = `${endpoint}${workflow}/` + (id ? `{id}/` : '')
      http(uri, { json: true }, (err, response, body) => {
        if (err || response.statusCode !== 200) {
          return done(new Error('Error fetching case'))
        }
        send('receiveCase', body, done)
      })
    },
    createCase: (data, state, send, done) => {
      const { workflow, payload } = data
      const uri = `${endpoint}${workflow}/`
      http.post(uri, { json: payload }, (err, response, body) => {
        if (err || response.statusCode !== 200) {
          return done(new Error('Error creating case'))
        }
        send('receiveCase', body, done)
      })
    }
  }
}
