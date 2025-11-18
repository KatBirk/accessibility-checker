import json
import Severity
import os
import re
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

            # helper to map various impact strings to our Severity values
            def impact_to_value(impact_str: str) -> int:
                if not impact_str:
                    return Severity.Severity.DEFAULT.value
                s = impact_str.lower()
                if s in ("critical", "fatal", "high"):
                    return Severity.Severity.FATAL.value
                if s in ("serious",):
                    return Severity.Severity.SERIOUS.value
                if s in ("moderate", "medium"):
                    return Severity.Severity.MODERATE.value
                if s in ("minor", "low"):
                    return Severity.Severity.MINOR.value
                # fallback
                try:
                    return Severity.Severity[s.upper()].value
                except Exception:
                    return Severity.Severity.DEFAULT.value

            # aggregate scores by violation id
            for item in violations_list:
                violation_id = item.get("id")
                impact_str = item.get("impact")
                severity_value = impact_to_value(impact_str)
                if not violation_id:
                    continue
                if violation_id not in self.rankedViolations:
                    self.rankedViolations[violation_id] = severity_value
                else:
                    self.rankedViolations[violation_id] += severity_value

            # produce a sorted list of violations according to aggregated score
            def score_of(v):
                return self.rankedViolations.get(v.get("id"), 0)

            sorted_violations = sorted(violations_list, key=score_of, reverse=True)

            # assign rank per unique violation id (1 = highest score)
            id_order = []
            for v in sorted_violations:
                vid = v.get("id")
                if vid not in id_order:
                    id_order.append(vid)

            id_to_rank = {vid: idx + 1 for idx, vid in enumerate(id_order)}

            for v in sorted_violations:
                v_id = v.get("id")
                v["rank"] = id_to_rank.get(v_id, 0)

            # write a global violations.json that the report frontend expects
            try:
                with open("violations.json", "w") as gf:
                    json.dump(sorted_violations, gf, indent=4)
            except Exception as e:
                print(f"Failed to write global violations.json: {e}")

            self.scoreboard()

    def getRankings(self):
        return self.rankedViolations

    def scoreboard(self):
        for key, val in self.rankedViolations.items():

            print(f"{key}: {val}")

        if not self.rankedViolations:
            print("Scoreboard is empty. No violations were ranked.")
