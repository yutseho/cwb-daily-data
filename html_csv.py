import datetime
import requests
import urllib
import csv
from bs4 import BeautifulSoup
from datetime import timedelta

# url ex:    "https://e-service.cwb.gov.tw/HistoryDataQuery/DayDataController.do?command=viewMain&station=C0A520&stname=%25E5%25B1%25B1%25E4%25BD%25B3&altitude=48m&datepicker=2022-04-01"
URL_PREDIX = "https://e-service.cwb.gov.tw/HistoryDataQuery/DayDataController.do?command=viewMain"

DATE_FORMAT = "%Y-%m-%d"

TARGET_COL = [0, 7, 6]   # ObsTime, WD, WS

def html_to_csv(targets, station_code, is_merge):
    try:
        for date_list, url, csv_file in targets:
            print("processing {} ...".format(date_list))
            filename = station_code + ".csv" if is_merge else csv_file
            #print("url {} csv_file {}".format(url, csv_file))
            response = requests.get(url)
            html_page = response.text

            soup = BeautifulSoup(html_page, 'html.parser')

            # find <table>
            tables = soup.find_all("table")
            if len(tables) != 2:
                print("unexpected html_page: {}".format(url))
                continue

            for index, table in enumerate(tables):
                #print("--- Table {}".format(index))
                if index == 0:
                    continue

                with open(filename, "a", encoding="utf-8-sig", newline="") as file:
                    writer = csv.writer(file)

                    # find <tr>
                    table_rows = table.find_all("tr")
                    for row in table_rows:
                        row_data = date_list[:]

                        if row.find_all("th"):                     # <th> data
                            continue
                            #table_headings = row.find_all("th")
                            #for th in table_headings:
                            #    row_data.append(th.text.strip())
                        else:                                      # <td> data
                            table_data = row.find_all("td")

                            subrow = []
                            for td in table_data:
                                subrow.append(td.text.strip())
                            for i in TARGET_COL:
                                row_data.append(subrow[i])

                        writer.writerow(row_data)
                        #print(",".join(row_data))
    except Exception as e:
        print("html_to_csv err: {}".format(e))
        return

def isTimeFormat(time_str):
    try:
        time.strptime(time_str, DATE_FORMAT)
        return True
    except ValueError:
        return False

def daterange(start_date, end_date):
    try:
        for n in range(1+int((end_date - start_date).days)):
            yield start_date + timedelta(n)
    except Exception as e:
        print("daterange err: {}".format(e))

def process(station_code, start_date, end_date, is_merge):
    import json
    with open("stations.json", encoding="utf-8-sig") as f:
        stations = json.load(f)

    codes = []
    if station_code == "all":
        codes = list(stations.keys())
    else:
        if station_code not in stations:
            print("station {} not exists".format(station_code))
            return
        codes.append(station_code)
    print("codes {}".format(codes))

    targets = []
    try:
        for code in codes:
            obj = stations[code]

            name = obj["name"]
            tmp = urllib.parse.quote(name.encode('utf8'))
            stname = tmp.replace("%", "%25")    # ?

            url_prefix = URL_PREDIX
            url_prefix += ("&station="+ code)
            url_prefix += ("&stname="+ stname)
            url_prefix += ("&altitude="+ str(obj["altitude"]) + "m")

            for single_date in daterange(start_date, end_date):
                date_list = [single_date.year, single_date.month, single_date.day]

                date_str = single_date.strftime(DATE_FORMAT)
                url = url_prefix + "&datepicker=" + date_str
                csv_file = code + "-" + name + "-" + date_str + ".csv"

                targets.append((date_list, url, csv_file))
    except Exception as e:
        print("process err: {}".format(e))
        return

    html_to_csv(targets, station_code, is_merge)

station_code = input("input station code: ")
start_str = input("input start date (YYYY-MM-DD): ")
end_str = input("input end date (YYYY-MM-DD): ")
merge_str = input("merge csv (n/Y): ")

start_date = datetime.datetime.strptime(start_str, DATE_FORMAT)
end_date = datetime.datetime.strptime(end_str, DATE_FORMAT)

is_merge = False if merge_str=='n' else True

process(station_code, start_date, end_date, is_merge)