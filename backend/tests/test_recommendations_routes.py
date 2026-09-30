from app.recommendations.routes import router


def test_recommendations_route_is_registered():
    routes = [
        route
        for route in router.routes
        if getattr(route, "path", None) == "/recommendations"
    ]

    assert routes

    route = routes[0]

    assert "GET" in route.methods


def test_recommendations_route_has_expected_endpoint():
    routes = [
        route
        for route in router.routes
        if getattr(route, "path", None) == "/recommendations"
    ]

    assert len(routes) == 1
    assert routes[0].endpoint.__name__ == "recommendations"
