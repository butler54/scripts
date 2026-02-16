#!/usr/bin/env python

import sys


def read_inputs():
    if len(sys.argv) != 3:
        print("Usage: ./email-flatten.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    return input_file, output_file

def read_file(input_file):
    try:
        with open(input_file) as f:
            return f.readlines()
    except FileNotFoundError:
        print(f"File {input_file} not found.")
        sys.exit(1)

def write_file(output_file, lines):
    with open(output_file, 'w') as f:
        for line in lines:
            f.write(line + '\n')


def clean(lines):
    emails = []
    for line in lines:
        if '@redhat.com' in line.strip():
            emails.append(line.strip())
    return emails

if __name__ == '__main__':
    input_file, output_file = read_inputs()
    emails = clean(read_file(input_file))
    write_file(output_file, emails)


# Rest of your code goes here


