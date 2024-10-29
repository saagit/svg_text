#!/usr/bin/env python3
"""
Output text strings from SVG.
"""

# BSD Zero Clause License
#
# Copyright (c) 2024 Scott A. Anderson
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

# Possible template for command line tool.

import argparse
from collections.abc import Iterator
import contextlib
import os
import sys
from typing import BinaryIO

import xml.etree.ElementTree as ET

VERSION='0.1'

def progname() -> str:
    """
    Return the name of this program.
    """
    return os.path.basename(__file__)

@contextlib.contextmanager
def open_ro_with_error(filename: str) -> Iterator[tuple[BinaryIO, None]
                                                  | tuple[None, OSError]]:
    """
    Adapted from PEP 343 Example 6
    """
    try:
        if filename == '-':
            file_handle = sys.stdin.buffer
        else:
            file_handle = open(filename, 'rb')
    except IOError as err:
        yield None, err
    else:
        try:
            yield file_handle, None
        finally:
            if filename != '-':
                file_handle.close()

def parse_args() -> argparse.Namespace:
    """
    Parse the command line arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__, prog=progname(),
                                     add_help=False)
    parser.add_argument('-h', '--help',
                        help='display this help and exit',
                        action='help')
    parser.add_argument('-V', '--version',
                        help='output version information and exit',
                        action='version', version='%(prog)s v' + VERSION)
    parser.add_argument('-i', '--id', action='store_true',
                        help='Print the ID for each text element.')
    parser.add_argument('-w', '--whitespace', action='store_true',
                        help='Collapse whitespace in text strings.')
    parser.add_argument('svg_files', metavar='SVG_FILE', nargs="*",
                        help='SVG files or stdin if none provided')
    args = parser.parse_args()

    return args

def get_childrens_text(element: ET.Element) -> str:
    """
    Return a string that is the text of all children joined together.
    """
    return ''.join([child.text for child in element.iter() if child.text])

def main() -> int:
    """The main event."""
    args = parse_args()
    if not args.svg_files:
        args.svg_files = [ '-' ]

    rtn = 0
    for filename in args.svg_files:
        with open_ro_with_error(filename) as (svgfile, err):
            if err:
                print(f'{progname()}: {err.filename}: {err.strerror}',
                      file=sys.stderr)
                rtn += 1
                continue
            assert svgfile
            tree = ET.parse(svgfile)
            for element in tree.iter('{http://www.w3.org/2000/svg}text'):
                prefix = f'{element.attrib["id"]}: ' if args.id else ''
                text = get_childrens_text(element)
                if args.whitespace:
                    text = ' '.join(text.split())
                print(f'{prefix}{repr(text)}')

    return rtn

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('Keyboard interrupt', file=sys.stderr)
    except BrokenPipeError:
        print('Broken pipe', file=sys.stderr)
    sys.exit(255)
