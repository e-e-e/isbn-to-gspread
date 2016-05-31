# ISBN to Google spreadsheet

Enables you to quickly look up metadata associated with an ISBN and append it to a google spreadsheet. The books isbn, title, author, year, and publisher, are stored in as a new row.
*note:* google spreadsheets have 1000 rows by default. If you do not initially remove these the app will start appending rows at 1001.

This has been build to be used with the iPhone application [iScanWeb](https://itunes.apple.com/us/app/iscan-scan-barcodes-to-web/id443235962?mt=8). This enables users to quickly scan barcodes of books to share the metadata.

To configure the iScanWeb app:

> Form Name = isbnform

> Form Field = isbn

> Start Url = the url pointing to this app

This has been developed to help with cataloguing the library at [Frontyard](www.frontyardprojects.org/library).

## installation

```sh 
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt

```

requires a config.ini

```conf

[server]
server_port = defaultport
images_dir = /dir/of/static/images/directory
css_dir = /dir/of/css/files

[authentication]
google_speadsheet = url.to.google.speadsheet 
google_credentials = /path/to/credentials.json
isbndb_key = yourkeyforisbndb.com

```