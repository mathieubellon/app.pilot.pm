import logging

from django.test.runner import DiscoverRunner


class NoLogsTestRunner(DiscoverRunner):
    """ disabling all logging below CRITICAL.
        usage: add  TEST_RUNNER = "pilot.utils.test.NoLogsTestRunner"` to your settings file
    """

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        # disable logging below CRITICAL while testing
        logging.disable(logging.CRITICAL)

        return super(NoLogsTestRunner, self).run_tests(test_labels, extra_tests, **kwargs)
