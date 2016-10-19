const http = require('choo/http')

const endpoint = 'http://localhost:8000/api/'

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
      const uri = `${endpoint}actor/`
      http(uri, { json: true, withCredentials: true }, (err, response, body) => {
        if (err || response.statusCode !== 200) return done(new Error('Error fetching user'))
        send('user:receive', body, done)
      })
    }
  }
}
