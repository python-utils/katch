class Scenario:

    status_code = 500
    is_callable = False
    stringify_exception = False

    def __init__(
        self,
        exceptions,
        func=None,
        constant=None,
        stringify_exception=False,
        status_code=500,
    ):
        self.exceptions = exceptions
        self.stringify_exception = stringify_exception
        self.func = func
        self.constant = constant
        if not stringify_exception:
            if func and hasattr(func, "__call__"):
                self.is_callable = True
        self.status_code = status_code

    def respond(self, e):
        if self.is_callable:
            return self.func(e)
        elif self.stringify_exception:
            return str(e)
        return self.constant

    def with_status_code(self, status_code):
        self.status_code = status_code
        return self

    def and_stringify(self):
        self.stringify_exception = True
        return self

    def and_return(self, constant):
        self.constant = constant
        return self

    def and_call(self, func):
        self.is_callable = True
        self.func = func
        return self


def catch(*exceptions):
    return Scenario(exceptions=list(exceptions))
