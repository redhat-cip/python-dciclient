# python-dciauth

DCI authentication module used by dci-control-server and python-dciclient

This section shows example programs written in python that illustrate how to work with Signature Version 4 in DCI. The algorithm used by dciauth is similar to [Signature Version 4 in AWS](http://docs.aws.amazon.com/general/latest/gr/sigv4-signed-request-examples.html).

## Signing example:

```python
import requests

from dciauth.signature import Signature
from dciauth.request import AuthRequest

auth_request = AuthRequest(endpoint='/api/v1/jobs')
headers = Signature(request=auth_request).generate_headers('remoteci', 'client_id', 'secret')
r = requests.get('http://127.0.0.1:5000/api/v1/jobs', headers=headers)
assert r.status_code == 200
```

Here we are signing the GET request with `secret` and generate headers used by `requests` module.

## Validation example


```python
    from flask import request

    from dciauth.signature import Signature
    from dciauth.request import AuthRequest

    auth_request = AuthRequest(
        method=request.method,
        endpoint=request.path,
        payload=request.get_json(silent=True),
        headers=request.headers,
        params=request.args.to_dict(flat=True)
    )
    signature = Signature(request=auth_request)
    if not signature.is_valid('secret'):
        raise Exception("Authentication failed: signature invalid")
    if signature.is_expired():
        raise Exception("Authentication failed: signature expired")
```

## License

Apache 2.0


## Author Information

Distributed-CI Team  <distributed-ci@redhat.com>


