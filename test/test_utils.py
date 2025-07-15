# coding: utf-8
import json
import pywss
import unittest

from pywss.utils import resolve_refs


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

    def test_query(self):
        data = {"name": "pywss", "version": pywss.__version__}
        query = pywss.Query(data)
        name = query.fetch("name")
        self.assertEqual(name, data["name"])
        name, version = query.fetch("name", "version")
        self.assertEqual(name, data["name"])
        self.assertEqual(version, data["version"])
        name, version, typ = query.fetch("name", "version", "typ")
        self.assertEqual(name, data["name"])
        self.assertEqual(version, data["version"])
        self.assertEqual(typ, None)


class TestResolveRefs(unittest.TestCase):
    def setUp(self):
        # 通用的 definitions 供多个测试使用
        self.definitions = {
            "Person": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"}
                }
            },
            "Address": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"}
                }
            },
            "NestedRef": {
                "type": "object",
                "properties": {
                    "person": {"$ref": "#/definitions/Person"}
                }
            }
        }

    def test_non_ref_schema(self):
        """测试不包含引用的普通schema"""
        schema = {"type": "string"}
        result = resolve_refs(schema, self.definitions)
        self.assertEqual(result, schema)

    def test_simple_ref(self):
        """测试简单引用解析"""
        schema = {"$ref": "#/definitions/Person"}
        expected = self.definitions["Person"]
        result = resolve_refs(schema, self.definitions)
        self.assertEqual(result, expected)

    def test_nested_ref(self):
        """测试嵌套引用"""
        schema = {
            "type": "object",
            "properties": {
                "user": {"$ref": "#/definitions/Person"},
                "address": {"$ref": "#/definitions/Address"}
            }
        }
        expected = {
            "type": "object",
            "properties": {
                "user": self.definitions["Person"],
                "address": self.definitions["Address"]
            }
        }
        result = resolve_refs(schema, self.definitions)
        self.assertEqual(result, expected)

    def test_ref_in_list(self):
        """测试列表中的引用"""
        schema = [
            {"type": "string"},
            {"$ref": "#/definitions/Person"},
            {"type": "integer"}
        ]
        expected = [
            {"type": "string"},
            self.definitions["Person"],
            {"type": "integer"}
        ]
        result = resolve_refs(schema, self.definitions)
        self.assertEqual(result, expected)

    def test_deeply_nested_ref(self):
        """测试多层嵌套的引用"""
        schema = {"$ref": "#/definitions/NestedRef"}
        expected = {
            "type": "object",
            "properties": {
                "person": self.definitions["Person"]
            }
        }
        result = resolve_refs(schema, self.definitions)
        self.assertEqual(result, expected)

    def test_multiple_refs_in_object(self):
        """测试对象中的多个引用"""
        schema = {
            "person1": {"$ref": "#/definitions/Person"},
            "person2": {"$ref": "#/definitions/Person"},
            "other": {"type": "boolean"}
        }
        expected = {
            "person1": self.definitions["Person"],
            "person2": self.definitions["Person"],
            "other": {"type": "boolean"}
        }
        result = resolve_refs(schema, self.definitions)
        self.assertEqual(result, expected)

    def test_non_dict_non_list(self):
        """测试非字典非列表的输入"""
        schema = "plain string"
        result = resolve_refs(schema, self.definitions)
        self.assertEqual(result, schema)

    def test_missing_ref(self):
        """测试引用不存在的情况"""
        schema = {"$ref": "#/definitions/NonExistent"}
        with self.assertRaises(KeyError):
            resolve_refs(schema, self.definitions)

    def test_empty_schema(self):
        """测试空schema"""
        schema = {}
        result = resolve_refs(schema, self.definitions)
        self.assertEqual(result, schema)

    def test_empty_list(self):
        """测试空列表"""
        schema = []
        result = resolve_refs(schema, self.definitions)
        self.assertEqual(result, schema)


if __name__ == '__main__':
    unittest.main()
