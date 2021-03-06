#! /usr/bin/env python
"""A custom library used to interact with Git repositories.

In the future most of these functions could be refactored into
using a more standard library such as GitPython."""

import os
import subprocess


class GitRepo:
    def __init__(self, git_dir):
        self.git_dir = git_dir

    def apply_patch(self, patch_filename):
        """Apply a patch to a git repo from an external file. Returns the git binary return code."""
        p = subprocess.Popen(
            [
                'git',
                'apply',
                '--index',
                patch_filename,
            ], cwd=self.git_dir)
        p.wait()
        return p.returncode

    def checkout(self, branch='8.0.x', is_new_branch=False, commit_hash=False):
        """Checkout a branch in a git repository. Returns the git binary return code."""
        command_list = ['git', 'checkout']
        if is_new_branch:
            command_list.extend(['-b'])
        command_list.extend([branch])
        if commit_hash:
            command_list.extend([commit_hash])
        p = subprocess.Popen(command_list, cwd=self.git_dir)
        p.wait()
        return p.returncode

    def check_old_new_correct(self):
        """
        Check if branch names are correct and sane to proceed with an interdiff. Returns BOOL if safe to succeed.

        This method assumes a bit of a hokey formalism that I use : when updating existing patches, I checkout and
        commit the old patch in a branch 'old_patch' and then check out into a new branch named 'new_patch' to
        continue the work. By standardizing the branch names, I can later generate diffs and interdiffs
        automatically."""
        p = subprocess.Popen(
            [
                'git',
                'branch',
            ],
            cwd=self.git_dir,
            stdout=subprocess.PIPE)
        p.wait()
        branch_list_output = p.stdout.read()
        if 'old_patch' in branch_list_output and '* new_patch' in branch_list_output:
            return True
        return False

    def cleanup(self):
        """Clean up the current git repository - reset back to HEAD and discard changes."""
        self.other_command(['rebase', '--abort'])
        self.other_command(['merge', '--abort'])
        self.checkout()
        self.delete_all_not_checkedout_branches()
        self.other_command(['stash'])
        self.pull()
        self.delete_patch_files()
        self.delete_interdiffs()
        return True

    # Returns either the diff text OR a return code if you specify a filename
    # in output_to_file.
    def diff(self, compare_branch, output_to_file=''):
        """Generate a diff between repository branches. Returns the diff or success code regarding file write."""
        output_handle = False
        if output_to_file:
            output_handle = open(output_to_file, "w")
        output_target = subprocess.PIPE if not output_to_file else output_handle
        p = subprocess.Popen(
            [
                'git',
                'diff',
                compare_branch,
            ],
            cwd=self.git_dir,
            stdout=output_target)
        p.wait()
        if output_to_file:
            output_handle.close()
            return p.returncode
        return p.stdout.read()

    def commit(self, commit_message):
        """Commit the current staged changes to the repository."""
        p = subprocess.Popen(
            [
                'git',
                'commit',
                '-m',
                commit_message,
            ],
            cwd=self.git_dir)
        p.wait()
        return p.returncode

    def delete_all_not_checkedout_branches(self):
        """Delete all branches of the repository, except the one which is currently checked out."""
        for cur_branch in self.not_checkedout_branches():
            self.delete_branch(cur_branch)
        return True

    def not_checkedout_branches(self):
        """Get a list of all branches in the repository that are not checked out. Returns a list of branch names."""
        branch_list = []
        p = subprocess.Popen(
            [
                'git',
                'branch',
            ],
            cwd=self.git_dir,
            stdout=subprocess.PIPE)
        p.wait()
        for line in p.stdout:
            if not line.startswith('*'):
                branch_list.append(line.strip())
        return branch_list

    def delete_branch(self, branch_name):
        """Delete a branch from the repository. Returns the git binary return code."""
        p = subprocess.Popen(
            [
                'git',
                'branch',
                '-D',
                branch_name,
            ],
            cwd=self.git_dir)
        p.wait()
        return p.returncode

    def other_command(self, command_list):
        """Perform another git command not defined as a method in this class. Returns the git binary return code."""
        run_command = ['git']
        run_command.extend(command_list)
        p = subprocess.Popen(run_command, cwd=self.git_dir)
        p.wait()
        return p.returncode

    def rebase(self, branch='8.0.x'):
        """Perform a rebase from another branch in the repository. Returns the stdout of the rebase."""
        p = subprocess.Popen(
            [
                'git',
                'rebase',
                branch,
            ],
            cwd=self.git_dir,
            stdout=subprocess.PIPE)
        p.wait()
        return p.stdout.read()

    def pull(self, remote='origin', branch_name='8.0.x'):
        """Pull data from a remote branch. Returns the git binary return code."""
        p = subprocess.Popen(
            [
                'git',
                'pull',
                remote,
                branch_name
            ],
            cwd=self.git_dir)
        p.wait()
        return p.returncode

    def patch(self, patch_filename, dry_run=False):
        """Apply a patch to the repository from a file. Returns the stdout of the operation."""
        if dry_run:
            p = subprocess.Popen(
                [
                    'git',
                    'apply',
                    '--check',
                    patch_filename,
                ],
                cwd=self.git_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            p.wait()
            return p.stderr.read()
        else:
            p = subprocess.Popen(
                [
                    'git',
                    'apply',
                    '--index',
                    patch_filename
                ],
                cwd=self.git_dir,
                stdout=subprocess.PIPE)
            p.wait()
            return p.stdout.read()

    def delete_patch_files(self):
        """Delete all files in the repository path that end in '.patch'."""
        file_list = [f for f in os.listdir(self.git_dir) if f.endswith(".patch")]
        for f in file_list:
            os.remove(f)

    def delete_interdiffs(self):
        """Delete all files in the repository path that start with 'interdiff' and end in '.txt'."""
        file_list = [f for f in os.listdir(self.git_dir) if f.startswith("interdiff") and f.endswith(".txt")]
        for f in file_list:
            os.remove(f)

    def get_dated_commit_hash(self, date_string):
        """Get the commit hash that was HEAD on the date provided."""
        p = subprocess.Popen(
            [
                'git',
                'log',
                '--format=%H',
                '-n', '1',
                '--before="' + date_string + '"',
            ],
            cwd=self.git_dir,
            stdout=subprocess.PIPE)
        p.wait()
        return p.stdout.read().rstrip()
