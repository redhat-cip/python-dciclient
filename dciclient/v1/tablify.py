hor_line = u"\u2500"
left_corner_top = u"\u250C"
right_corner_top = u"\u2510"
left_side = u"\u251C"
right_side = u"\u2524"
top_connector = u"\u252C"
bottom_connector = u"\u2534"
cross = u"\u253C"
left_corner_bottom = u"\u2514"
right_corner_bottom = u"\u2518"
vertical_line = u"\u2502"


def increase_header_size(header_size):
    while header_size < 3:
        header_size += 1
    return header_size


def get_longest_header(headers):
    longest_header = headers[0]['size']
    for item in headers:
        if item['size'] > longest_header:
            longest_header = item['size']
    return longest_header


def get_headers_and_sizes_from_data(data, headers, console_width):
    headers_and_sizes = []
    for header in headers:
        size = max(map(lambda x: len(x[header]), data))
        if len(header) > size:
            size = len(header)
        headers_and_sizes.append({"size": size, "name": header})
    headers_and_sizes_adjusted = adjust_column_width_to_console(
        headers_and_sizes, console_width
    )
    return headers_and_sizes_adjusted


def adjust_column_width_to_console(headers, console_width):
    sum_of_sizes = 0
    num_of_items = 0

    for item in headers:
        sum_of_sizes += int(item["size"])
        num_of_items += 1

    console_width -= num_of_items + 1
    for item in headers:
        item["size"] = int(round(console_width * (float(item["size"]) / sum_of_sizes)))
    total_width = sum([item["size"] for item in headers])
    while total_width > console_width:
        headers[-1]["size"] -= 1
        total_width -= 1

    for item in headers:
        if item['size'] <= 2:
            longest_header = get_longest_header(headers)
            if longest_header <= 3:
                return '[]'
            item["size"] = increase_header_size(item['size'])
            for item in headers:
                if item['size'] == longest_header:
                    item['size'] -= 1
    return headers


def format_line(headers, line_position):
    line = []
    for header in headers:
        column_width = header["size"]
        line.append(hor_line * int(column_width))
    if line_position == "top":
        line = left_corner_top + top_connector.join(line) + right_corner_top
    if line_position == "separator":
        line = left_side + cross.join(line) + right_side
    if line_position == "bottom":
        line = left_corner_bottom + bottom_connector.join(line) + right_corner_bottom
    return line


def split_strings(data_row):
    substrings = []
    for string in data_row:
        substrings.append(string.split("\n"))
    return substrings


def create_line_content(substrings):
    lines = []
    line = []
    max_length = max([len(item) for item in substrings])
    i = 0
    while max_length > 0:
        for item in substrings:
            try:
                line.append(item[i])
            except IndexError:
                line.append(" ")
            continue
        lines.append(line)
        line = []
        max_length -= 1
        i += 1

    return lines


def format_data_line(row, headers):
    data_row = []
    for header in headers:
        column_width = header["size"]
        data_row.append(adjust_text(row[header["name"]], column_width))
    substrings = split_strings(data_row)
    data_line = format_text(headers, substrings)
    return data_line


def format_headers_line(headers):
    headers_row = []
    for header in headers:
        column_width = header["size"]
        headers_row.append(adjust_text(header["name"], column_width))
    substrings = split_strings(headers_row)
    headers_line = format_text(headers, substrings)
    return headers_line


def format_text(headers, substrings):
    headers_sizes = [header["size"] for header in headers]
    row_to_print = []
    final_data = []
    line = create_line_content(substrings)
    for item in line:
        i = 0
        for string in item:
            column_width = headers_sizes[i]
            row_to_print.append(string.ljust(column_width - 1).rjust(column_width))
            i += 1
        final_data.append(
            vertical_line + vertical_line.join(row_to_print) + vertical_line
        )
        row_to_print = []
    return final_data


def _data_to_string(data):
    new_data = []
    for item in data:
        new_data.append({pair: str(item[pair]) for pair in item})
    return new_data


def adjust_text(string, column_width):
    string_width = column_width - 2
    char_num_so_far = 0
    line = []
    line_to_print = []
    for word in string.split():
        if (char_num_so_far + len(word) + 1) <= string_width:
            line.append(word)
            char_num_so_far += len(word) + 1
        else:
            char_left = string_width - char_num_so_far
            if char_left == 1:
                line.append(word[char_left - 1])
            if char_left > 1:
                line.append(word[:char_left])
            line_to_print.append(" ".join(line))
            char_num_so_far = 0
            line = []
            new_word = word[int(char_left):]
            length = len(new_word)
            start = 0
            end = string_width
            while length > 0:
                if length < string_width:
                    line.append(new_word[int(start): int(start + length)])
                    char_num_so_far = length + 1
                    break
                line_to_print.append(new_word[int(start): int(end)])
                length -= string_width
                start += string_width
                end = start + string_width

    if line:
        line_to_print.append(" ".join(line))

    return "\n".join(line_to_print)


def get_default_console_width():
    try:
        from shutil import get_terminal_size

        console_width, rows = get_terminal_size()
        return console_width
    except ImportError:
        import termios
        import fcntl
        import struct
        import sys

        s = struct.pack("hh", 0, 0)
        try:
            x = fcntl.ioctl(sys.__stdout__.fileno(), termios.TIOCGWINSZ, s)
            rows, console_width = struct.unpack("hh", x)
            return console_width
        except IOError:
            return 80


def printer(lines):
    for line in lines:
        print(line)
