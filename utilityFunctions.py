#! /usr/bin/env python
"""
Several helper functions related to working with patches on drupal.org"""

import subprocess
import os
import sys


def download_patch(url):
    """Download a patch file from Drupal.org. Returns the patch filename."""
    patch_filename = os.path.basename(url)
    p = subprocess.Popen(
        [
            'curl',
            '-o', patch_filename,
            url,
        ]
    )
    p.wait()
    try:
        with open(patch_filename):
            pass
    except IOError:
        print "Download Failed"
        sys.exit(1)
    return patch_filename


def open_diff_files_phpstorm(script_cwd, diff_file):
    """Open all files referenced in a diff in PHPStorm."""
    diff_file_point = open(diff_file, "r")
    files_to_open = []
    for line in diff_file_point:
        if '+++ ' in line:
            files_to_open.append(
                os.path.join(
                    script_cwd,
                    line.replace('+++ ', '').replace('b/', '').rstrip()
                )
            )
    return open_files_phpstorm(files_to_open)


def open_rebase_conflicts_phpstorm(script_cwd, patch_filename, rebase_output):
    """Open all files referenced in a rebase conflict in PHPStorm."""
    files_to_open = [os.path.join(script_cwd, patch_filename)]
    for line in rebase_output:
        if 'CONFLICT (content): Merge conflict in ' in line:
            files_to_open.append(
                os.path.join(
                    script_cwd,
                    line.replace('CONFLICT (content): Merge conflict in ', '').rstrip()
                )
            )
    print files_to_open
    return open_files_phpstorm(files_to_open)


def open_files_phpstorm(file_list):
    """Open a list of files in PHPStorm."""
    file_open_command = ['pstorm', '~/gitDev/drupal']
    file_open_command.extend(file_list)
    print "Opening files in PHPStorm:"
    print "\n".join(file_list)
    return subprocess.call(file_open_command)
