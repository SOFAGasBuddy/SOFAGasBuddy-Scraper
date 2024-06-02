import time
import logging
from logging.handlers import RotatingFileHandler
import mechanicalsoup
from bs4 import BeautifulSoup

LOG_TIME_FORMAT = "%Y/%m/%d %H:%M:%S "

ID_FIELD = "_ctl0:ContentPlaceHolder1:ucAuthenticate:tbxSponsorID"
ID_TYPE_FIELD = "_ctl0:ContentPlaceHolder1:ucAuthenticate:ddlSponsorType"
PLATE_NUMBER_FIELD = "_ctl0:ContentPlaceHolder1:ucAuthenticate:tbxVRN"
BALANCE_ID = "_ctl0_ContentPlaceHolder1_ucESSOPanel_lblAccountBalance"
VEHICLE_TABLE_ID="_ctl0_ContentPlaceHolder1_ucESSOPanel_dgridVehicleList"

# add a rotating handler
logger = logging.getLogger("ESSOScraper Rotating Log")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler("esso.log", maxBytes=2048000, backupCount=25)
logger.addHandler(handler)

def print_and_log(text, error=False):
    """Logs and prints with one statement"""
    print(text)
    if error:
        logger.error(time.strftime(LOG_TIME_FORMAT) + text)
    else:
        logger.info(time.strftime(LOG_TIME_FORMAT) + text)

class Vehicle:
    """Simple class to hold the relevent vehicle data"""
    def __init__(self, vrn=None, veh_type=None, status=None,
                 limit=None, available=None, exp_date=None):
        self.vrn = vrn
        self.veh_type = veh_type
        self.status = status
        self.limit = limit
        self.available = available
        self.exp_date = exp_date

def update_data(ssn, plate_number):
    """It... updates... the data..."""
    vehicle_list = []
    browser = mechanicalsoup.StatefulBrowser()
    url = "https://odin.aafes.com/esso/"
    browser.open(url)
    browser.select_form("form")
    browser[ID_FIELD] = ssn
    browser[PLATE_NUMBER_FIELD] = plate_number
    browser[ID_TYPE_FIELD] = "S"
    resp = browser.submit_selected()

    soup = BeautifulSoup(resp.text, 'html.parser')

    try:
        balance = soup.find('span', id=BALANCE_ID).string
    except AttributeError:
        return "-9999", "Failed request", "1"

    vehicles = soup.find("table", id=VEHICLE_TABLE_ID)

    first = True
    for row in vehicles.find_all("tr"):
        if first:
            first = False
            continue

        columns = row.find_all('td')
        car = Vehicle()
        if columns != []:
            car.vrn = columns[0].text.strip()
            car.veh_type = columns[1].text.strip()
            car.status = columns[2].text.strip()
            car.limit = columns[3].text.strip()
            car.available = columns[4].text.strip()
            car.exp_date = columns[5].text.strip()
        vehicle_list.append(car)

    return balance, vehicle_list, str(0)
