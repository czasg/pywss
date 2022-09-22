# coding: utf-8

class Route:

    def __init__(self, route: str):
        self.route = route
        self.route_list = []
        self.name = None
        if route[0] == "{" and route[-1] == "}":
            self.route = self.name = route[1:-1]

    @staticmethod
    def from_route(route: str):
        node = Route(route)
        for r in route.strip("/").split("/"):
            node.route_list.append(Route(r))
        return node

    def match(self, route: str) -> (bool, dict):
        resp = {}
        r = route.strip("/").split("/")
        if len(r) != len(self.route_list):
            return False, resp
        for index in range(len(r)):
            rr = r[index]
            node = self.route_list[index]  # type: Route
            if node.name:
                resp[node.name] = rr
                continue
            if rr != node.route:
                return False, resp
        return True, resp
