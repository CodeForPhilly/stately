Stately
================

Form-driven workflow engine. Making city government better, one form at a time.

Government, like many organizations, have a ton of processes. For example:

* Leave request
  * employee submits form, manager approves, entry is able to be looked up later
* Travel request
  * like leave request, but director must also approve, and if >$500, CFO must approve
* New hire onboarding
  * multiple tasks that can be completed asynchronously. perhaps when all 3 tasks are done, the 4th task is able to begin
* Contract
  * Document-oriented (w/signature) vs content-oriented
* Freedom of Information Act request
  * public submits form, can track its progress, assigned based on department field, can be re-assigned, auto-reply if not fulfilled in 5 business days, requests can be shared publicly like forum posts
* New-hire Indebtedness Check (ensure new hires don't owe the city money)
  * HR manager enters a candidate for employment, and reps from various departments verify that the candidate does not owe any money to the city

This project should eventually enable IT staff in government agencies to configure
workflows like these. They will generally be initiated with an HTML form, posted
to an API, which triggers other events.

[More details, API spec, etc.](https://hackpad.com/Workflow-app-ideas-3PWIAukkmki)
