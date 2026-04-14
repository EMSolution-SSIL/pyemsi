---
sidebar_position: 1
title: Open Workspace
---

In pyemsi, a workspace is the folder that contains your simulation files, such as mesh files, EMSolution input control files, and result files.

Opening the correct workspace is typically the first step in a pyemsi session, because the Explorer, file tabs, plotting tools, and simulation workflows all operate relative to that folder.

## Ways To Open A Workspace

There are several ways to open a workspace in pyemsi.

### From The Main Toolbar Or File Menu

Click the open-folder icon <img src="/pyemsi/img/FolderOpen.svg" alt="Open Folder icon" width="20"/> on the main toolbar, or use `File -> Open Folder...`.

This is the most direct way to open a workspace from inside the application.

### With The Keyboard Shortcut

Press `Ctrl + O` to open the folder picker immediately.

### From Windows Explorer

On Windows, you can right-click a folder and choose `Open with pyemsi`.

On Windows 11, this option may appear only after selecting `Show more options` in the context menu.

This integration is available when the `Explorer "Open with pyemsi"` option was enabled during installation. See [Installation](/docs/docs/installation) for details.

## Recent Workspaces

Once a workspace has been opened, pyemsi stores it in the recent-workspace history.

You can reopen a recent workspace in either of these ways:

1. Click the history icon <img src="/pyemsi/img/History.svg" alt="History icon" width="20"/> on the main toolbar.
2. Open `File -> Open Recent`.

This is useful when you switch between the same simulation projects frequently and want to reopen them without browsing for the folder again.