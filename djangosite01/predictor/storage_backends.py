from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
import os

class StaticStorage(S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'

class MediaStorage(S3Boto3Storage):
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False

class DataStorage(S3Boto3Storage):
    location = 'data'
    default_acl = 'public-read'
    file_overwrite = False