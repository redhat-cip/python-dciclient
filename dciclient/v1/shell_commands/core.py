import argparse
import functools
import os

# NOTE(Gonéri): we now ignore the --id parameter, we need this until the
# transition is done.
import sys

sys.argv = [a for a in sys.argv if a != "--id"]

_default_dci_cs_url = "http://127.0.0.1:5000"
_default_sso_url = "http://127.0.0.1:8180"


from dciclient.v1.api import context as dci_context
from dciclient.v1.exceptions import UsageError

from dciclient.v1.api import context as dci_context
from dciclient.v1.exceptions import UsageError


class DciCtl(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            "--dci-login",
            default=os.environ.get("DCI_LOGIN", None),
            help="DCI login or 'DCI_LOGIN' environment variable.",
        )
        self.parser.add_argument(
            "--dci-password",
            default=os.environ.get("DCI_PASSWORD", None),
            help="DCI password or 'DCI_PASSWORD' environment variable.",
        )
        self.parser.add_argument(
            "--dci-client-id",
            default=os.environ.get("DCI_CLIENT_ID", None),
            help="DCI CLIENt ID or 'DCI_CLIENT_ID' environment variable.",
        )
        self.parser.add_argument(
            "--dci-api-secret",
            default=os.environ.get("DCI_API_SECRET", None),
            help="DCI API secret or 'DCI_API_SECRET' environment variable.",
        )
        self.parser.add_argument(
            "--dci-cs-url",
            default=os.environ.get("DCI_CS_URL", _default_dci_cs_url),
            help="DCI control server url, default to '%s'." % _default_dci_cs_url,
        )
        self.parser.add_argument(
            "--sso-url",
            default=os.environ.get("SSO_URL", _default_sso_url),
            help="SSO url, default to '%s'." % _default_sso_url,
        )
        self.parser.add_argument(
            "--sso-username",
            default=os.environ.get("SSO_USERNAME", None),
            help="SSO username or 'SSO_USERNAME' environment variable.",
        )
        self.parser.add_argument(
            "--sso-password",
            default=os.environ.get("SSO_PASSWORD", None),
            help="SSO password or 'SSO_PASSWORD' environment variable.",
        )
        self.parser.add_argument(
            "--sso-token",
            default=os.environ.get("SSO_TOKEN", None),
            help="SSO token or 'SSO_TOKEN' environment variable.",
        )
        self.parser.add_argument(
            "-refresh-sso-token",
            default=False,
            required=False,
            action="store_true",
            help="Refresh the token (default: False)",
        )
        self.parser.add_argument(
            "--format",
            required=False,
            default=os.environ.get("DCI_CLI_OUTPUT_FORMAT", "table"),
            help="DCI CLI output format (default: table)",
        )
        self.subparsers = self.parser.add_subparsers()

    def __call__(self):
        args = self.parser.parse_args(sys.argv[1:])
        if args.dci_login is not None and args.dci_password is not None:
            context = dci_context.build_dci_context(
                dci_login=args.dci_login,
                dci_password=args.dci_password,
                dci_cs_url=args.dci_cs_url,
            )
        elif (
            args.sso_url is not None
            and args.sso_username is not None
            and args.sso_password is not None
        ) or args.sso_token is not None:
            context = dci_context.build_sso_context(
                args.dci_cs_url,
                args.sso_url,
                args.sso_username,
                args.sso_password,
                args.sso_token,
                refresh=args.refresh_sso_token,
            )
        elif args.dci_client_id is not None and args.dci_api_secret is not None:
            context = dci_context.build_signature_context(
                dci_cs_url=args.dci_cs_url,
                dci_client_id=args.dci_client_id,
                dci_api_secret=args.dci_api_secret,
            )
        else:
            raise UsageError(
                "Missing options --dci-login and --dci-password or "
                "--dci-client-id and dci-api-secret."
            )
        context.format = format
        kwargs = {
            k: v
            for k, v in vars(args).items()
            if k
            not in [
                "func",
                "dci_password",
                "dci_login",
                "dci_client_id",
                "dci_api_secret",
                "dci_cs_url",
                "dci_cli_output_format",
                "sso_token",
                "sso_password",
                "sso_username",
                "sso_url",
                "refresh_sso_token",
                "format",
            ]
        }

        if hasattr(args.func, "pass_context"):
            kwargs["context"] = context
        args.func(**kwargs)

    def command(self, name, help):
        parser = self.subparsers.add_parser(name, help=help)
        boolean_args = {True: "store_true", False: "store_false"}

        def decorator(func):
            if not hasattr(func, "options"):
                func.options = {}
            cb_funcs = {}
            dest = None
            for option in func.options:
                name = option["name"]
                kwargs = option["kwargs"]
                has_callback = False
                if "callback" in kwargs:
                    cb_func = kwargs["callback"]
                    del kwargs["callback"]
                    has_callback = True
                if "is_flag" in kwargs:
                    del kwargs["is_flag"]
                    default = kwargs.get("default", True)
                    kwargs["action"] = "store_false" if default else "store_true"
                    kwargs.pop("default", None)
                if "/" in name:
                    pos, neg = name.split("/")
                    group = parser.add_mutually_exclusive_group()
                    default = kwargs.pop("default", True)
                    arg = group.add_argument(pos, action=boolean_args[default])
                    dest = arg.dest
                    group.add_argument(neg, action=boolean_args[default], dest=dest)
                else:
                    arg = parser.add_argument(option["name"], **option["kwargs"])
                    dest = arg.dest
                if has_callback and dest:
                    cb_funcs[dest] = cb_func

            @functools.wraps(func)
            def decorated_func(*args, **kwargs):
                for name, cb_func in cb_funcs.items():
                    kwargs[name] = cb_func(kwargs[name])
                return func(*args, **kwargs)

            parser.set_defaults(func=decorated_func)
            return decorated_func

        return decorator

    def option(self, name, **params):
        def decorator(func):
            @functools.wraps(func)
            def decorated_func(*args, **kwargs):
                return func(*args, **kwargs)

            if not hasattr(decorated_func, "options"):
                decorated_func.options = []
            decorated_func.options.append({"name": name, "kwargs": params})
            return decorated_func

        return decorator

    argument = option

    def pass_obj(self, func):
        @functools.wraps(func)
        def decorated_func(*args, **kwargs):
            return func(*args, **kwargs)

        decorated_func.pass_context = True
        return decorated_func
