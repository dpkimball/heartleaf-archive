#!/usr/bin/env bash

# debugging flag
# https://www.gnu.org/software/bash/manual/bash.html#The-Set-Builtin
# Print a trace of simple commands, for commands, case commands, select
# commands, and arithmetic for commands and their arguments or associated word
# lists after they are expanded and before they are executed. The value of the
# PS4 variable is expanded and the resultant value is printed before the command
# and its expanded arguments.
[[ -n "$DEBUG_SCRIPT" ]] && set -x

# Exit immediately if a pipeline (see Pipelines), which may consist of a single
# simple command (see Simple Commands), a list (see Lists), or a compound
# command (see Compound Commands) returns a non-zero status. The shell does
# not exit if the command that fails is part of the command list immediately
# following a while or until keyword, part of the test in an if statement,
# part of any command executed in a && or || list except the command following
# the final && or ||, any command in a pipeline but the last, or if
# the command’s return status is being inverted with !. If a compound command
# other than a subshell returns a non-zero status because a command failed
# while -e was being ignored, the shell does not exit. A trap on ERR,
# if set, is executed before the shell exits.
set -e

# check system dependencies
echo "Testing system dependencies"
command -v python3 >/dev/null 2>&1 || { echo >&2 "This project requires Python >= 3.6.1"; exit 1; }
command -v virtualenv >/dev/null 2>&1 || { echo >&2 "This project requires virtualenv"; exit 1; }

# Remove virtual directory and then recreate venv
echo "(Re)Creating the virtual environment"
rm -rf .venv/
virtualenv -p python3 .venv

# install requirements
echo "Installing python requirements into virtual environment"
.venv/bin/pip install -r requirements.txt
