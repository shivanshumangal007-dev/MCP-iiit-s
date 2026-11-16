"""Unit tests for the About Us module."""
import unittest

import about_us


class TestAboutUs(unittest.TestCase):

    def test_pages_loaded(self):
        self.assertGreaterEqual(len(about_us.PAGES), 13)

    def test_vision_and_mission(self):
        res = about_us.get_vision_and_mission()
        data = res.get("data", {})
        self.assertIn("vision", data)
        self.assertIn("mission", data)
        self.assertGreater(len(data["vision"]), 0)
        self.assertGreater(len(data["mission"]), 0)

    def test_courses(self):
        res = about_us.get_courses()
        courses = res.get("data", {}).get("courses", [])
        self.assertEqual(len(courses), 4)
        branches = [c["branch"] for c in courses]
        self.assertIn("Computer Science and Engineering", branches)
        self.assertIn("Information Technology", branches)

    def test_visitor(self):
        res = about_us.get_visitor()
        vis = res.get("data", {})
        self.assertIn("Droupadi Murmu", vis.get("name", ""))

    def test_governance_all_and_filtered(self):
        all_gov = about_us.get_governance().get("data", {})
        self.assertIn("board_of_governors", all_gov)
        self.assertIn("senate", all_gov)
        self.assertEqual(len(all_gov["board_of_governors"]), 13)
        self.assertEqual(len(all_gov["senate"]), 7)

        bog_only = about_us.get_governance("bog").get("data", {})
        self.assertIn("board_of_governors", bog_only)
        self.assertNotIn("senate", bog_only)

    def test_administration_committees(self):
        all_comm = about_us.get_administration_committees().get("data", {})
        self.assertEqual(len(all_comm["committees"]), 14)

        admission = about_us.get_administration_committees("admissions").get("data", {})
        self.assertGreaterEqual(len(admission["committees"]), 1)

    def test_mous(self):
        all_mous = about_us.get_mous().get("data", {})
        self.assertEqual(len(all_mous["mous"]), 7)

        surat = about_us.get_mous("Surat").get("data", {})
        self.assertEqual(len(surat["mous"]), 1)

    def test_rti(self):
        rti = about_us.get_rti_info().get("data", {})
        self.assertEqual(len(rti["officials"]), 2)

    def test_about_snippets(self):
        snips = list(about_us.about_snippets())
        self.assertGreaterEqual(len(snips), 80)


if __name__ == "__main__":
    unittest.main()
