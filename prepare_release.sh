echo "updating library version to $1"
poetry version "$1"
poetry run black setup.py
