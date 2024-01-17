# UNITTEST
import os
from pathlib import Path
import re
from unittest import TestCase

# ALPHAZ_NEXT
from alphaz_next.utils.logger import AlphaLogger

LOG_PATTERN = r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\s-\sINFO\s-\s\d+\s-\s\w+\.\d+\s-\s\w+\s+:\s+.+"


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
        for row in rows:
            row = re.sub(r"\s+", " ", row).strip()
            self.assertRegex(row, expected_log_pattern)
