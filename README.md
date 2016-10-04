Stately
================

Form-driven workflow engine. Making city government better, one form at a time.

Government agencies, like many organizations, have a ton of processes. If an
employee wants to attend a conference and needs travel reimbursement, their
supervisor must approve, then their director must approve, and if it costs more
than $500, the CFO must approve. New hire on-boarding consists of several steps
that can happen in parallel.

In many cases, there is already software out there -- especially in the HR world
-- that handle these processes. When they're available, you should use them.
But when there isn't software already available, or the agency doesn't have
access to it, the processes still exist; they just take place over email. Stately
is for these processes.

Eventually, we'd like Stately to have a user-friendly web interface for designing
forms and workflows. For now, it's driven by a
[configuration file](workflows/travel-request.yml) that looks like this:

```yml
name: Travel Request
states:
  - name: Not started
    actions:
      - name: Initiate
        template:
          fields:
            - name: Name
            - name: Initiator Email
            - name: Destination
            - name: Cost
            - name: Supervisor Email
        handler: |
          change_state('Awaiting Supervisor Approval')
          assign(data.supervisor_email, send_email=True)
  - name: Awaiting Supervisor Approval
    actions:
      - name: Approve
        handler: |
          if (data.cost) >= 500:
            change_state('Awaiting CFO Approval')
            assign(cfo_email, send_email=True)
          else:
            change_state('Approved')
            assign(data.initiator_email, send_email=True)
      - name: Reject
        # ...... (see the rest in workflows/travel-request.yml)
```

This renders a form that, when submitted, kicks off the `handler`, changing
the state of the request and sending emails to reviewers with unique access
tokens.

![screenshot of travel request form](http://i.imgur.com/CpCk3Is.png)

The aim of this approach is to provide a balance between configurability and
flexibility, accommodating many workflows out-of-the-box, with an option
to write basic python code for any advanced / edge-case workflows.

![screenshot of submitted travel request](http://i.imgur.com/LmQUZ1F.png)

## Example workflows
We're building with the following use cases from Philadelphia City Government
in mind. Have your own that comes to mind?
[Tell us about it](https://github.com/codeforphilly/stately/issues/new).

* Leave request
  * employee submits form, manager approves, entry is able to be looked up later
* Travel reimbursement request
  * like leave request, but director must also approve, and if >$500, CFO must approve
* New hire onboarding
  * multiple tasks that can be completed asynchronously. perhaps when all 3 tasks are done, the 4th task is able to begin
* Contract
  * Document-oriented (w/signature) vs content-oriented
* Freedom of Information Act request
  * public submits form, can track its progress, assigned based on department field, can be re-assigned, auto-reply if not fulfilled in 5 business days, requests can be shared publicly like forum posts
* New-hire Indebtedness Check (ensure new hires don't owe the city money)
  * HR manager enters a candidate for employment, and reps from various departments verify that the candidate does not owe any money to the city

## API

Brainstorming, API spec, etc. is [on a hackpad](https://hackpad.com/Workflow-app-ideas-3PWIAukkmki)

## Client usage
The client application requires [Node JS](https://nodejs.org/en/download/) to build.
Install dependencies by navigating into the `client` directory in the terminal and run:
```bash
npm install
```
Afterwards, run a local development server using:
```bash
npm start
```

## Server usage
The server application requires python. It is recommended that you create a
[virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/)
before installing dependencies. Once you've activated your virtual environment,
install dependencies by navigating to the `server` directory and running:
```bash
pip install .
```
Then setup the database using:
```bash
python src/manage.py migrate
```
Load the workflow files from the `workflows` directory into the database using:
```bash
python src/manage.py workflow_load ../workflows/*
```
Check the workflows that are loaded into the database using:
```bash
python src/manage.py workflow_list
```
Finally, run the server using:
```bash
python src/manage.py runserver
```

## Prior art
* [geekq/workflow](https://github.com/geekq/workflow)
* [viewflow](http://viewflow.io/)
