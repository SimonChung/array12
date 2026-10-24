import sys
import os

def convert_cin(input_file, output_file):
    mapping = {
        'a': '1', 'b': '5*', 'c': '3*', 'd': '3', 'e': '3/',
        'f': '4', 'g': '5', 'h': '6', 'i': '8/', 'j': '7',
        'k': '8', 'l': '9', 'm': '7*', 'n': '6*', 'o': '9/',
        'p': '0/', 'q': '1/', 'r': '4/', 's': '2', 't': '5/',
        'u': '7/', 'v': '4*', 'w': '2/', 'x': '2*', 'y': '6/',
        'z': '1*', '.': '9*', '/': '0*', ';': '0', ',': '8*'
    }

    def replace_key(key):
        return "".join(mapping.get(c, c) for c in key)

    # Opening the output in write mode would truncate the input when both paths
    # name the same inode (including hard-link aliases), so check first.
    try:
        if os.path.samefile(input_file, output_file):
            raise ValueError("input and output must be different files")
    except FileNotFoundError:
        # A new output file cannot already alias the input.
        pass

    with open(input_file, 'r', encoding='utf-8') as f_in, \
         open(output_file, 'w', encoding='utf-8') as f_out:

        in_keyname = False
        in_quick = False
        in_chardef = False
        chardef_skip_header = True
        lines_to_delete = {
            '%endkey 1234567890',
            '%space_style 2',
            '%phase_auto_skip_endkey',
            '%flag_disp_full_match',
            '%flag_disp_partial_match'
        }
        for line in f_in:

            stripped = line.strip()

            if line.lstrip().startswith('#'):
                f_out.write(line)
                continue

            if stripped == '%quick begin':
                in_quick = True
                continue
            if stripped == '%quick end':
                in_quick = False
                continue
            if in_quick:
                continue

            if stripped == '%keyname begin':
                f_out.write(line)
                f_out.write("1\t1\n2\t2\n3\t3\n4\t4\n5\t5\n6\t6\n7\t7\n8\t8\n9\t9\n0\t0\n/\t↑\n*\t↓\n")
                in_keyname = True
                continue
            if stripped == '%keyname end':
                in_keyname = False
                f_out.write(line)
                continue
            if in_keyname:
                continue

            if stripped == '%chardef begin':
                in_chardef = True
                chardef_skip_header = True
                f_out.write(line)
                continue
            if stripped == '%chardef end':
                in_chardef = False
                f_out.write(line)
                continue
            if in_chardef:
                if not stripped:
                    f_out.write(line)
                    continue

                parts = stripped.split()
                is_digit_header = (
                    len(parts) == 2
                    and len(parts[0]) == 1
                    and parts[0] in '0123456789'
                    and parts[1] == parts[0]
                )
                if chardef_skip_header and is_digit_header:
                    continue

                chardef_skip_header = False
                if '\t' in line:
                    key, value = line.split('\t', 1)
                    f_out.write(f"{replace_key(key)}\t{value}")
                else:
                    parts = line.split(None, 1)
                    if len(parts) == 2:
                        key, value = parts
                        f_out.write(f"{replace_key(key)} {value}")
                    else:
                        f_out.write(line)
                continue

            if stripped in lines_to_delete:
                continue

            if not stripped:
                f_out.write(line)
                continue

            if line.startswith('%'):
                processed_line = line
                if '%ename array30' in processed_line:
                    processed_line = processed_line.replace('%ename array30', '%ename array12')
                if '%cname 行列30' in processed_line:
                    processed_line = processed_line.replace('%cname 行列30', '%cname 行列12')
                f_out.write(processed_line)
                continue

            # # Process mapping lines
            # if '\t' in line:
            #     key, value = line.split('\t', 1)
            #     f_out.write(f"{replace_key(key)}\t{value}")
            # else:
            #     # Try splitting by space if no tab
            #     parts = line.split(None, 1)
            #     if len(parts) == 2:
            #         key, value = parts
            #         # preserve original whitespace if possible
            #         # but since we don't know if it was space or tab,
            #         # we'll use a space.
            #         # Actually, most .cin files use tabs.
            #         f_out.write(f"{replace_key(key)} {value}")
            #     else:
            #         f_out.write(line)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: python {os.path.basename(sys.argv[0])} <input_file> <output_file>")
        sys.exit(1)

    convert_cin(sys.argv[1], sys.argv[2])
