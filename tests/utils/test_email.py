# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock
import unittest

from airflow.utils import email


class TestEmail(unittest.TestCase):
    def setUp(self):
        super(TestEmail, self).setUp()

    def test_successful_send(self):
        s_mock = mock.MagicMock(name="s_mock")
        sendmail_mock = mock.MagicMock(name="sendmail_mock")
        s_mock.sendmail = sendmail_mock
        smtplib_smtp_mock = mock.MagicMock(name="mock_smtplib.smtp", return_value=s_mock)
        email.smtplib.SMTP = smtplib_smtp_mock

        email.send_email(
            "this_is_the_to@example.com",
            "this is the subject",
            "<h1>the_html_yes_I_know_it_isnt_valid</h1>"
        )

        smtplib_smtp_mock.assert_called_once()
        smtplib_smtp_mock.assert_called_with("localhost", 25)

        sendmail_mock.assert_called_once()
        self.assertEquals(sendmail_mock.mock_calls[0][1][0], "airflow@example.com")
        self.assertEquals(sendmail_mock.mock_calls[0][1][1], ["this_is_the_to@example.com"])
        self.assertTrue("this is the subject" in sendmail_mock.mock_calls[0][1][2])
        self.assertTrue("the_html_yes_I_know_it_isnt_valid" in sendmail_mock.mock_calls[0][1][2])

    def test_send_with_retries(self):
        self.invocations = 0
        def the_side_effect(*args, **kwargs):
            self.invocations += 1
            if self.invocations <= 4:
                raise Exception("simulating a failure at try " + str(self.invocations))

        s_mock = mock.MagicMock(name="s_mock")
        sendmail_mock = mock.MagicMock(name="sendmail_mock", side_effect=the_side_effect)
        s_mock.sendmail = sendmail_mock
        smtplib_smtp_mock = mock.MagicMock(name="mock_smtplib.smtp", return_value=s_mock)
        email.smtplib.SMTP = smtplib_smtp_mock

        email.send_email(
            "this_is_the_to@example.com",
            "this is the subject",
            "<h1>the_html_yes_I_know_it_isnt_valid</h1>"
        )

        self.assertEquals(smtplib_smtp_mock.call_count, 5)
        smtplib_smtp_mock.assert_called_with("localhost", 25)

        self.assertEquals(sendmail_mock.call_count, 5)
        for i in range(0, 5):
            self.assertEquals(sendmail_mock.mock_calls[i][1][0], "airflow@example.com")
            self.assertEquals(sendmail_mock.mock_calls[i][1][1], ["this_is_the_to@example.com"])
            self.assertTrue("this is the subject" in sendmail_mock.mock_calls[i][1][2])
            self.assertTrue("the_html_yes_I_know_it_isnt_valid" in sendmail_mock.mock_calls[i][1][2])


if __name__ == '__main__':
    unittest.main()
