import datetime


class DateTimeModel(object):
    default_fields = ('year',
                    'month',
                    'day',
                    'iso')

    extra_fields = ('hours',
                  'minutes',
                  'seconds',
                  'name')

    all_fields = tuple(set(default_fields + extra_fields))


    def __init__(self, the_time):
        """Expects `the_time` to be an instance of datetime.datetime."""
        self.timestamp = the_time
        self.include_time = False
        self.name = None


    def update_date(self, year, month, day=None):
        # datetime.datetime is immutable, so create a new one with the
        # updated values
        if day is None:
            day = self.timestamp.day

        new_timestamp = datetime.datetime(
                year=year,
                month=month,
                day=day,
                hour=self.timestamp.hour,
                minute=self.timestamp.minute,
                second=self.timestamp.second,
                microsecond=self.timestamp.microsecond,
                tzinfo=self.timestamp.tzinfo)

        self.timestamp = new_timestamp


    def set_include_time(self, should_include):
        self.include_time = should_include

    @property
    def year(self):
        return self.timestamp.year

    @property
    def month(self):
        return self.timestamp.month

    @property
    def day(self):
        return self.timestamp.day

    @property
    def hours(self):
        return self.timestamp.hour

    @property
    def minutes(self):
        return self.timestamp.minute

    @property
    def seconds(self):
        return self.timestamp.second

    @property
    def iso(self):
        return self.timestamp.isoformat()


class DateTimeRangeModel(object):

    def __init__(self, duration_microseconds):
        self.duration = datetime.timedelta(microsecond=duration_microseconds)

        utc_now = datetime.datetime.utcnow()
        utc_then = utc_now + self.duration

        if utc_now > utc_then:
            self.start = utc_then
            self.end = utc_now
        else:
            self.start = utc_now
            self.end = utc_then
