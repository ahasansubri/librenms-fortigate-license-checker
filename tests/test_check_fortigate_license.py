#!/usr/bin/env python3

import importlib.machinery
import importlib.util
import sys
import unittest
from datetime import date, datetime, time, timezone
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1] / "plugins" / "check_fortigate_license"
loader = importlib.machinery.SourceFileLoader("check_fortigate_license", str(PLUGIN))
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
sys.modules[loader.name] = module
loader.exec_module(module)


def epoch(days_from_today: int) -> int:
    target = datetime.combine(date.today(), time(), tzinfo=timezone.utc)
    return int(target.timestamp()) + (days_from_today * 86400)


class FortiGateLicenceTests(unittest.TestCase):
    def test_flat_and_nested_results(self):
        payload = {
            "status": "success",
            "results": {
                "web_filtering": {"status": "licensed", "expires": epoch(120)},
                "hardware": {
                    "support": {
                        "enhanced": {"status": "registered", "expires": epoch(45)},
                        "comprehensive": {"status": "registered", "expires": epoch(90)},
                    }
                },
            },
        }
        items = module.parse_licences(payload, [])
        self.assertEqual(len(items), 3)
        self.assertIn("hardware / enhanced", {item.name for item in items})

    def test_warning_and_critical_thresholds(self):
        items = [
            module.Licence("healthy", "licensed", date.fromordinal(date.today().toordinal() + 120)),
            module.Licence("warning", "licensed", date.fromordinal(date.today().toordinal() + 45)),
        ]
        status, _ = module.evaluate(
            items,
            60,
            30,
            list(module.DEFAULT_CRITICAL_STATUS_PATTERNS),
            list(module.DEFAULT_WARNING_STATUS_PATTERNS),
        )
        self.assertEqual(status, module.WARNING)

        items.append(module.Licence("bad", "expired", None))
        status, _ = module.evaluate(
            items,
            60,
            30,
            list(module.DEFAULT_CRITICAL_STATUS_PATTERNS),
            list(module.DEFAULT_WARNING_STATUS_PATTERNS),
        )
        self.assertEqual(status, module.CRITICAL)

    def test_zero_expiry_is_treated_as_no_expiry(self):
        self.assertIsNone(module.parse_epoch_or_date(0))

    def test_millisecond_epoch_is_supported(self):
        seconds = epoch(90)
        self.assertEqual(
            module.parse_epoch_or_date(seconds * 1000),
            datetime.fromtimestamp(seconds, tz=timezone.utc).date(),
        )

    def test_supported_text_date_is_parsed(self):
        self.assertEqual(module.parse_epoch_or_date("2030-04-03"), date(2030, 4, 3))

    def test_invalid_date_raises_value_error(self):
        with self.assertRaises(ValueError):
            module.parse_epoch_or_date("not-a-date")

    def test_ignore_features_supports_case_insensitive_wildcards(self):
        payload = {
            "status": "success",
            "results": {
                "web_filtering": {"status": "licensed", "expires": epoch(120)},
                "FortiAnalyzer_Cloud": {"status": "no_license", "expires": 0},
            },
        }
        items = module.parse_licences(payload, ["fortianalyzer*"])
        self.assertEqual([item.name for item in items], ["web_filtering"])

    def test_no_license_is_visible_but_ok_by_default(self):
        items = [module.Licence("optional_feature", "no_license", None)]
        status, message = module.evaluate(
            items,
            60,
            30,
            list(module.DEFAULT_CRITICAL_STATUS_PATTERNS),
            list(module.DEFAULT_WARNING_STATUS_PATTERNS),
        )
        self.assertEqual(status, module.OK)
        self.assertIn("optional_feature: no_license", message)

    def test_custom_status_pattern_can_make_no_license_critical(self):
        item = module.Licence("required_feature", "no_license", None)
        self.assertEqual(
            module.item_severity(item, 60, 30, ["*no_license*"], []),
            module.CRITICAL,
        )

    def test_api_failure_status_is_rejected(self):
        with self.assertRaises(RuntimeError):
            module.parse_licences({"status": "error", "results": {}}, [])

    def test_endpoint_normalization(self):
        self.assertEqual(
            module.endpoint_list({"endpoint": "api/custom"}),
            ("/api/custom",),
        )


if __name__ == "__main__":
    unittest.main()
