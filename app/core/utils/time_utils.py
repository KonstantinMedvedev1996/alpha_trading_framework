from datetime import datetime
from dateutil.relativedelta import relativedelta

def get_year_month(years=0, months=0):
    date = datetime.now()
    result = date + relativedelta(years=years, months=months)
    return result.strftime("%Y-%m")