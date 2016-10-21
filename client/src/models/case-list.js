const http = require('choo/http')

const config = require('../config')

module.exports = {
  namespace: 'caseList',
  state: {
    inbox: [],
    history: [],
    view: 'Inbox'
  },
  reducers: {
    receiveInbox: (cases, state) => {
      return { inbox: cases }
    },
    receiveHistory: (cases, state) => {
      return { history: cases }
    },
    setView: (newView, state) => {
      return { view: newView }
    }
  },
  effects: {
    fetchInbox: (data, state, send, done) => {
      const uri = `${config.endpoint}cases/awaiting/`
      http(uri, { json: true, withCredentials: true }, (err, response, body) => {
        if (err || response.statusCode !== 200) return done(new Error('Error fetching inbox'))
        send('caseList:receiveInbox', body.cases, done)
      })
    },
    fetchHistory: (data, state, send, done) => {
      const uri = `${config.endpoint}cases/acted/`
      http(uri, { json: true, withCredentials: true }, (err, response, body) => {
        if (err || response.statusCode !== 200) return done(new Error('Error fetching history'))
        send('caseList:receiveHistory', body.cases, done)
      })
    }
  }
}
