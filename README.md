# google-analytics-scraper

Here's a simple python API to access your Google Analytics data.


## Dependencies

We use buildout to handle all the dependencies.  Just run:

```shell
python bootstrap.py
./bin/buildout
export PATH=$PWD/bin:$PATH
```


## Example

```python
import gascrape

session = gascrape.Session()
session.login(username, password)
data = session.get_page({
    'explorer-table.filter': "",
    'explorer-table.plotKeys': "[]",
    'explorer-table.rowStart': "0",
    'explorer-table.rowCount': "10",
    'id': "content-pages",
    'ds': "a2498192w4533326p4663517",
    'cid': "explorer-motionChart,explorer-table,explorer-table,timestampMessage",
    'hl': "en_US",
    'authuser': "0",
}
```


## FAQ

### Why don't you just use the Analytics API that Google provides?

The analytics API is an afterthought for Google.  For example, access
to realtime data is only in private beta.


### Why didn't you create a normal python package on pypi?

I use selenium and phantomjs for the Google login which requires nodejs so a
pure python solution wouldn't work.  Instead of a standard python egg
installable via pip, I use buildout.
