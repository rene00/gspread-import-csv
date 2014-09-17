gspread-import-csv
==================

Import a CSV file into Google Docs using Python.

Requires [gspread](https://github.com/burnash/gspread) & [gdata](https://pypi.python.org/pypi/gdata).

example
-------

```
$ python gspread_import_csv.py \
    --config-file=gspread_import_csv.conf \
    --csv-file=example.csv \
    --document-title="Melbourne vs North American Time"
````
