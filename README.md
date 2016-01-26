# python-dciclient

## Installation

One should retrieve the package available at http://dci.enovance.com/dci-release.el7.noarch.rpm and install it.

Then simply run yum install python-dciclient.

## Example

```python
from dciclient.v1.api import context as dcicontext
from dciclient.v1.api import job as dcijob
from dciclient.v1.api import jobstate as dcijobstate
from dciclient.v1.api import file as dcifile

ctx = dcicontext.build_dci_context(
    'http://127.0.0.1',
    'your_account',
    'your_password')

remoteci_id = 'e86ab5ba-695b-4337-a163-161e20b20f56'
job = dcijob.schedule(ctx, remoteci_id=remoteci_id).json()
job_full_data = dcijob.get_full_data(ctx, job_id)

dcijobstate.create(ctx, 'pre-run', 'Initializing the environment', job_id)
do_some_operations()

jobstate = dcijobstate.create(ctx, 'running', 'Running the test', job_id)
result == run_the_deployment(job_full_data)

with codecs.open('test.log', encoding='utf-8') as f:
    content = f.read(20 * 1024 * 1024)
    dcifile.create(ctx, 'to_send.log', content, 'text/plain', jobstate_id)

if result:
    final_status = 'success'
else:
    final_status = 'failure'

dcijobstate.create(ctx, final_status, 'Job has been proceeded.', job_id)
```
