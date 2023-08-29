# coding: utf-8
import json
import pywss
import unittest


class TestBase(unittest.TestCase):

    def test_split_method_route(self):
        self.assertEqual(
            pywss.utils.split_method_route("GET"),
            ("GET", "/")
        )
        self.assertEqual(
            pywss.utils.split_method_route("POST/api/v1"),
            ("POST", "/api/v1")
        )
        self.assertEqual(
            pywss.utils.split_method_route("POST///cza"),
            ("POST", "/cza")
        )

    def test_safe_encoder(self):
        self.assertEqual(
            json.loads(json.dumps({"typ": "str"}, default=pywss.utils.safe_encoder)),
            {"typ": "str"}
        )
        self.assertEqual(
            json.loads(json.dumps({"typ": {None}}, default=pywss.utils.safe_encoder)),
            {"typ": "{None}"}
        )

    def test_merge_dict(self):
        self.assertEqual(
            pywss.utils.merge_dict({"typ": "1"}, {"une": "1"}),
            {"typ": "1", "une": "1"}
        )
        self.assertEqual(
            pywss.utils.merge_dict({"typ": "1"}, {"typ": "2"}),
            {"typ": "1"}
        )
        self.assertEqual(
            pywss.utils.merge_dict({"typ": {"a": "a"}}, {"typ": {"b": "b"}}),
            {"typ": {"a": "a", "b": "b"}}
        )
        self.assertEqual(
            pywss.utils.merge_dict({"typ": {"a": "a"}}, {"typ": {"a": "b"}}),
            {"typ": {"a": "a"}}
        )


if __name__ == '__main__':
    unittest.main()
