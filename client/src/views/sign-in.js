const html = require('choo/html')

module.exports = (state, prev, send) => {
  return html`
    <div>
      <h1>Sign in</h1>
      <form onsubmit=${onSubmit}>
        <div class="form-group">
          <label for="email">Email address</label>
          <input class="form-control" type="email" name="email" required />
        </div>
        <button type="submit" class="btn btn-primary">Sign in</button>
      </form>
    </div>
  `

  function onSubmit (evt) {
    const emailEl = evt.target.querySelector('[name="email"]')
    const email = emailEl.value
    send('user:sendAuthToken', email)
    emailEl.value = '' // reset email field

    evt.preventDefault()
  }
}
