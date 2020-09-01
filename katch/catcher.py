import json
from flask import Response


class Catcher:
    app = None
    scenarios = []
    envelope = "message"
    code = "code"
    pending_scenarios = []

    def __init__(self, app=None, scenarios=None, envelope="message", code="code"):
        if scenarios:
            if app:
                self.scenarios = scenarios
            else:
                self.pending_scenarios = scenarios
        if app:
            self.app = app
            self._apply()
        self.envelope = envelope
        self.code = code

    def init_app(self, app):
        self.app = app
        self.scenarios = self.pending_scenarios
        self.pending_scenarios = []
        self._apply()

    def add_scenario(self, scenario):
        if self.app:
            self.scenarios.append(scenario)
            self._apply()
        else:
            self.pending_scenarios.append(scenario)

    def add_scenarios(self, *scenarios):
        if self.app:
            self.scenarios.extend(scenarios)
            self._apply()
        else:
            self.pending_scenarios.extend(scenarios)

    def _generate_scenario_handler(self, scenario):
        def f(*args, **kwargs):
            if self.envelope:
                response_dict = {self.envelope: scenario.respond(*args, **kwargs)}
                if self.code:
                    response_dict[self.code] = scenario.status_code
                response = json.dumps(response_dict)
            else:
                response = json.dumps(scenario.respond(*args, **kwargs))
            return Response(
                response=response,
                status=scenario.status_code,
                content_type="application/json",
            )

        return f

    def _apply(self):
        for scenario in self.scenarios:
            for e in scenario.exceptions:
                self.app.register_error_handler(
                    e, self._generate_scenario_handler(scenario)
                )
