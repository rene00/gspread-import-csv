import ConfigParser as configparser
import argparse
import csv
from datetime import datetime
import gdata.docs.client
import gspread
import os
import sys

class ScriptError(StandardError):
    pass

def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('--config-file', required=True)
    parser.add_argument('--csv-file', required=True)
    parser.add_argument('--document-title', default=None, required=False)

    return parser.parse_args()

def get_config(config_file, section):
    "return config file section as a dict."

    if not os.path.exists(config_file):
        raise ScriptError('cant find config file; config_file={}'.format(
            config_file))

    ini = configparser.ConfigParser()
    config = open(config_file)
    ini.readfp(config)
    config.close()
    config = {}

    for (option, value) in ini.items(section):
        config[option] = value

    return config

def create_spreadsheet(username, password, google_docs_folder_id=None, 
        document_title=None):

    # generate default title if not supplied
    if document_title is None:
        document_title = 'Generated with {0} on {1}'.format(
                sys.argv[0], datetime.now().strftime('%Y-%m-%d'))

    docs_client = gdata.docs.client.DocsClient()
    docs_client.ClientLogin(username, password, 'Any non empty string')
    document = gdata.docs.data.Resource(type='spreadsheet', 
            title=document_title)
    resource = docs_client.CreateResource(document)

    # move document if required
    if google_docs_folder_id:
        docs_client.MoveResource(resource, 
                docs_client.GetResourceById(google_docs_folder_id))

    full_id = resource.resource_id.text # returned by gdata
    gc = gspread.login(username, password)
    gc_id = full_id[len('spreadsheet:'):]

    return gc.open_by_key(gc_id)

def main():
    args = parse_args()
    google_config = get_config(args.config_file, 'google')

    try:
        google_docs_folder_id = google_config['google_docs_folder_id']
    except IndexError:
        google_docs_folder_id = None

    fh = open(args.csv_file, 'rt')

    try:
        reader = csv.DictReader(fh)
    except IOError:
        raise ScriptError('unable to read csv file: csv_file=csv_file')
    finally:
        sh = create_spreadsheet(google_config['username'], 
                google_config['password'], 
                google_docs_folder_id=google_docs_folder_id, 
                document_title=args.document_title)
        ws = sh.get_worksheet(0)

        column_count = 1
        row_count = 1

        headers_printed = False
        for row in reader:
            for data in row.keys():
                if not headers_printed:
                    for header in list(row.keys()):
                        ws.update_cell(column_count, row_count, header)
                        row_count += 1
                    row_count = 1
                    column_count += 1
                    headers_printed = True
                ws.update_cell(column_count, row_count, row[data])
                row_count += 1
            column_count += 1
            row_count = 1

        fh.close()

if __name__ == '__main__':
    sys.exit(main())
