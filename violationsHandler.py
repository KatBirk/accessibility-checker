import json
import Severity
import os
import re
import ranking
from typing import List, Dict, Any


class ViolationsHandler:

    initialized = False
    vioCount = 0
    rankedViolations = {}

    def __init__(self, context_id: str):
        self.file_path = self._sanitize_url(context_id)

    def _sanitize_url(self, url: str) -> str:
        # made by GPT may contain bugs
        safe_name = re.sub(r'https?://(www\.)?', '', url).rstrip('/')
        safe_name = re.sub(r'[/?:&=.]', '_', safe_name)
        return safe_name[:200] + ".json"

    def _init_file(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump({"all_violations": []}, f, indent=4)
        self.initialized = True

    def _read_violationsFile(self) -> Dict[str, Any]:
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"all_violations": []}

    def _write_violationsFile(self, violations: Dict[str, Any]):
        with open(self.file_path, "w") as f:
            json.dump(violations, f, indent=4)

    def append_violation(self, violation: List[Dict[str, Any]]) -> int:
        data = self._read_violationsFile()

        data["all_violations"].extend(violation)

        self._write_violationsFile(data)
        self.vioCount += 1
        return len(data["all_violations"])

    def ranking(self):

        if self.initialized:
            with open(self.file_path, "r") as f:

                data = f.read()
                file_data = json.loads(data)
                violations_list = file_data.get("all_violations", [])

            for item in violations_list:
                violation_id = item.get("id")
                impact_str = item.get("impact")
                severity_value = Severity.Severity[impact_str.upper()].value
                if violation_id not in self.rankedViolations.keys():

                    self.rankedViolations[violation_id] = severity_value
                else:
                    self.rankedViolations[violation_id] += severity_value
            self.scoreboard()

    def getRankings(self):
        return self.rankedViolations

    def scoreboard(self):
        for key, val in self.rankedViolations.items():

            print(f"{key}: {val}")

        if not self.rankedViolations:
            print("Scoreboard is empty. No violations were ranked.")
