import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "ohif" / "qido_proxy.py"
SPEC = importlib.util.spec_from_file_location("medcua_qido_proxy", MODULE_PATH)
qido_proxy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(qido_proxy)


def study(uid):
    return {"0020000D": {"vr": "UI", "Value": [uid]}}


class QIDOProxyTests(unittest.TestCase):
    def test_cohort_has_thirty_unique_studies(self):
        self.assertEqual(len(qido_proxy.ALLOWED_STUDY_UIDS), 30)
        self.assertEqual(len(set(qido_proxy.ALLOWED_STUDY_UIDS)), 30)

    def test_filter_preserves_cohort_order(self):
        response = [
            study(uid)
            for uid in reversed(qido_proxy.ALLOWED_STUDY_UIDS)
        ]
        filtered = qido_proxy.filter_studies(response)
        self.assertEqual(
            [qido_proxy._study_uid(item) for item in filtered],
            list(qido_proxy.ALLOWED_STUDY_UIDS),
        )

    def test_filter_fails_if_required_study_disappears(self):
        response = [
            study(uid)
            for uid in qido_proxy.ALLOWED_STUDY_UIDS[:-1]
        ]
        with self.assertRaisesRegex(RuntimeError, "missing required"):
            qido_proxy.filter_studies(response)


if __name__ == "__main__":
    unittest.main()
