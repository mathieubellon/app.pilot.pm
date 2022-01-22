import datetime

from django.core.exceptions import ValidationError
from django.forms.fields import DateTimeField, BaseTemporalField, SplitDateTimeField


class NaiveDateTimeField(DateTimeField):
    # Override to orevent Conversion to the current timezone
    def prepare_value(self, value):
        return value

    def to_python(self, value):
        """
        Validates that the input can be converted to a datetime. Returns a
        Python datetime.datetime object.
        """
        if value in self.empty_values:
            return None
        if isinstance(value, datetime.date):
            return datetime.datetime(value.year, value.month, value.day)
        return super(BaseTemporalField, self).to_python(value)


class NaiveSplitDateTimeField(SplitDateTimeField):
    def compress(self, data_list):
        if data_list:
            # Raise a validation error if time or date is empty
            # (possible if SplitDateTimeField has required=False).
            if data_list[0] in self.empty_values:
                raise ValidationError(self.error_messages['invalid_date'], code='invalid_date')
            if data_list[1] in self.empty_values:
                raise ValidationError(self.error_messages['invalid_time'], code='invalid_time')
            return datetime.datetime.combine(*data_list)
        return None
