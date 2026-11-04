"""Führt die Node-Tests des KI-Kurses aus (tools/tests/kurs/*.test.mjs).

Aufruf aus dem Repo-Wurzelverzeichnis:  python3 -m unittest discover -s tools/tests -v

Wie test_rechner.py: Die Logik des Kurses ist JavaScript und wird in Node geprüft, nicht in
Python nachgebaut. Ohne Node überspringt sich der Test, statt den Lauf rot zu machen.
"""
import glob
import os
import shutil
import subprocess
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@unittest.skipIf(shutil.which("node") is None, "Node nicht installiert")
class TestKursLogik(unittest.TestCase):
    def test_node_tests_des_kurses(self):
        dateien = sorted(glob.glob(os.path.join(REPO, "tools", "tests", "kurs", "*.test.mjs")))
        self.assertTrue(dateien, "keine Node-Tests gefunden")
        r = subprocess.run(["node", "--test", *dateien], capture_output=True, text=True, cwd=REPO)
        self.assertEqual(r.returncode, 0, r.stdout[-4000:] + r.stderr[-2000:])


if __name__ == "__main__":
    unittest.main()
