# Copyright 2014 IBM Corp.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock
from oslo.config import cfg
from oslo.serialization import jsonutils

from nova.api.openstack import api_version_request as api_version
from nova import test
from nova.tests.unit.api.openstack import fakes

CONF = cfg.CONF


class MicroversionsTest(test.NoDBTestCase):

    @mock.patch("nova.api.openstack.APIRouterV21.api_extension_namespace",
                return_value='nova.api.v3.test_extensions')
    def test_microversions_no_header(self, mock_namespace):
        app = fakes.wsgi_app_v21(init_only='test-microversions')
        req = fakes.HTTPRequest.blank('/v2/fake/microversions')
        res = req.get_response(app)
        self.assertEqual(200, res.status_int)
        resp_json = jsonutils.loads(res.body)
        self.assertEqual('val', resp_json['param'])

    @mock.patch("nova.api.openstack.api_version_request.max_api_version")
    @mock.patch("nova.api.openstack.APIRouterV21.api_extension_namespace",
                return_value='nova.api.v3.test_extensions')
    def test_microversions_with_header(self, mock_namespace, mock_maxver):
        mock_maxver.return_value = api_version.APIVersionRequest("2.3")

        app = fakes.wsgi_app_v21(init_only='test-microversions')
        req = fakes.HTTPRequest.blank('/v2/fake/microversions')
        req.headers = {'X-OpenStack-Compute-API-Version': '2.3'}
        res = req.get_response(app)
        self.assertEqual(200, res.status_int)
        resp_json = jsonutils.loads(res.body)
        self.assertEqual('val2', resp_json['param'])

    @mock.patch("nova.api.openstack.api_version_request.max_api_version")
    @mock.patch("nova.api.openstack.APIRouterV21.api_extension_namespace",
                return_value='nova.api.v3.test_extensions')
    def test_microversions_with_header_exact_match(self, mock_namespace,
                                                   mock_maxver):
        mock_maxver.return_value = api_version.APIVersionRequest("2.3")

        app = fakes.wsgi_app_v21(init_only='test-microversions')
        req = fakes.HTTPRequest.blank('/v2/fake/microversions')
        req.headers = {'X-OpenStack-Compute-API-Version': '2.2'}
        res = req.get_response(app)
        self.assertEqual(200, res.status_int)
        resp_json = jsonutils.loads(res.body)
        self.assertEqual('val2', resp_json['param'])

    @mock.patch("nova.api.openstack.api_version_request.max_api_version")
    @mock.patch("nova.api.openstack.APIRouterV21.api_extension_namespace",
                return_value='nova.api.v3.test_extensions')
    def test_microversions2_no_2_1_version(self, mock_namespace, mock_maxver):
        mock_maxver.return_value = api_version.APIVersionRequest("2.3")

        app = fakes.wsgi_app_v21(init_only='test-microversions')
        req = fakes.HTTPRequest.blank('/v2/fake/microversions2')
        req.headers = {'X-OpenStack-Compute-API-Version': '2.3'}
        res = req.get_response(app)
        self.assertEqual(200, res.status_int)
        resp_json = jsonutils.loads(res.body)
        self.assertEqual('controller2_val1', resp_json['param'])

    @mock.patch("nova.api.openstack.api_version_request.max_api_version")
    @mock.patch("nova.api.openstack.APIRouterV21.api_extension_namespace",
                return_value='nova.api.v3.test_extensions')
    def test_microversions2_later_version(self, mock_namespace, mock_maxver):
        mock_maxver.return_value = api_version.APIVersionRequest("3.1")

        app = fakes.wsgi_app_v21(init_only='test-microversions')
        req = fakes.HTTPRequest.blank('/v2/fake/microversions2')
        req.headers = {'X-OpenStack-Compute-API-Version': '3.0'}
        res = req.get_response(app)
        self.assertEqual(202, res.status_int)
        resp_json = jsonutils.loads(res.body)
        self.assertEqual('controller2_val2', resp_json['param'])

    @mock.patch("nova.api.openstack.api_version_request.max_api_version")
    @mock.patch("nova.api.openstack.APIRouterV21.api_extension_namespace",
                return_value='nova.api.v3.test_extensions')
    def test_microversions2_version_too_high(self, mock_namespace,
                                             mock_maxver):
        mock_maxver.return_value = api_version.APIVersionRequest("3.5")

        app = fakes.wsgi_app_v21(init_only='test-microversions')
        req = fakes.HTTPRequest.blank('/v2/fake/microversions2')
        req.headers = {'X-OpenStack-Compute-API-Version': '3.2'}
        res = req.get_response(app)
        self.assertEqual(404, res.status_int)

    @mock.patch("nova.api.openstack.APIRouterV21.api_extension_namespace",
                return_value='nova.api.v3.test_extensions')
    def test_microversions2_version_too_low(self, mock_namespace):
        app = fakes.wsgi_app_v21(init_only='test-microversions')
        req = fakes.HTTPRequest.blank('/v2/fake/microversions2')
        req.headers = {'X-OpenStack-Compute-API-Version': '2.1'}
        res = req.get_response(app)
        self.assertEqual(404, res.status_int)

    @mock.patch("nova.api.openstack.api_version_request.max_api_version")
    @mock.patch("nova.api.openstack.APIRouterV21.api_extension_namespace",
                return_value='nova.api.v3.test_extensions')
    def test_microversions_global_version_too_high(self, mock_namespace,
                                                   mock_maxver):
        mock_maxver.return_value = api_version.APIVersionRequest("3.5")

        app = fakes.wsgi_app_v21(init_only='test-microversions')
        req = fakes.HTTPRequest.blank('/v2/fake/microversions2')
        req.headers = {'X-OpenStack-Compute-API-Version': '3.7'}
        res = req.get_response(app)
        self.assertEqual(406, res.status_int)
        res_json = jsonutils.loads(res.body)
        self.assertEqual("Version 3.7 is not supported by the API. "
                         "Minimum is 2.1 and maximum is 3.5.",
                         res_json['computeFault']['message'])
