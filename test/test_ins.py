# coding: utf-8
import loggus
import pywss
import unittest

loggus.SetLevel(loggus.PANIC)


class Repo1:
    def __init__(self):
        self.value = "repo1"


class Repo2:
    def __init__(self, *args, **kwargs):
        self.value = "repo2"


class Repo3:
    def __init__(self, value="repo3"):
        self.value = value


class Repo4:
    def __init__(self, value):
        self.value = value or "repo4"


class Repo5:
    def __init__(self, value: int):
        self.value = value or "repo5"


class Repo6:
    def __init__(self, app: pywss.App):
        self.value = "repo6"


class TestBase(unittest.TestCase):

    def test_ins(self):
        repo1 = Repo1()
        app = pywss.App()
        self.assertEqual(app.ins(repo1), repo1)

    def test_ins_cls(self):
        class Service:
            def __init__(
                    self,
                    repo1: Repo1,
                    repo2: Repo2,
                    repo3: Repo3,
                    repo4: Repo4,
                    repo5: Repo5,
                    repo6: Repo6,
            ):
                self.repo1 = repo1
                self.repo2 = repo2
                self.repo3 = repo3
                self.repo4 = repo4
                self.repo5 = repo5
                self.repo6 = repo6

        class View:
            def __init__(self, service: Service):
                self.service = service

        app = pywss.App()
        view: View = app.ins(View)
        self.assertEqual(view.service.repo1.value, "repo1")
        self.assertEqual(view.service.repo2.value, "repo2")
        self.assertEqual(view.service.repo3.value, "repo3")
        self.assertEqual(view.service.repo4.value, "repo4")
        self.assertEqual(view.service.repo5.value, "repo5")
        self.assertEqual(view.service.repo6.value, "repo6")

    def test_ins_func(self):
        class Service:
            def __init__(self):
                self.value = "service"

        def View(
                service: Service,
                repo1: Repo1,
                repo2: Repo2,
                repo3: Repo3,
                repo4: Repo4,
                repo5: Repo5,
                repo6: Repo6,
        ):
            self.assertEqual(service.value, "service")
            self.assertEqual(repo1.value, "repo1")
            self.assertEqual(repo2.value, "repo2")
            self.assertEqual(repo3.value, "repo3")
            self.assertEqual(repo4.value, "repo4")
            self.assertEqual(repo5.value, "repo5")
            self.assertEqual(repo6.value, "repo6")

        app = pywss.App()
        app.ins(View)


if __name__ == '__main__':
    unittest.main()
