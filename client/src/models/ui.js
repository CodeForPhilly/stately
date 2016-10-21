module.exports = {
  namespace: 'ui',
  state: {
    notifications: []
  },
  reducers: {
    addNotification: (data, state) => {
      const newNotifications = state.notifications.slice(0)
      newNotifications.push(data)
      return { notifications: newNotifications }
    },
    removeNotification: (id, state) => {
      const index = state.notifications.findIndex((row) => row._id === id)
      const newNotifications = [
        ...state.notifications.slice(0, index),
        ...state.notifications.slice(index + 1)
      ]
      return { notifications: newNotifications }
    }
  },
  effects: {
    notify: (data, state, send, done) => {
      const message = typeof data === 'string' ? data : data.message
      const type = data.type || 'info'
      const duration = data.duration || 4000
      const _id = Math.random() // used to ensure timeout removes correct notification
      const payload = { message, type, _id }
      send('ui:addNotification', payload, () => {
        window.setTimeout(() => {
          send('ui:removeNotification', _id, done)
        }, duration)
      })
    },
    success: (data, state, send, done) => {
      const message = typeof data === 'string' ? data : data.message
      const payload = { message, type: 'success' }
      send('ui:notify', payload, done)
    },
    info: (data, state, send, done) => {
      const message = typeof data === 'string' ? data : data.message
      const payload = { message, type: 'info' }
      send('ui:notify', payload, done)
    },
    warning: (data, state, send, done) => {
      const message = typeof data === 'string' ? data : data.message
      const payload = { message, type: 'warning' }
      send('ui:notify', payload, done)
    },
    error: (data, state, send, done) => {
      const message = typeof data === 'string' ? data : data.message
      const payload = { message, type: 'error' }
      send('ui:notify', payload, done)
    }
  }
}
