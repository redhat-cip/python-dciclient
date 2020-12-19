from dciclient.v1 import utils


def print_response(response, format, headers, verbose):
    if response and response.status_code != 204:
        utils.format_output(response, format, headers=headers, verbose=verbose)
