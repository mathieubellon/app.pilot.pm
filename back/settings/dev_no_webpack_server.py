""""This settings file is used by `inv serve` command when webpack server is not running."""

from settings.dev import *  # noqa

WEBPACK_LOADER['DEFAULT']['STATS_FILE'] = frontend_path('webpack-stats.json')
