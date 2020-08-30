from katch import Catcher, catch


class TestCatcher:

    @staticmethod
    def test_catcher_with_returned_string(app, client):

        Catcher(app=app, envelope="error").add_scenarios(
            catch(IndexError).with_status_code(400).and_return_string("Out of bound"),
        )

        @app.route("/break-something")
        def break_list():
            my_list = ["foo"]
            return my_list[1]

        response = client.get("/break-something")
        error = response.json.get("error")
        assert 400 == response.status_code
        assert "Out of bound" == error

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
        assert 401 == response.status_code
        assert "division by zero" == message

    @staticmethod
    def test_catcher_with_callable_return_value(app, client):
        Catcher(app=app, envelope="error").add_scenario(
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
        assert "can only concatenate str (not \"NoneType\") to str" == error.get("err")

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
            catch(IndexError).with_status_code(400).and_return_string("Out of bound"),
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
                catch(IndexError).with_status_code(400).and_return_string("Out of bound"),
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
