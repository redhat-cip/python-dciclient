# python-dciclient

The `python-dciclient` project provides both the python bindings and a CLI to the [DCI Control Server](https://github.com/redhat-cip/dci-control-server)

## Installation

The team behind the project offers repositories for Red Hat/CentOS:

  * `yum -y install https://packages.distributed-ci.io/dci-release.el7.noarch.rpm`

Then simply run `yum install python-dciclient`.

As mentioned above, the package provides two things:

  * The CLI: a `dcictl` command is provided. For more details `dcictl --help`.
  * The API: a python module one can use to interact with a control server (`dciclient.v1.api.*`)


## Credentials

Admitting one has valid credentials to use the DCI Control Server platform, there are two way to specify those informations while using dcictl:

  * A dcirc file:

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

  * At the command line level:

One can pass those informations on the CLI level. Example: `dcictl --dci-login jdoe --dci-password jdoe --dci-cs-url 'https://api.distributed-ci.io' team-list`
 or `dcictl --dci-client-id <client_type>/<client_id> --dci-api-secret <api_secret> --dci-cs-url 'https://api.distributed-ci.io' team-list`

Where `client_type` can currently be `remoteci` or `feeder`

For RemoteCIs or Feeders please use the API Secret to authenticate.

## List of available commands

Run `dcictl --help` command to see the list of the available commands

## License

Apache 2.0


## Author Information

Distributed-CI Team  <distributed-ci@redhat.com>
