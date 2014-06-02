#! /usr/bin/env python
"""Automates updating a patch.
"""
from gitCmds import GitRepo
import utilityFunctions as utilityFunctions
import os
import sys

if not len(sys.argv) > 1:
    print "Please specify a Drupal.org patch URL"
    sys.exit(1)

git = GitRepo(os.getcwd())
git.cleanup()
patch_filename = utilityFunctions.download_patch(sys.argv[1])

git.checkout(branch = 'old_patch', is_new_branch = True)
git.apply_patch(patch_filename)
git.commit('Old Patch')

git.checkout(branch = 'new_patch', is_new_branch = True)
utilityFunctions.open_diff_files_phpstorm(git.git_dir, patch_filename)
print "Ready for development in new_patch. git add new changes and run generateNewPatch.py when done."
