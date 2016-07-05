import datetime
import dateutil.parser

class DateUtils(object):
    ''' collection of random utility functions
    '''

    def get_dt_from_stamp(self, time_stamp=0):
        '''
        time_stamp : example 1454822094965
        '''
        return datetime.datetime.fromtimestamp(time_stamp/1000)

    def get_dt_from_iso(self, iso_date=''):
        '''
        iso_date : example '2016-02-07T18:06:21.695Z'
        '''
        return dateutil.parser.parse(iso_date)
