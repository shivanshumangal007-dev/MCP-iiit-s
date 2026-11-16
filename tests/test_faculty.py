"""Unit tests for the Faculty module."""
import unittest

import faculty


class TestFaculty(unittest.TestCase):

    def test_faculty_loaded(self):
        self.assertEqual(len(faculty.FACULTY_LIST), 17)

    def test_department_filter(self):
        cse = faculty.get_faculty(department="Computer Science").get("data", {})
        self.assertGreaterEqual(cse.get("total_count"), 12)

        ece = faculty.get_faculty(department="ECE").get("data", {})
        self.assertEqual(ece.get("total_count"), 2)

        math = faculty.get_faculty(department="Math").get("data", {})
        self.assertEqual(math.get("total_count"), 2)

        humanities = faculty.get_faculty(department="Humanities").get("data", {})
        self.assertEqual(humanities.get("total_count"), 1)

    def test_name_filter(self):
        mukesh = faculty.get_faculty(name="Mukesh").get("data", {})
        self.assertEqual(mukesh.get("total_count"), 1)
        self.assertIn("Mukesh Mann", mukesh.get("faculty", [])[0]["name"])

    def test_search_expertise(self):
        res = faculty.search_faculty("Artificial Intelligence").get("data", {})
        self.assertGreater(res.get("match_count"), 0)

    def test_faculty_snippets(self):
        snips = list(faculty.faculty_snippets())
        self.assertGreaterEqual(len(snips), 30)


if __name__ == "__main__":
    unittest.main()
