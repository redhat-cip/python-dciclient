# python-dciclient

The `python-dciclient` project provides both the python bindings and a CLI to the [DCI Control Server](https://github.com/redhat-cip/dci-control-server)

## Installation

The team behind the project offers repositories for Red Hat/CentOS:

- `yum -y install https://packages.distributed-ci.io/dci-release.el7.noarch.rpm`

Then simply run `yum install python2-dciclient` for Python 2 or `yum install python3-dciclient` for Python 3.

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
  component-create             Create a component.
  component-delete             Delete a component.
  component-file-delete        Delete a component file.
  component-file-download      Retrieve a component file.
  component-file-list          List files attached to a component.
  component-file-show          Show a component file.
  component-file-upload        Attach a file to a component.
  component-list               List all components.
  component-show               Show a component.
  component-status             Show an overview of the last jobs associated...
  component-update             Update a component.
  file-delete                  Delete a file.
  file-list                    List all files.
  file-show                    Show a file.
  job-delete                   Delete a job.
  job-list                     List all jobs.
  job-output                   Show the job output.
  job-recheck                  Recheck a job.
  job-results                  List all job results.
  job-show                     Show a job.
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
  remoteci-create              Create a remoteci.
  remoteci-delete              Delete a remoteci.
  remoteci-get-data            Retrieve data field from a remoteci.
  remoteci-list                List all remotecis.
  remoteci-refresh-keys        Refresh a remoteci key pair.
  remoteci-reset-api-secret    Reset a remoteci api secret.
  remoteci-show                Show a remoteci.
  remoteci-update              Update a remoteci.
  team-create                  Create a team.
  team-delete                  Delete a team.
  team-list                    List all teams.
  team-show                    Show a team.
  team-update                  Update a team.
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

## dci-vault

If you want to store secrets in your YAML configuration files
(settings or inventories), you can use the `dci-vault` command to do
so. The various agents will then decrypt the secrets
transparently. For example:

```ShellSession
$ source dcirc.sh
$ echo -n 42 | dci-vault encrypt_string --stdin-name answer
Reading plaintext input from stdin. (ctrl-d to end input)
answer: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          36373332616633313866333234303166616237613332316534393834663934663463353433363464
          6363626133323036383939633566383139373636633533390a316363393437653663363538343730
          65333862633131353030353137636236663036656264393638353464343138623664323731613331
          6466636637393865380a336365633465633037623935633866366562373732356635343361353334
          3732
Encryption successful
```

`dci-vault` is a thin layer on top of `ansible-vault` so all the
sub-commands of `ansible-vault` are available.

## License

Apache 2.0

## Author Information

Distributed-CI Team <distributed-ci@redhat.com>
