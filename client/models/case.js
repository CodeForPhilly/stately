const http = require('choo/http')

module.exports = {
  namespace: 'case',
  state: {
    schema: {}
  },
  reducers: {
    receiveSchema: (data, state) => {
      return { schema: data }
    }
  },
  effects: {
    getSchema: (schema, state, send, done) => {
      http(`./fixtures/${schema}.json`, { json: true }, (err, response, body) => {
        if (err || response.statusCode !== 200) return done(new Error('Error fetching schema'))
        send('case:receiveSchema', body, done)
      })
    }
  }
}
