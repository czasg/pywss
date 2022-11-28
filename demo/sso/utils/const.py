# coding: utf-8

class Response(dict):

    def __init__(self, code=0, msg="ok", data=None):
        super(Response, self).__init__(code=code, msg=msg, data=data)

    @property
    def code(self):
        return self["code"]

    @code.setter
    def code(self, value):
        self["code"] = value

    @property
    def msg(self):
        return self["msg"]

    @msg.setter
    def msg(self, value):
        self["msg"] = value

    @property
    def data(self):
        return self["data"]

    @data.setter
    def data(self, value):
        self["data"] = value


if __name__ == '__main__':
    resp = Response()
    resp.code = 500
    resp.msg = "invalid"
    resp.data = {"trace": "test"}
