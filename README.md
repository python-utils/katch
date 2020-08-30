<div align="center">

[![Codefresh build status]( https://g.codefresh.io/api/badges/pipeline/python-utils/katch-ci%2Fkatch-ci?type=cf-1&key=eyJhbGciOiJIUzI1NiJ9.NWY0YjE1YTU2NDgwMzU1N2UxNjViMzhj.gaE2miSJx_85nbwyKnesXkXNRTBKw597DtOGTjlf6iU)]( https://g.codefresh.io/pipelines/edit/new/builds?id=5f4b1650109c4f7cadc8beb0&pipeline=katch-ci&projects=katch-ci&projectId=5f4b161b64131f72fc953e6b)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://katch-ci-artifacts.s3.us-east-2.amazonaws.com/5f4b1650109c4f7cadc8beb0/master/5f4b2d7d0c37bab6e74732f7/coverage.svg"></a>
</div>

<h2 align="center">Katch - declarative error handling for Flask</h2>


*Katch* is a declarative way to manage your error handling in a Flask server.
While Flask already possesses error handling capabilities, which are technically Pythonic,
it often becomes cumbersome to keep track of where errors are handled.

## Usage

### Simple usage

```python
from flask import Flask
from katch import Catcher, catch

app = Flask(__name__)
catcher = Catcher(app=app, envelope="error")
catcher.add_scenario(
    catch(IndexError).with_status_code(400).and_return_string("Out of bound")
)

@app.route("/break-list")
def break_list():
    my_list = ["foo"]
    return my_list[1]
```

Calling the endpoint above with `curl 127.0.0.1:5000/break-list` will yield the following:
```json
{"error": "Out of bound"}
```

### Response Evaluation

*Katch* scenarios currently support three different response evaluation types: 

1. Returning a constant (e.g., a string containing the appropriate message for the scenario)
1. Returning a string representation of the raised exception
1. Returning a value from a callable

#### Respond with a Constant 

```python
app = Flask(__name__)
catcher = Catcher(app=app, envelope="error")
catcher.add_scenarios(
    catch(IndexError).with_status_code(400).and_return_string("Out of bound"),
    catch(TypeError).with_status_code(418).and_return_string("Type violation"),
)
```

#### Respond with a Stringified Exception

```python
app = Flask(__name__)
catcher = Catcher(app=app, envelope="error")
catcher.add_scenarios(
    catch(ArithmeticError).with_status_code(500).and_stringify(),
)

@app.route("/break-math")
def break_math():
    x, y = 1, 0
    return x / y
```

Calling the endpoint above with `curl 127.0.0.1:5000/break-math` will yield the following:
```json
{"error": "division by zero"}
```

#### Respond from a Callable

You can respond by calling a function that evaluates the returned error to the client on runtime.
This can be particularly handy if you have message formatting requirements, your exception classes
might be handling the formatting themselves, or any other reason to control the evaluation of the
response the client receives on a given error handler.

```python
class NoSoupForYouError(Exception):
    def __init__(self, name):
        self.name = name

    @property
    def custom_message(self):
        return f"No soup for you, {self.name}"

Catcher(app=app, envelope="error").add_scenarios(
    catch(NoSoupForYouError).with_status_code(403).and_call(lambda e: e.custom_message)
)

@app.route("/break-something")
def break_something():
    name = request.args.get("name")
    if name in ["Jerry", "Jason"]:
        raise NoSoupForYouError(name)
    return jsonify({"soup": "Minestrone"})
```

### Envelope Responses

By default, all responses will be returned within a root `message` JSON key. You can
override this by setting your own string.

If you pass `envelope=None` explicitly when constructing your `Catcher`,
error responses will not be enveloped. This is particularly useful when you want to
add more than one attribute in the root of the response JSON object (e.g., you may want
to return an enumeration of the error code, or maybe an incident ID).

```python
import uuid

class NoSoupForYouError(Exception):
    error_code = "NO_SOUP_FOR_YOU"
    def __init__(self, name, incident_id):
        self.name = name
        self.incident_id = incident_id

    @property
    def respond(self):
        return {
            msg: f"No soup for you, {self.name}",
            code: self.error_code,
            incident_id: self.incident_id
        }

Catcher(app=app, envelope=None).add_scenarios(
    catch(NoSoupForYouError).with_status_code(403).and_call(lambda e: e.custom_message)
)

@app.route("/break-something")
def break_something():
    name = request.args.get("name")
    if name in ["Jerry", "Jason"]:
        incident_id = str(uuid.uuid4())
        raise NoSoupForYouError(name, incident_id)
    return jsonify({"soup": "Minestrone"})
```

### Exception Ancestry

The library registers the scenarios as error handlers in the order you appended them to your `Catcher`.
Think of it like a `try` and `except` block with multiple exceptions.

For this reason, it wouldn't make sense to add scenarios for exceptions *after* a higher-order exception
in their ancestry tree has been registered. For example, `ZeroDivisionError` is a subclass of `ArithmeticError`,
thus the following wouldn't make sense:

```python
catcher.add_scenario(
    catch(ArithmeticError).with_status_code(400).and_return_string("Can't calculate this"),
    catch(ZeroDivisionError).with_status_code(400).and_return_string("Can't divide by 0"), # caught by the 1st scenario
)
```

## Contributing

Contributions are welcome. Please be sure to add tests and run all the necessary checks with your pull request.

First create a virtual environment:

```shell script
make venv
```

You can run all the CI checks with one command:

```shell script
make ci
```

If you'd like to run CI checks separately:

```shell script
make test               # will run the unit tests
make test-cov           # will run the unit tests with an ASCII coverage report in your shell
make test-cov-html      # will run the unit tests with an HTML report written to ./html_cov
make check-style        # will run code style checks
make check-security     # will run general security checks
make check-dependencies # will run dependency checks to scan for vulnerable dependencies
```
