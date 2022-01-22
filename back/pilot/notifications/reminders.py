from django.db import models


class ReminderImpactorModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super(ReminderImpactorModel, self).save(*args, **kwargs)
        for reminder in self.reminders.all():
            reminder.tally()
