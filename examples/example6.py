from pywss import Pywss, route


@route("/ws/chat")
def index(request, data):
    return "Pywss support wss protocol"


if __name__ == '__main__':
    ws = Pywss(__name__,
               address="0.0.0.0",
               port=8866,
               ssl_key="www.czasg.xyz.key",
               ssl_pem="www.czasg.xyz.pem")
    ws.serve_forever()
