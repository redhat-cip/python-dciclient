# python-dciclient

## Installation

One should retrieve the package available at
https://packages.distributed-ci.io/dci-release.el7.noarch.rpm and install it.

Then simply run `yum install python-dciclient`.

## Example

```python
#!/usr/bin/env python
import dciclient.v1.api.context as dci_context
import dciclient.v1.api.job as dci_job
import dciclient.v1.api.jobstate as dci_jobstate
import dciclient.v1.api.file as dci_file
import io

# Basic function that simulates a test run and log creation
def execute_testing(content=None):
    with io.open('test.log', 'w') as f:
        f.write(unicode(content))
    return True

# Our DCI connection
dci_context = dci_context.build_dci_context(
    'http://127.0.0.1',
    'remoteci_1',
    'welcome')

# RemoteCI id and Topic id -- probably better to be dynamically passed in
remoteci_id = 'fd6c285c-fa57-4aa8-a8b3-c68a4acdfa9c'
topic_id = 'fe145e49-992a-4843-a44f-b058c7a05261'

# schedule the job and pull down data
job = dci_job.schedule(dci_context, remoteci_id=remoteci_id, topic_id=topic_id).json()
job_id = job['job']['id']
job_full_data = dci_job.get_full_data(dci_context, job_id)

# create initial jobstate of pre-run
jobstate = dci_jobstate.create(dci_context, 'pre-run', 'Initializing the environment', job_id)
print "This is where we'd do some stuff to init the environment"

# update the jobstate to start the job run
dci_jobstate.create(dci_context, 'running', 'Running the test', job_id)
jobstate_id = dci_context.last_jobstate_id
print "This is where we'd run some tests"
result = execute_testing(content=job_full_data)

# read our testing log and push to the DCI control server
with io.open('test.log', encoding='utf-8') as f:
    content = f.read(20 * 1024 * 1024) # default file size is 20MB
    dci_file.create(dci_context, 'test.log', content, 'text/plain', jobstate_id)

# Check if our test passed successfully
print "Submit result"
if result:
    final_status = 'success'
else:
    final_status = 'failure'

# Set final job state based on test pass/fail
dci_jobstate.create(dci_context, final_status,  "Job has been processed.", job_id)
```
