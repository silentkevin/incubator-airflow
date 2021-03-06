# -*- coding: utf-8 -*-
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import unittest

import airflow.contrib.hooks.gcs_hook as gcs_hook

from airflow.exceptions import AirflowException
from apiclient.errors import HttpError

try:
    from unittest import mock
except ImportError:
    try:
        import mock
    except ImportError:
        mock = None

BASE_STRING = 'airflow.contrib.hooks.gcp_api_base_hook.{}'
GCS_STRING = 'airflow.contrib.hooks.gcs_hook.{}'

EMPTY_CONTENT = ''.encode('utf8')


class TestGCSHookHelperFunctions(unittest.TestCase):
    def test_parse_gcs_url(self):
        """
        Test GCS url parsing
        """

        self.assertEqual(
            gcs_hook._parse_gcs_url('gs://bucket/path/to/blob'),
            ('bucket', 'path/to/blob'))

        # invalid URI
        self.assertRaises(AirflowException, gcs_hook._parse_gcs_url,
                          'gs:/bucket/path/to/blob')

        # trailing slash
        self.assertEqual(
            gcs_hook._parse_gcs_url('gs://bucket/path/to/blob/'),
            ('bucket', 'path/to/blob/'))

        # bucket only
        self.assertEqual(
            gcs_hook._parse_gcs_url('gs://bucket/'), ('bucket', ''))


class TestGCSBucket(unittest.TestCase):
    def test_bucket_name_value(self):

        bad_start_bucket_name = '/testing123'
        with self.assertRaises(AssertionError):

            gcs_hook.GoogleCloudStorageHook().create_bucket(
                bucket_name=bad_start_bucket_name
            )

        bad_end_bucket_name = 'testing123/'
        with self.assertRaises(AssertionError):
            gcs_hook.GoogleCloudStorageHook().create_bucket(
                bucket_name=bad_end_bucket_name
            )


