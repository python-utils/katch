from katch import Catcher, catch


class TestCatcher:

    @staticmethod
    def test_catcher_with_returned_string(app, client):

        Catcher(app=app, envelope="error", code="status_code").add_scenarios(
            catch(IndexError).with_status_code(400).and_return("Out of bound"),
        )

        @app.route("/break-something")
        def break_list():
            my_list = ["foo"]
            return my_list[1]

        response = client.get("/break-something")
        error = response.json.get("error")
        code_from_body = response.json.get("status_code")
        assert 400 == response.status_code == code_from_body
        assert "Out of bound" == error

    @staticmethod
    def test_catcher_with_blueprint(app, blueprint, client):
        Catcher(app=blueprint, envelope="error", code="status_code").add_scenarios(
            catch(IndexError).with_status_code(400).and_return("Out of bound"),
        )

        @blueprint.route("/break-something")
        def break_list():
            my_list = ["foo"]
            return my_list[1]

        app.register_blueprint(blueprint)

        response = client.get("/api/v1/break-something")
        print(response.data)
        error = response.json.get("error")
        code_from_body = response.json.get("status_code")
        assert 400 == response.status_code == code_from_body
        assert "Out of bound" == error

    @staticmethod
    def test_catcher_with_first_scenario_taking_over(app, blueprint, client):
        @blueprint.route("/break-something")
        def break_list():
            my_list = ["foo"]
            return my_list[1]

        app.register_blueprint(blueprint)

        Catcher(app=app, envelope="error", code="status_code").add_scenarios(
            catch(IndexError).with_status_code(400).and_return("App says hi"),
        )

        Catcher(app=blueprint, envelope="error", code="status_code").add_scenarios(
            catch(IndexError).with_status_code(400).and_return("Blueprint says hi"),
        )

        response = client.get("/api/v1/break-something")
        print(response.data)
        error = response.json.get("error")
        code_from_body = response.json.get("status_code")
        assert 400 == response.status_code == code_from_body
        assert "App says hi" == error

    @staticmethod
    def test_catcher_with_stringified_exception(app, client):
        Catcher(app=app, envelope="message").add_scenarios(
            catch(ArithmeticError).with_status_code(401).and_stringify(),
        )

        @app.route("/break-something")
        def break_math():
            a, b = 1, 0
            return a / b

        response = client.get("/break-something")
        message = response.json.get("message")
        code_from_body = response.json.get("code")
        assert 401 == response.status_code == code_from_body
        assert "division by zero" == message

    @staticmethod
    def test_catcher_with_callable_return_value(app, client):
        Catcher(app=app, envelope="error", code=None).add_scenario(
            catch(TypeError).with_status_code(418).and_call(
                lambda e: dict(
                    msg="I'm a teapot",
                    err=str(e),
                )
            )
        )

        @app.route("/break-something")
        def break_concat():
            first_name, last_name = "John", None
            return first_name + " " + last_name

        response = client.get("/break-something")
        error = response.json.get("error")
        assert 418 == response.status_code
        assert type(error) == dict
        assert "I'm a teapot" == error.get("msg")
        assert error.get("err")
        assert not response.json.get("code")

    @staticmethod
    def test_catcher_with_user_defined_exception(app, client):

        class WoeWoeWoeException(Exception):
            def __init__(self, num_1, num_2):
                self.num_1 = num_1
                self.num_2 = num_2

            @property
            def custom_message(self):
                return f"Woe woe woe! Whatever you're trying to do with {self.num_1} and {self.num_2} won't fly"

        def eval_func(e):
            return e.custom_message

        Catcher(app=app, envelope="error").add_scenarios(
            catch(WoeWoeWoeException).with_status_code(403).and_call(eval_func)
        )

        @app.route("/break-something")
        def break_math():
            x, y = 1, 0
            try:
                return x / y
            except ArithmeticError:
                raise WoeWoeWoeException(x, y)

        response = client.get("/break-something")
        error = response.json.get("error")
        assert 403 == response.status_code
        assert "Woe woe woe! Whatever you're trying to do with 1 and 0 won't fly" == error

    @staticmethod
    def test_catcher_without_envelope(app, client):
        incident_id = "94c375c6-9f9d-4da4-a0cc-e5aa3e7a765c"
        Catcher(app=app, envelope=None).add_scenarios(
            catch(TypeError).with_status_code(500).and_call(
                lambda e: dict(
                    msg="Something went wrong",
                    incident_id=incident_id
                )
            ),
        )

        @app.route("/break-something")
        def break_concat():
            return "" + None

        response = client.get("/break-something")
        body = response.json
        assert 500 == response.status_code
        assert "Something went wrong" == body.get("msg")
        assert incident_id == body.get("incident_id")

    @staticmethod
    def test_catcher_with_lazy_loading(app, client):

        catcher = Catcher(envelope="error")
        catcher.add_scenario(
            catch(IndexError).with_status_code(400).and_return("Out of bound"),
        )
        catcher.add_scenarios(
            catch(ArithmeticError).with_status_code(400).and_stringify(),
        )
        catcher.init_app(app)

        @app.route("/break-something")
        def break_list():
            my_list = ["foo"]
            return my_list[1]

        response = client.get("/break-something")
        error = response.json.get("error")
        assert 400 == response.status_code
        assert "Out of bound" == error

    @staticmethod
    def test_catcher_with_lazy_loading_and_pass_scenarios_to_catcher_constructor(app, client):

        catcher = Catcher(
            envelope="error",
            scenarios=[
                catch(IndexError).with_status_code(400).and_return("Out of bound"),
                catch(ArithmeticError).with_status_code(400).and_stringify(),
            ]
        )
        catcher.init_app(app)

        @app.route("/break")
        def break_list():
            my_list = ["foo"]
            return my_list[1]

        response = client.get("/break")
        error = response.json.get("error")
        assert 400 == response.status_code
        assert "Out of bound" == error

    @staticmethod
    def test_catcher_with_multiple_exceptions_in_scenario(app, client):

        Catcher(
            app=app,
            envelope="msg",
            scenarios=[
                catch(IndexError, ArithmeticError).with_status_code(401).and_return("Out of the question"),
            ]
        )

        @app.route("/break-list")
        def break_list():
            my_list = ["foo"]
            return my_list[1]

        @app.route("/break-math")
        def break_math():
            x, y, = 1, 0
            return x / y

        response_1 = client.get("/break-list")
        error_1 = response_1.json.get("msg")
        response_2 = client.get("/break-math")
        error_2 = response_2.json.get("msg")
        assert response_1.status_code == response_1.status_code == 401
        assert error_1 == error_2 == "Out of the question"
