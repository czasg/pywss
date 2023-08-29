# coding: utf-8
import pywss
import unittest


class TestBase(unittest.TestCase):

    def test_transfer_parameters(self):
        self.assertEqual(
            pywss.openapi.transfer_parameters({
                "name": "desc",
            }),
            [
                {
                    "name": "name",
                    "description": "desc",
                    "in": "query",
                    "required": False
                }
            ]
        )
        self.assertEqual(
            pywss.openapi.transfer_parameters({
                "age:required": "desc",
            }),
            [
                {
                    "name": "age",
                    "description": "desc",
                    "in": "query",
                    "required": True
                }
            ]
        )
        self.assertEqual(
            pywss.openapi.transfer_parameters({
                "age:path": "desc",
            }),
            [
                {
                    "name": "age",
                    "description": "desc",
                    "in": "path",
                    "required": False
                }
            ]
        )
        self.assertEqual(
            pywss.openapi.transfer_parameters({
                "id:path,required": "desc",
            }),
            [
                {
                    "name": "id",
                    "description": "desc",
                    "in": "path",
                    "required": True
                }
            ]
        )

    def test_transfer_content_type(self):
        self.assertEqual(
            pywss.openapi.transfer_content_type({}),
            "application/json"
        )
        self.assertEqual(
            pywss.openapi.transfer_content_type([]),
            "application/json"
        )
        self.assertEqual(
            pywss.openapi.transfer_content_type(""),
            "text/html"
        )
        self.assertEqual(
            pywss.openapi.transfer_content_type(None),
            "application/octet-stream"
        )

    def test_transfer_schema(self):
        self.assertEqual(
            pywss.openapi.transfer_schema({"typ": None}, None),
            {
                "application/json": {
                    "schema": {
                        "example": {"typ": None}
                    }
                }
            }
        )
        self.assertEqual(
            pywss.openapi.transfer_schema({"typ": None}, "custom"),
            {
                "custom": {
                    "schema": {
                        "example": {"typ": None}
                    }
                }
            }
        )

        class Field:
            default = "fieldValue"

        class Custom:
            __fields__ = {
                "fieldKey": Field
            }

        self.assertEqual(
            pywss.openapi.transfer_schema(Custom, "custom"),
            {
                "custom": {
                    "schema": {
                        "example": {
                            "fieldKey": "fieldValue"
                        }
                    }
                }
            }
        )

    def test_transfer_fields(self):
        class StringField:
            default = "fieldValue"
            type_ = str

        class IntegerField:
            default = None
            type_ = int

        class Custom:
            __fields__ = {
                "string": StringField,
                "integer": IntegerField,
            }

        self.assertEqual(
            pywss.openapi.transfer_fields(Custom()),
            {
                "string": "fieldValue",
                "integer": "integer",
            }
        )

    def test_openapi_ui_template(self):
        self.assertIsNotNone(
            pywss.openapi.openapi_ui_template(
                "", "", "", ""
            ),
        )


if __name__ == '__main__':
    unittest.main()
