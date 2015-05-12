#! /usr/bin/env python
"""Generates a path and interdiff after updating a patch.
"""
from gitCmds import GitRepo
import os
import sys
import glob

git = GitRepo(os.getcwd())

## Check if we're in new_patch branch and if old_patch exists
if not git.check_old_new_correct():
    print "Something is wrong with the branches, are you on new_patch? Exiting."
    sys.exit(1)

## Make sure before commit that old_patch and new_patch diff is zero.
if not git.diff('old_patch') == '':
    print "Something is wrong : the new_patch HEAD and old_patch are different"

print "Committing changes to new_patch"
git.commit('New Patch')

for patch_filename in glob.glob('*.patch'):
    print patch_filename

issue_no = raw_input("Enter The Issue #: ")
issue_slug = raw_input("Enter The Issue Slug: ")
arch_extra_info = raw_input("Enter The Arch/Extra Info: ")
old_patch_no = raw_input("Enter The Old Patch Comment #: ")
new_patch_no = raw_input("Enter The New Patch Comment #: ")
new_patch_filename = "-".join(
                              [
                               issue_no,
                               issue_slug,
                               new_patch_no,
                               arch_extra_info
                               ]
                              ) + '.patch'
interdiff_filename = "_".join(
                              [
                               'interdiff',
                               issue_no,
                               old_patch_no + '-' + new_patch_no
                               ]
                              ) + '.txt'

git.diff('8.0.x', output_to_file = new_patch_filename)
git.diff('old_patch', output_to_file = interdiff_filename)

print "Done."
