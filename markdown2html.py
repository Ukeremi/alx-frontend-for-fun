#!/usr/bin/python3
"""
markdown2html.py

A script that converts Markdown to HTML.

Usage:
    ./markdown2html.py README.md README.html

Arguments:
    input_file (str): The name of the Markdown file to convert.
        Default is "README.md".
    output_file (str): The name of the HTML file to create.
        Default is "README.html".
"""

import sys
import os.path
import re
import hashlib


def convert_bold(line):
    """
    Converts bold syntax in Markdown to HTML.

    Args:
        line (str): The Markdown line to convert.

    Returns:
        str: The converted HTML line.
    """
    # Replace the first occurrence of '**' with '<b>'
    line = line.replace('**', '<b>', 1)
    # Replace the second occurrence of '**' with '</b>'
    line = line.replace('**', '</b>', 1)
    # Replace the first occurrence of '__' with '<em>'
    line = line.replace('__', '<em>', 1)
    # Replace the second occurrence of '__' with '</em>'
    line = line.replace('__', '</em>', 1)

    return line


def convert_md5(line):
    """
    Converts MD5 syntax in Markdown to HTML.

    Args:
        line (str): The Markdown line to convert.

    Returns:
        str: The converted HTML line.
    """
    # Md5: Replace [[md5_text]] with the MD5 hash of md5_text
    md5 = re.findall(r'\[\[.+?\]\]', line)
    # Extract the content inside [[md5_text]] using capturing group
    md5_text = re.findall(r'\[\[(.+?)\]\]', line)
    # Check if there is any match for [[md5_text]]
    if md5:
        # Replace the first occurrence of [[md5_text]] with its MD5 hash
        line = line.replace(
            md5[0], hashlib.md5(
            md5_text[0].encode()
            ).hexdigest()
        )

    return line


def remove_letter_c(line):
    """
    Removes the letter 'C' or 'c' from ((text)) in Markdown.

    Args:
        line (str): The Markdown line to convert.

    Returns:
        str: The converted HTML line.
    """
    matches_c = re.findall(r'\(\(.+?\)\)', line)
    removed_c_text = re.findall(r'\(\((.+?)\)\)', line)
    if matches_c:
        # Filter characters from the first match, excluding 'C' or 'c'
        removed_c_text = ''.join(
            char for char in removed_c_text[0] if char not in 'Cc'
        )
        # Replace ((text)) with text, removing 'C' or 'c'
        line = line.replace(matches_c[0], removed_c_text)

    return line


def convert_line(line):
    """
    Converts a single line of Markdown to HTML.

    Args:
        line (str): The Markdown line to convert.

    Returns:
        str: The converted HTML line.
    """
    # Bold syntax markdown to html
    line = convert_bold(line)
    # Md5: Replace [[md5_text]] with the MD5 hash of md5_text
    line = convert_md5(line)
    # Removing the letter C: Remove 'C' or 'c' from ((text))
    line = remove_letter_c(line)

    return line


