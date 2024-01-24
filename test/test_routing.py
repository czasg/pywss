# coding: utf-8
import loggus
import pywss
import unittest

loggus.SetLevel(loggus.PANIC)


class TestBase(unittest.TestCase):

    def test_routing1(self):
        # full match
        route = pywss.Route.from_route("/full/match")
        self.assertEqual(str(route), "/full/match")
        self.assertEqual(route.match("/full/match"), (True, {}))
        self.assertEqual(route.match("/full/match/fail"), (False, {}))

        # local match
        route = pywss.Route.from_route("/{k1}/{k2}")
        self.assertEqual(str(route), "/{k1}/{k2}")
        self.assertEqual(route.match("/1/2"), (True, {"k1": "1", "k2": "2"}))
        self.assertEqual(route.match("/1/2/3"), (False, {}))

    def test_routing2(self):
        route = pywss.routing.Route.from_route("/test/test/{test}")
        ok, res = route.match("/test")
        self.assertEqual(ok, False)
        ok, res = route.match("/test/test1/test")
        self.assertEqual(ok, False)
        ok, res = route.match("/test/test/test")
        self.assertEqual(ok, True)
        self.assertEqual(res, {"test": "test"})

        app = pywss.App()
        app.get("/test/", lambda ctx: ctx.write(ctx.route))
        resp = pywss.HttpTestRequest(app).get("/test")
        self.assertEqual(resp.body, "/test")
        resp = pywss.HttpTestRequest(app).get("/test/")
        self.assertEqual(resp.body, "/test/")

        app = pywss.App()
        app.get("/{test}/", lambda ctx: ctx.write(ctx.route_params["test"]))
        resp = pywss.HttpTestRequest(app).get("/123")
        self.assertEqual(resp.body, "123")
        resp = pywss.HttpTestRequest(app).get("/456/")
        self.assertEqual(resp.body, "456")

        app = pywss.App()
        app.get("*", lambda ctx: ctx.write(ctx._route))
        resp = pywss.HttpTestRequest(app).get("/123")
        self.assertEqual(resp.body, "GET")
        resp = pywss.HttpTestRequest(app).get("/456/")
        self.assertEqual(resp.body, "GET")


if __name__ == '__main__':
    unittest.main()
