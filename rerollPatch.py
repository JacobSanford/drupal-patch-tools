#! /usr/bin/env python
"""Automates the repetitive parts of rerolling a patch.
"""
from gitCmds import GitRepo
import os
import sys
import utilityFunctions as utilityFunctions

if not len(sys.argv) > 1:
    print "Please specify a Drupal.org patch URL"
    sys.exit(1)

yes_values_list = set(['yes', 'y', 'ye', ''])

git = GitRepo(os.getcwd())
git.cleanup()
print "Downloading patch..."
patch_filename = utilityFunctions.download_patch(sys.argv[1])
print "Attempting to apply patch..."
patch_result_output = git.patch(patch_filename, dry_run = True)

if 'hunk FAILED' in patch_result_output:
    print "Patch does not apply cleanly!"
    print "Checking if patch applies cleanly at post date..."
    patch_date = raw_input("Enter the patch date: ")
    hash_to_checkout = git.get_dated_commit_hash(patch_date)
    print "Looks like " + hash_to_checkout + ' is the commit we need to roll back to...'
    project_string = raw_input("Enter a project string for branch: ")
    git.checkout(
                 branch = project_string,
                 is_new_branch = True,
                 commit_hash = hash_to_checkout
                 )
    patch_result_output = git.patch(patch_filename, dry_run = True)
    if 'hunk FAILED' in patch_result_output:
        print "Patch doesn't apply cleanly on OLD hash, restart and try an older date."
        sys.exit(1)
    else:
        print 'Patch applied cleanly on OLD hash, applying patch with git'
        git.apply_patch(patch_filename)
        choice = raw_input("Wish to continue and rebase? ").lower()
        if choice in yes_values_list:
            thread_url = raw_input("Thread URL (with comment anchor)? ")
            git.commit('Applying patch from ' + thread_url)
            utilityFunctions.open_rebase_conflicts_aptana(
                                                          git.git_dir,
                                                          patch_filename,
                                                          git.rebase()
                                                          )
            print "Rebase paused, add files and rebase --continue"
            sys.exit(1)
        print "Exiting due to concerns."
        sys.exit(1)
else :
    print "Patch applies cleanly, reverting working directory."
    git.cleanup()
