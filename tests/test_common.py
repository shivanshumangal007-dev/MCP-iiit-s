"""Unit tests for common utilities and configuration."""
import os
import unittest
from pathlib import Path

import common


class TestCommon(unittest.TestCase):

    def setUp(self):
        self.original_env = os.environ.copy()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_paths_exist(self):
        self.assertTrue(common.DATA_DIR.is_dir())
        self.assertTrue(common.FILES_DIR.is_dir())
        self.assertTrue(common.SITE_DIR.is_dir())

    def test_base_url_default(self):
        os.environ.pop("BASE_URL", None)
        os.environ.pop("VERCEL_URL", None)
        os.environ.pop("RENDER_EXTERNAL_URL", None)
        self.assertEqual(common.base_url(), "http://localhost:8000")

    def test_base_url_vercel(self):
        os.environ["VERCEL_URL"] = "mcp-iiit-s.vercel.app"
        self.assertEqual(common.base_url(), "https://mcp-iiit-s.vercel.app")

    def test_base_url_override(self):
        os.environ["BASE_URL"] = "https://custom.domain.edu"
        os.environ["VERCEL_URL"] = "ignored.vercel.app"
        self.assertEqual(common.base_url(), "https://custom.domain.edu")

    def test_reply_structure(self):
        res = common.reply({"test": 123}, section="courses", official_url="https://iiitsonepat.ac.in")
        self.assertIn("data", res)
        self.assertEqual(res["data"], {"test": 123})
        self.assertIn("source", res)
        self.assertTrue(res["source"].endswith("#courses"))
        self.assertEqual(res.get("official_source"), "https://iiitsonepat.ac.in")

    def test_load_json_missing_file(self):
        data = common.load_json("non_existent_file.json", default={"fallback": True})
        self.assertEqual(data, {"fallback": True})


if __name__ == "__main__":
    unittest.main()
