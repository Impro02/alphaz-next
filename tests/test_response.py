# UNITTEST
from unittest import TestCase

# ALPHAZ_NEXT
from alphaz_next.core.response import AlphaJSONResponse


class TestAlphaResponse(TestCase):
    def test_json(self):
        # GIVEN
        expected_headers = {
            "content-length": "5",
            "content-type": "application/json",
            "access-control-expose-headers": "foo, boo, x-pagination, x-status-description, x-warning",
            "x-pagination": '{"total": 2, "page": 0, "per_page": 10, "total_pages": 1}',
            "x-status-description": '"Foo Boo Far"',
            "x-warning": "1",
        }

        headers = {
            "access-control-expose-headers": "foo, boo",
        }
        ext_headers = {
            "pagination": '{"total": 2, "page": 0, "per_page": 10, "total_pages": 1}',
            "status_description": "Foo Boo Far",
            "warning": True,
        }
        # WHEN
        res = AlphaJSONResponse(
            content="Foo",
            headers=headers,
            ext_headers=ext_headers,
        )

        self.assertEqual(
            expected_headers,
            {k: v for k, v in res.headers.items()},
        )
