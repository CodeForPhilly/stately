const html = require('choo/html')

module.exports = (state, prev, send) => {
  return html`
    <div>
      <h1>Stately</h1>
      <p>Form-driven workflow engine. Making city government better, one form at a time.</p>

      <p>Government agencies, like many organizations, have a ton of processes. If an
      employee wants to attend a conference and needs travel reimbursement, their
      supervisor must approve, then their director must approve, and if it costs more
      than $500, the CFO must approve. New hire on-boarding consists of several steps
      that can happen in parallel.</p>

      <p>In many cases, there is already software out there -- especially in the HR world
      -- that handle these processes. When they're available, you should use them.
      But when there isn't software already available, or the agency doesn't have
      access to it, the processes still exist; they just take place over email. Stately
      is for these processes.</p>

      <p><a href="https://github.com/codeforphilly/stately">Source code</a></p>
    </div>
  `
}
