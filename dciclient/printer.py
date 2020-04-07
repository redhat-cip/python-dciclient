from dciclient.v1 import utils


def print_response(response, format, verbose):
    if response.status_code == 204:
        utils.print_json({"id": id, "message": "resource deleted."})
    else:
        utils.format_output(response, format, verbose=verbose)