def process_line(line, html, unordered_start, ordered_start, paragraph):
    """
    Processes a single line of Markdown and writes the corresponding HTML.

    Args:
        line (str): The Markdown line to process.
        html (file): The HTML file to write to.
        unordered_start (bool): Indicates if an unordered list is open.
        ordered_start (bool): Indicates if an ordered list is currently open.
        paragraph (bool): Indicates if a paragraph is currently open.

    Returns:
        tuple: Updated values of unordered_start, ordered_start, and paragraph.
    """
    # Calculate length of each line
    length = len(line)

    # Remove leading '#' to determine heading level
    headings = line.lstrip('#')
    # Calculate heading level based on the difference in lengths
    heading_num = length - len(headings)

    # Remove leading '-' to determine if it's part of an unordered list
    unordered = line.lstrip('-')
    # Calculate length of stripped line: identify the unordered list item
    unordered_num = length - len(unordered)

    # Remove leading '*' to determine if it's part of an ordered list
    ordered = line.lstrip('*')
    # Calculate length of stripped line: identify the ordered list item
    ordered_num = length - len(ordered)

    # Headings and Lists
    if 1 <= heading_num <= 6:
        # Convert Markdown heading to HTML heading
        line = '<h{}>'.format(
            heading_num
            ) + headings.strip() + '</h{}>\n'.format(
            heading_num
        )

    if unordered_num:
        # Handle Markdown unordered list
        if not unordered_start:
            # If not inside an unordered list, open a new <ul> tag
            html.write('<ul>\n')
            unordered_start = True
        line = '<li>' + unordered.strip() + '</li>\n'
    if unordered_start and not unordered_num:
        # If no more unordered list items, close the <ul> tag
        html.write('</ul>\n')
        unordered_start = False

    if ordered_num:
        # Handle Markdown ordered list
        if not ordered_start:
            # If not inside an ordered list, open a new <ol> tag
            html.write('<ol>\n')
            ordered_start = True
        line = '<li>' + ordered.strip() + '</li>\n'
    if ordered_start and not ordered_num:
        # If no more ordered list items, close the <ol> tag
        html.write('</ol>\n')
        ordered_start = False

    if not (heading_num or unordered_start or ordered_start):
        # Handle paragraphs and line breaks
        if not paragraph and length > 1:
            # If not inside a paragraph, open a new <p> tag
            html.write('<p>\n')
            paragraph = True
        elif length > 1:
            # Insert a line break
            html.write('<br/>\n')
        elif paragraph:
            # If inside a paragraph, close the <p> tag
            html.write('</p>\n')
            paragraph = False

    if length > 1:
        # Write the line content (excluding single-character lines)
        html.write(line)

    return unordered_start, ordered_start, paragraph


def close_open_tags(html, unordered_start, ordered_start, paragraph):
    """
    Close any open unordered list, ordered list, or paragraph tags.

    Args:
        html (file): The HTML file to write to.
        unordered_start (bool): Indicates if an unordered list is open.
        ordered_start (bool): Indicates if an ordered list is currently open.
        paragraph (bool): Indicates if a paragraph is currently open.

    Returns:
        None
    """
    # Close any open unordered list tag
    if unordered_start:
        html.write('</ul>\n')
    # Close any open ordered list tag
    if ordered_start:
        html.write('</ol>\n')
    # Close any open paragraph tag
    if paragraph:
        html.write('</p>\n')


def convert_and_write_html(lines, output_file):
    """
    Converts and processes Markdown lines, then writes to the HTML file.

    Args:
        lines (iterable): Iterable containing Markdown lines.
        output_file (str): The name of the HTML file to create.

    Returns:
        None
    """
    # Open the HTML file for writing
    with open(output_file, 'w') as html:
        # Initialize flags for tracking list and paragraph states
        unordered_start, ordered_start, paragraph = False, False, False

        # Process each line in the iterable
        for line in lines:
            # Convert the Markdown line to HTML
            line = convert_line(line)
            # Process the HTML line and update list and paragraph states
            unordered_start, ordered_start, paragraph = process_line(
                line, html, unordered_start, ordered_start, paragraph
            )

        # Call the helper function to close open tags
        close_open_tags(html, unordered_start, ordered_start, paragraph)


def process_markdown(input_file, output_file):
    """
    Converts a Markdown file to HTML.

    Args:
        input_file (str): The name of the Markdown file to convert.
        output_file (str): The name of the HTML file to create.

    Returns:
        None
    """
    # Check that the Markdown file exists and is a file
    if not os.path.isfile(input_file):
        # Print an error message to stderr if the file is missing
        print('Missing {}'.format(input_file), file=sys.stderr)
        # exit with a status code of 1
        exit(1)

    # Read the Markdown file and convert to html
    with open(input_file) as readme:
        convert_and_write_html(readme, output_file)


# Check if the script is being run as the main program
if __name__ == '__main__':
    # Check the number of command-line arguments
    if len(sys.argv) < 3:
        # Print usage message to stderr if number of arguments is insufficient
        print('Usage: ./markdown2html.py README.md README.html',
              file=sys.stderr)
        # Exit with a status code of 1 to indicate an error
        exit(1)

    # Call the process_markdown function with input and output file names
    process_markdown(sys.argv[1], sys.argv[2])

    # Exit with a successful status code (0) to indicate successful execution
    exit(0)
