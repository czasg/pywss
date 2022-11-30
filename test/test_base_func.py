# coding: utf-8
import pywss
import unittest


class TestBase(unittest.TestCase):

    def test_openapi(self):
        self.assertEqual(
            pywss.openapi.transfer_list([]),
            {"example": []}
        )
        self.assertEqual(
            pywss.openapi.merge_dict({"1": "1", "3": "3"}, {"2": "2", "3": "3"}),
            {"1": "1", "2": "2", "3": "3"}
        )


if __name__ == '__main__':
    unittest.main()
