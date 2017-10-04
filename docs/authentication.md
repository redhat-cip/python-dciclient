# Authentication

There are two authentication methods available:

-   Using your user credentials:
    -   Good for administrative and manual tasks,
    -   Your credentials should not be stored on a server shared with your team.
-   Using a RemoteCI credentials:
    -   To run agent tasks or scheduled tasks,
    -   Credentials can be stored on a server shared with your team,
    -   Credentials can be reset anytime by a member of the team via the CLI or the web GUI.

## User credentials authentication

Both CLI and Python bindings will accept the following environment variables:

    DCI_LOGIN=<user name>
    DCI_PASSWORD=<password>

### CLI

CLI will also accept the following parameters which take precedence over the environment variables:

    --dci-login <user name>
    --dci-password <password>

### Python bindings

To use user credentials, you need to create a client context using the `dciclient.v1.api.build_dci_context()` method.

If you pass `dci_login` and `dci_password` parameters, they will be used ; if not, environment variables will.

## Authenticating with RemoteCI credentials

To authenticate as a RemoteCI, you'll have to get the RemoteCI API Secret from either the web GUI or the CLI.

The following command will list your team's RemoteCIs:

    dcictl --dci-login me@example.com --dci-password dummy remoteci-list

You can reset this API Secret through the web GUI or the CLI at any time (both `remoteci id` and `etag` can be found when listing your team's RemoteCIs):

    dcictl --dci-login me@example.com --dci-password dummy remoteci-reset-api-secret --id <remoteci id> --etag <etag>

Both CLI and Python bindings will accept the following environment variables:

    DCI_CLIENT_ID=<remoteci id>
    DCI_API_SECRET=<remoteci api secret>

### CLI

CLI will also accept the following parameters which take precedence over the environment variables:

    --dci-client-id <remoteci id>
    --dci-api-secret <remoteci api secret>

NOTE: the CLI will automatically detect which authentication method to use. However, if both credential kinds are passed, user credentials will take precedence.

### Python bindings

To use RemoteCI credentials, you need to create a client context using the `dciclient.v1.api.build_signature_context()` method.

If you pass `dci_client_id` and `dci_api_secret` parameters, they will be used ; if not, environment variables will.
