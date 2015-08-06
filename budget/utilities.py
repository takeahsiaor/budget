import datetime

def get_whole_month(date):
    '''
    Given a single date, will return start and end date representing the
    first day of the current month and the first day of the next month.

    Meant to be used as a greater than or equal for start_date and a less than
    for end_date
    '''

    #Very naive. look for calendar app
    month = date.month
    year = date.year
    start_date = datetime.datetime(month=month, year=year, day=1)
    end_date = datetime.datetime(month=month+1, year=year, day=1)