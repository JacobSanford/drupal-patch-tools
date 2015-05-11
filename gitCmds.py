#! /usr/bin/env python
"""git interface.
"""

import os
import subprocess

class GitRepo:
    def __init__(self, git_dir):
        self.git_dir = git_dir

    def apply_patch(self, patch_filename):
        p = subprocess.Popen([
                         'git',
                         'apply',
                         '--index',
                         patch_filename
                       ], cwd = self.git_dir)
        p.wait()
        return p.returncode

    def checkout(self, branch ='8.0.x', is_new_branch = False, commit_hash = False):
        command_list = ['git', 'checkout']
        if is_new_branch : command_list.extend(['-b'])
        command_list.extend([branch])
        if commit_hash : command_list.extend([commit_hash])
        p = subprocess.Popen( command_list, cwd = self.git_dir)
        p.wait()
        return p.returncode

    # This method assumes a bit of a hokey formalism that I use : when updating
    # existing patches, I checkout and commit the old patch in a branch
    # 'old_patch' and then check out into a new branch named 'new_patch' to
    # continue the work. By standardizing the branch names, I can later
    # generate diffs and Interdiffs automatically. @see generateDiffInterDiff
    def check_old_new_correct(self):
        p = subprocess.Popen([
                         'git',
                         'branch'
                       ], cwd = self.git_dir, stdout = subprocess.PIPE)
        p.wait()
        branch_list_output = p.stdout.read()
        if 'old_patch' in branch_list_output and '* new_patch' in branch_list_output :
            return True
        return False

    def cleanup(self):
        self.other_command(['rebase', '--abort'])
        self.other_command(['merge', '--abort'])
        self.checkout()
        self.delete_all_not_checkedout_branches()
        self.other_command(['stash'])
        self.pull()
        self.delete_patch_files()
        self.delete_interdiffs()
        return True

    # Returns either the diff text OR a returncode if you specify a filename
    # in output_to_file.
    def diff(self, compare_branch, output_to_file = False):
        if output_to_file : output_handle = open(output_to_file, "w")
        output_target = subprocess.PIPE if not output_to_file else output_handle
        p = subprocess.Popen([
                         'git',
                         'diff',
                         compare_branch
                       ], cwd = self.git_dir, stdout = output_target)
        p.wait()
        if output_to_file :
            output_handle.close()
            return p.returncode
        return p.stdout.read()

    def commit(self, commit_message):
        p = subprocess.Popen([
                         'git',
                         'commit',
                         '-m',
                         commit_message
                       ], cwd = self.git_dir)
        p.wait()
        return p.returncode

    def delete_all_not_checkedout_branches(self):
        for cur_branch in self.not_checkedout_branches():
            self.delete_branch(cur_branch)
        return True

    def not_checkedout_branches(self):
        branch_list = []
        p = subprocess.Popen([
                         'git',
                         'branch'
                       ], cwd = self.git_dir, stdout = subprocess.PIPE)
        p.wait()
        for line in p.stdout:
            if not line.startswith('*'):
                branch_list.append(line.strip())
        return branch_list

    def delete_branch(self, branch_name):
        p = subprocess.Popen([
                         'git',
                         'branch',
                         '-D',
                         branch_name
                       ], cwd = self.git_dir)
        p.wait()
        return p.returncode

    def other_command(self, command_list):
        run_command = ['git']
        run_command.extend(command_list)
        p = subprocess.Popen(run_command, cwd = self.git_dir)
        p.wait()
        return p.returncode

    def rebase(self, branch = '8.0.x'):
        p = subprocess.Popen([
                         'git',
                         'rebase',
                         branch
                       ], cwd = self.git_dir, stdout = subprocess.PIPE)
        p.wait()
        return p.stdout.read()

    def pull(self, remote = 'origin', branch_name = '8.0.x'):
        p = subprocess.Popen([
                         'git',
                         'pull',
                         remote,
                         branch_name
                       ], cwd = self.git_dir)
        p.wait()
        return p.returncode

    def patch(self, patch_filename, dry_run = False):
        if dry_run:
            p = subprocess.Popen([
                             'git',
                             'apply',
                             '--check',
                             patch_filename
                           ], cwd = self.git_dir, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            p.wait()
            return p.stderr.read()
        else :
            p = subprocess.Popen([
                             'git',
                             'apply',
                             '--index',
                             patch_filename
                           ], cwd = self.git_dir, stdout = subprocess.PIPE)
            p.wait()
            return p.stdout.read()

    def delete_patch_files(self):
        filelist = [ f for f in os.listdir(self.git_dir) if f.endswith(".patch") ]
        for f in filelist:
            os.remove(f)

    def delete_interdiffs(self):
        filelist = [ f for f in os.listdir(self.git_dir) if f.startswith("interdiff") and f.endswith(".txt")]
        for f in filelist:
            os.remove(f)

    def get_dated_commit_hash(self, date_string):
        p = subprocess.Popen([
                         'git',
                         'log',
                         '--format=%H',
                         '-n', '1',
                         '--before="' + date_string + '"'
                       ], cwd = self.git_dir, stdout = subprocess.PIPE)
        p.wait()
        return p.stdout.read().rstrip()
