#! /usr/bin/env python
"""Generates a path and interdiff after updating a patch.
"""
from gitCmds import GitRepo
import os


git = GitRepo(os.getcwd())
new_patch_filename = raw_input("Enter Patch Filename #: ")
git.diff('8.0.x', output_to_file = new_patch_filename)