class TestGoogleCloudStorageHook(unittest.TestCase):
    def setUp(self):
        with mock.patch(BASE_STRING.format('GoogleCloudBaseHook.__init__')):
            self.gcs_hook = gcs_hook.GoogleCloudStorageHook(
                google_cloud_storage_conn_id='test'
            )

    @mock.patch(GCS_STRING.format('GoogleCloudStorageHook.get_conn'))
    def test_exists(self, mock_service):

        test_bucket = 'test_bucket'
        test_object = 'test_object'

        (mock_service.return_value.objects.return_value
         .get.return_value.execute.return_value) = {
            "kind": "storage#object",
            # The ID of the object, including the bucket name,
            # object name, and generation number.
            "id": "{}/{}/1521132662504504".format(test_bucket, test_object),
            "name": test_object,
            "bucket": test_bucket,
            "generation": "1521132662504504",
            "contentType": "text/csv",
            "timeCreated": "2018-03-15T16:51:02.502Z",
            "updated": "2018-03-15T16:51:02.502Z",
            "storageClass": "MULTI_REGIONAL",
            "timeStorageClassUpdated": "2018-03-15T16:51:02.502Z",
            "size": "89",
            "md5Hash": "leYUJBUWrRtks1UeUFONJQ==",
            "metadata": {
                "md5-hash": "95e614241516ad1b64b3551e50538d25"
            },
            "crc32c": "xgdNfQ==",
            "etag": "CLf4hODk7tkCEAE="
        }

        response = self.gcs_hook.exists(bucket=test_bucket, object=test_object)

        self.assertTrue(response)

    @mock.patch(GCS_STRING.format('GoogleCloudStorageHook.get_conn'))
    def test_exists_nonexisting_object(self, mock_service):

        test_bucket = 'test_bucket'
        test_object = 'test_object'

        (mock_service.return_value.objects.return_value
         .get.return_value.execute.side_effect) = HttpError(
            resp={'status': '404'}, content=EMPTY_CONTENT)

        response = self.gcs_hook.exists(bucket=test_bucket, object=test_object)

        self.assertFalse(response)

    @mock.patch(GCS_STRING.format('GoogleCloudStorageHook.get_conn'))
    def test_copy(self, mock_service):
        source_bucket = 'test-source-bucket'
        source_object = 'test-source-object'
        destination_bucket = 'test-dest-bucket'
        destination_object = 'test-dest-object'

        (mock_service.return_value.objects.return_value
         .get.return_value.execute.return_value) = {
            "kind": "storage#object",
            # The ID of the object, including the bucket name, object name,
            # and generation number.
            "id": "{}/{}/1521132662504504".format(
                destination_bucket, destination_object),
            "name": destination_object,
            "bucket": destination_bucket,
            "generation": "1521132662504504",
            "contentType": "text/csv",
            "timeCreated": "2018-03-15T16:51:02.502Z",
            "updated": "2018-03-15T16:51:02.502Z",
            "storageClass": "MULTI_REGIONAL",
            "timeStorageClassUpdated": "2018-03-15T16:51:02.502Z",
            "size": "89",
            "md5Hash": "leYUJBUWrRtks1UeUFONJQ==",
            "metadata": {
                "md5-hash": "95e614241516ad1b64b3551e50538d25"
            },
            "crc32c": "xgdNfQ==",
            "etag": "CLf4hODk7tkCEAE="
        }

        response = self.gcs_hook.copy(
            source_bucket=source_bucket,
            source_object=source_object,
            destination_bucket=destination_bucket,
            destination_object=destination_object
        )

        self.assertTrue(response)

    @mock.patch(GCS_STRING.format('GoogleCloudStorageHook.get_conn'))
    def test_copy_failedcopy(self, mock_service):
        source_bucket = 'test-source-bucket'
        source_object = 'test-source-object'
        destination_bucket = 'test-dest-bucket'
        destination_object = 'test-dest-object'

        (mock_service.return_value.objects.return_value
         .copy.return_value.execute.side_effect) = HttpError(
            resp={'status': '404'}, content=EMPTY_CONTENT)

        response = self.gcs_hook.copy(
            source_bucket=source_bucket,
            source_object=source_object,
            destination_bucket=destination_bucket,
            destination_object=destination_object
        )

        self.assertFalse(response)

    def test_copy_fail_same_source_and_destination(self):

        source_bucket = 'test-source-bucket'
        source_object = 'test-source-object'
        destination_bucket = 'test-source-bucket'
        destination_object = 'test-source-object'

        with self.assertRaises(ValueError) as e:
            self.gcs_hook.copy(source_bucket=source_bucket,
                               source_object=source_object,
                               destination_bucket=destination_bucket,
                               destination_object=destination_object)

        self.assertEquals(
            str(e.exception),
            'Either source/destination bucket or source/destination object '
            'must be different, not both the same: bucket=%s, object=%s' %
            (source_bucket, source_object)
        )

    def test_copy_empty_source_bucket(self):

        source_bucket = None
        source_object = 'test-source-object'
        destination_bucket = 'test-dest-bucket'
        destination_object = 'test-dest-object'

        with self.assertRaises(ValueError) as e:
            self.gcs_hook.copy(source_bucket=source_bucket,
                               source_object=source_object,
                               destination_bucket=destination_bucket,
                               destination_object=destination_object)

        self.assertEquals(
            str(e.exception),
            'source_bucket and source_object cannot be empty.'
        )

    def test_copy_empty_source_object(self):

        source_bucket = 'test-source-object'
        source_object = None
        destination_bucket = 'test-dest-bucket'
        destination_object = 'test-dest-object'

        with self.assertRaises(ValueError) as e:
            self.gcs_hook.copy(source_bucket=source_bucket,
                               source_object=source_object,
                               destination_bucket=destination_bucket,
                               destination_object=destination_object)

        self.assertEquals(
            str(e.exception),
            'source_bucket and source_object cannot be empty.'
        )

    @mock.patch(GCS_STRING.format('GoogleCloudStorageHook.get_conn'))
    def test_delete(self, mock_service):
        test_bucket = 'test_bucket'
        test_object = 'test_object'

        (mock_service.return_value.objects.return_value
         .delete.return_value.execute.return_value) = {}

        response = self.gcs_hook.delete(bucket=test_bucket, object=test_object)

        self.assertTrue(response)

    @mock.patch(GCS_STRING.format('GoogleCloudStorageHook.get_conn'))
    def test_delete_nonexisting_object(self, mock_service):
        test_bucket = 'test_bucket'
        test_object = 'test_object'

        (mock_service.return_value.objects.return_value
         .delete.return_value.execute.side_effect) = HttpError(
            resp={'status': '404'}, content=EMPTY_CONTENT)

        response = self.gcs_hook.delete(bucket=test_bucket, object=test_object)

        self.assertFalse(response)
