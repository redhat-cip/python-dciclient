from dciclient.v1 import utils


def print_response(response, format, verbose):
    if response and response.status_code != 204:
        utils.format_output(response, format, verbose=verbose)
