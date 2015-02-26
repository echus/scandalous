"""
WSGI config for scandalous project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

### Patch for pymysql usage
#!/usr/bin/env python
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
### End patch

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scandalous.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
