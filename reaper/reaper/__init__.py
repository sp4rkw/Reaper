from __future__ import absolute_import, unicode_literals
from .celery import app as celery_app
import pymysql
__all__ = ['celery_app']
pymysql.version_info=(1,3,13,"final",0)
pymysql.install_as_MySQLdb()

