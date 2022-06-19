#!/bin/bash
rm -rd dist/
rm -rd build/
rm -rd bc125py.egg-info

python3 -m build
echo "BUILD DONE! Run with argument 'upload' to upload to pypi"

if [ "$1" == "upload" ]; then
	twine upload dist/*
fi
