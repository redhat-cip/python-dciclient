# python-dciclient

The `python-dciclient` project provides both the python bindings and a CLI to the [DCI Control Server](https://github.com/redhat-cip/dci-control-server)

## Installation

The team behind the project offers repositories for Red Hat/CentOS:

- `yum -y install https://packages.distributed-ci.io/dci-release.el7.noarch.rpm`

Then simply run `yum install python-dciclient`.

As mentioned above, the package provides two things:

- The CLI: a `dcictl` command is provided. For more details `dcictl --help`.
- The API: a python module one can use to interact with a control server (`dciclient.v1.api.*`)

## Credentials

Admitting one has valid credentials to use the DCI Control Server platform, there are two way to specify those informations while using dcictl:

- A dcirc file:

A file where the necessary credentials are stored. This file needs then to be sourced before using `dcictl`. Example:

```
export DCI_LOGIN=foo
export DCI_PASSWORD=bar
export DCI_CS_URL=https://api.distributed-ci.io
```

or using the API secret method:

```
export DCI_CLIENT_ID=<client_type>/<client_id>
export DCI_API_SECRET=<api_secret>
export DCI_CS_URL=https://api.distributed-ci.io
```

Where `client_type` can currently be `remoteci` or `feeder`

Which will allow the user to run the command: `dcictl team-list`

- At the command line level:

One can pass those informations on the CLI level. Example: `dcictl --dci-login jdoe --dci-password jdoe --dci-cs-url 'https://api.distributed-ci.io' team-list`
or `dcictl --dci-client-id <client_type>/<client_id> --dci-api-secret <api_secret> --dci-cs-url 'https://api.distributed-ci.io' team-list`

Where `client_type` can currently be `remoteci` or `feeder`

For RemoteCIs or Feeders please use the API Secret to authenticate.

## List of available commands

Run `dcictl --help` command to see the list of the available commands

```
Commands:
  component-attach-issue       Attach an issue to a component.
  component-create             Create a component.
  component-delete             Delete a component.
  component-file-delete        Delete a component file.
  component-file-download      Retrieve a component file.
  component-file-list          List files attached to a component.
  component-file-show          Show a component file.
  component-file-upload        Attach a file to a component.
  component-list               List all components.
  component-list-issue         List all component attached issues.
  component-show               Show a component.
  component-status             Show an overview of the last jobs associated...
  component-unattach-issue     Unattach an issue from a component.
  component-update             Update a component.
  file-delete                  Delete a file.
  file-list                    List all files.
  file-show                    Show a file.
  job-attach-issue             Attach an issue to a job.
  job-delete                   Delete a job.
  job-list                     List all jobs.
  job-list-issue               List all job attached issues.
  job-list-test                List all tests attached to a job.
  job-output                   Show the job output.
  job-recheck                  Recheck a job.
  job-results                  List all job results.
  job-show                     Show a job.
  job-unattach-issue           Unattach an issue from a job.
  jobdefinition-annotate       Annotate a jobdefinition.
  jobdefinition-attach-test    Attach a test to a jobdefinition.
  jobdefinition-create         Create a jobdefinition.
  jobdefinition-delete         Delete a jobdefinition.
  jobdefinition-list           List all jobdefinitions.
  jobdefinition-list-test      List tests attached to a jobdefinition.
  jobdefinition-set-active     Annotate a jobdefinition.
  jobdefinition-show           Show a jobdefinition.
  jobdefinition-unattach-test  Unattach a test to a jobdefinition.
  jobdefinition-update         Update a jobdefinition.
  jobstate-list                List all jobstates.
  jobstate-show                Show a jobstate.
  purge                        Purge soft-deleted resources.
  remoteci-attach-test         Attach a test to a remoteci.
  remoteci-create              Create a remoteci.
  remoteci-delete              Delete a remoteci.
  remoteci-get-data            Retrieve data field from a remoteci.
  remoteci-list                List all remotecis.
  remoteci-list-test           List tests attached to a remoteci.
  remoteci-refresh-keys        Refresh a remoteci key pair.
  remoteci-reset-api-secret    Reset a remoteci api secret.
  remoteci-show                Show a remoteci.
  remoteci-unattach-test       Unattach a test to a remoteci.
  remoteci-update              Update a remoteci.
  team-create                  Create a team.
  team-delete                  Delete a team.
  team-list                    List all teams.
  team-show                    Show a team.
  team-update                  Update a team.
  test-create                  Create a test.
  test-delete                  Delete a test.
  test-list                    List all tests.
  test-show                    Show a test.
  topic-attach-team            Attach a team to a topic.
  topic-create                 Create a topic.
  topic-delete                 Delete a topic.
  topic-list                   List all topics.
  topic-list-team              List teams attached to a topic.
  topic-show                   Show a topic.
  topic-unattach-team          Unattach a team from a topic.
  user-create                  Create a user.
  user-delete                  Delete a user.
  user-list                    List all users.
  user-show                    Show a user.
  user-update                  Update a user.
```

## License

Apache 2.0

## Author Information

Distributed-CI Team <distributed-ci@redhat.com>
