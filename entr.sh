#!/usr/bin/env bash
# Shim wrapper around entr because I cannot reliably expect any non-Nix system
# to have things installed declaratively like a competent system would -_-
#
# Usage: ./entr.sh file1 file2 -- command to run

dashIndex=0
for (( i=1; i<=$#; i++ )); do
	if [[ ${!i} == "--" ]]; then
		dashIndex=$i
		break
	fi
done

files=( "${@:1:$((dashIndex-1))}" )
command=( "${@:$((dashIndex+1))}" )

if command -v entr >/dev/null 2>&1; then
	echo "${files[@]}" | entr -nrz "${command[@]}"
else
	echo "No entr found, not doing live reload." >&2
	exec "${command[@]}"
fi
