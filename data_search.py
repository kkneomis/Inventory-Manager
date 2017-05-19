import dsi_calculator as dsi

def actual_sales(cfg):
    '''
    get sales and forecast data for a given cfg
    :param cfg:
    :return: json of sales/forecast data
    '''
    db  = dsi.get_db()
    cur = db.execute('select week.week_id, forecast.forecast_id, forecast.forecast_type, forecast.cfg_id, entry.entry_value \
                      from forecast, entry, week \
                      where forecast_type == "actual" \
                      and forecast.forecast_id = entry.forecast_id \
                      and week.week_id = entry.week_id \
                      and forecast.cfg_id ==  (?)', [cfg])

    sales = cur.fetchall()
    sales = clean_week(sales)

    return sales


def clean_week(data):
    '''
    Change the week name to make it digestable for Morris graphing
    data expected in json format
    '''
    for item in data:
        item['week_id'] = process(item['week_id'])
    return data


def process(string):
    '''
    Get valid date fromat from Version info
    Ex: Hard Drive - Desktop_COMM_FY17Q4W14
    Result: "2017 W44"
    '''
    month = month_string_to_number(string[:3])-1
    week = int(string[4])
    #adjust for weird fiscal year issues
    if month > 9:
        year = int(string[-2:])-1
    else:
        year = int(string[-2:])


    week = month * 4 + week
    new_string = '20%s W%s' % (year, week)
    return new_string


def month_string_to_number(string):
    m = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr':4,
         'may':5,
         'jun':6,
         'jul':7,
         'aug':8,
         'sep':9,
         'oct':10,
         'nov':11,
         'dec':12
        }
    s = string.strip()[:3].lower()

    try:
        out = m[s]
        return out
    except:
        raise ValueError('Not a month')