import netrc
import datetime
import calendar
import csv

import gascrape

def get_pageviews(session, start_date, end_date):
    start_date_txt = start_date.strftime("%Y%m%d")
    end_date_txt = end_date.strftime("%Y%m%d")

    data = session.get_page({
        '_u.date00': start_date_txt,
        '_u.date01': end_date_txt,
        'overview-graphOptions.selected': "analytics.nthMonth",
        'overview-graphOptions.primaryConcept': "analytics.pageviews",
        'id': "defaultid",
        'ds': "a2498192w4533326p4663517",
        'cid': "overview,reportHeader,timestampMessage",
        'hl': "en_US",
        'authuser': "0",
    })

    rows = data['components'][1]['graph']['lineChart']['dataTable']['rows']
    row = rows[0]
    pageviews = int(row['c'][1]['v'])
    return pageviews


def main(argv=None):
    if argv is None:
        argv = sys.argv

    username, account, password = netrc.netrc().authenticators("google.com")
    session = gascrape.Session()
    session.login(username, password)

    writer = csv.writer(sys.stdout)
    writer.writerow(["month", "page views"])
    for month in range(1, 13):
        start_date = datetime.date(2015, month, 1)
        end_day = calendar.monthrange(start_date.year, start_date.month)[1]
        end_date = datetime.date(2015, month, end_day)
        pageviews = get_pageviews(session, start_date, end_date)
        writer.writerow([start_date.strftime("%m/%Y"), pageviews])


if __name__ == '__main__':
    sys.exit(main())
