#!/bin/sh

# run unimport
unimport ./ --ignore-init --gitignore -r

# run isort
isort ./

# run our lint script
python ./.github/workflows/lint.py

# run flynt
flynt ./ -tc

# run black
black ./

echo "Linting finished!
