# Drupal.org Patch Generation Tools

These are a series of scripts that may be helpful in contributing patches to issues in Drupal.org. Although I have used these tools extensively, these scripts are poorly documented and unlikely to be useful to anyone but myself.

## How To Use
Add this repository to your system PATH and run the scripts from a clean project git repo clone.

### Rerolling Patches
Often patches become out of date and need changes so they apply cleanly again on HEAD. The script has the option to roll back to original patch date and attempt to fast-forward to the current HEAD. If merge conflicts occur, you can resolve them manually.

```
> rerollPatch.py <drupal.org patch URL> <git branch to work with>
```

### Updating Existing Patches
If you wish to modify an existing patch (that applies cleanly) and generate an interdiff between the two patches:

```
> updatePatch.py <drupal.org patch URL> <git branch to work with>
```

Then perform the changes to the project. To then generate the new patch with interdiff:

```
> generateNewPatch.py <git branch to work with>
```

## Summary
These are poorly written, sparsely documented and likely to ruin your development environment. You probably shouldn't use these.

## License
- Drupal.org Issue / Patch Helper Tools is licensed under the MIT License:
  - http://opensource.org/licenses/mit-license.html
- Attribution is not required, but much appreciated:
  - `Drupal.org Patch Tools by Jacob Sanford`
