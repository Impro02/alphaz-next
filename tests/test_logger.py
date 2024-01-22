# UNITTEST
import os
from pathlib import Path
import re
from unittest import TestCase

# ALPHAZ_NEXT
from alphaz_next.utils.logger import AlphaLogger

LOG_PATTERN = (
    r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\s-\s\w+\s-\s\d+\s-\s\w+\.\d+\s-\s\w+:\s.+"
)


class TestAlphaLogger(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._directory = Path(
            os.path.join(
                os.path.expanduser("~"),
                "tests",
                "assets",
                "logs",
            )
        )
        cls._directory.mkdir(parents=True, exist_ok=True)

    def test_info(self):
        # GIVEN
        expected_log_pattern = LOG_PATTERN

        logger = AlphaLogger(
            name="test",
            directory=str(self._directory),
        )

        # WHEN
        logger.info(message="Test info")

        with open(Path(self._directory) / "test.log") as f:
            rows = f.readlines()

        # THEN
        self.assertGreater(len(rows), 0)
        for row in rows:
            row = re.sub(r"\s+", " ", row).strip()
            self.assertRegex(row, expected_log_pattern)

    def test_error(self):
        # GIVEN
        expected_log_pattern = LOG_PATTERN

        logger = AlphaLogger(
            name="test",
            directory=str(self._directory),
        )

        # WHEN
        logger.error(message="Test error")

        with open(Path(self._directory) / "test.log") as f:
            rows_tests = f.readlines()

        with open(Path(self._directory) / "errors.log") as f:
            rows_errors = f.readlines()

        # THEN
        self.assertGreater(len(rows_tests), 0)
        self.assertGreater(len(rows_errors), 0)
        for row in rows_tests:
            row = re.sub(r"\s+", " ", row).strip()
            self.assertRegex(row, expected_log_pattern)

        for row in rows_errors:
            row = re.sub(r"\s+", " ", row).strip()
            self.assertRegex(row, expected_log_pattern)

    def test_warning(self):
        # GIVEN
        expected_log_pattern = LOG_PATTERN

        logger = AlphaLogger(
            name="test",
            directory=str(self._directory),
        )

        # WHEN
        logger.warning(message="Test warning")

        with open(Path(self._directory) / "test.log") as f:
            rows_tests = f.readlines()

        with open(Path(self._directory) / "warnings.log") as f:
            rows_warnings = f.readlines()

        # THEN
        self.assertGreater(len(rows_tests), 0)
        self.assertGreater(len(rows_warnings), 0)
        for row in rows_tests:
            row = re.sub(r"\s+", " ", row).strip()
            self.assertRegex(row, expected_log_pattern)

        for row in rows_warnings:
            row = re.sub(r"\s+", " ", row).strip()
            self.assertRegex(row, expected_log_pattern)

    def test_monitor(self):
        # GIVEN
        expected_log_pattern = LOG_PATTERN

        logger = AlphaLogger(
            name="test",
            directory=str(self._directory),
        )

        # WHEN
        logger.critical(message="Test monitor", monitor="monitor")

        with open(Path(self._directory) / "test.log") as f:
            rows_tests = f.readlines()

        with open(Path(self._directory) / "errors.log") as f:
            rows_warnings = f.readlines()

        with open(Path(self._directory) / "monitoring.log") as f:
            rows_monitor = f.readlines()

        # THEN
        self.assertGreater(len(rows_tests), 0)
        self.assertGreater(len(rows_warnings), 0)
        self.assertGreater(len(rows_monitor), 0)
        for row in rows_tests:
            row = re.sub(r"\s+", " ", row).strip()
            self.assertRegex(row, expected_log_pattern)

        for row in rows_warnings:
            row = re.sub(r"\s+", " ", row).strip()
            self.assertRegex(row, expected_log_pattern)

        for row in rows_monitor:
            row = re.sub(r"\s+", " ", row).strip()
            self.assertRegex(row, expected_log_pattern)
