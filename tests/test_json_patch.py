import pytest

from jsonpatch_to_mongodb import parse_patches, to_dot


@pytest.mark.parametrize(
    "expected, actual",
    [
        ("foo", "/foo"),
        ("", "/"),
        ("a/b", "/a~1b"),
        ("c%d", "/c%d"),
        ("e^f", "/e^f"),
        ("g|h", "/g|h"),
        ("i\\j", "/i\\j"),
        ('k"l', '/k"l'),
        (" ", "/ "),
        ("m~n", "/m~0n"),
    ],
)
def test_escape(expected, actual):
    assert to_dot(actual) == expected


def test_correct_parse():
    patches = [
        {"op": "add", "path": "/hello/0/hi/5", "value": 1},
        {"op": "add", "path": "/hello/0/hi/5", "value": 2},
        {"op": "add", "path": "/hello/0/hi/5", "value": 6},
        {"op": "add", "path": "/hello/0/hi/6", "value": 7},
        {"op": "remove", "path": "/hello/0/hi/5", "value": 3},
        {"op": "replace", "path": "/hello/0/hi/5", "value": 4},
    ]

    assert parse_patches(patches) == {
        "$push": {"hello.0.hi": {"$each": [6, 7, 2, 1], "$position": 5}},
        "$set": {"hello.0.hi.5": 4},
        "$unset": {"hello.0.hi.5": 1},
    }


def test_remove_query():
    remove_query = [{"op": "remove", "path": "/response/recs/objs/2"}]
    assert parse_patches(remove_query) == {"$unset": {"response.recs.objs.2": 1}}


@pytest.mark.parametrize(
    "query, result",
    [
        ([{"op": "add", "path": "/baz", "value": "qux"}], {"$set": {"baz": "qux"}}),
        (
            [{"op": "add", "path": "/name/nested", "value": "dave"}],
            {"$set": {"name.nested": "dave"}},
        ),
        (
            [{"op": "add", "path": "/foo/1", "value": "qux"}],
            {"$push": {"foo": {"$position": 1, "$each": ["qux"]}}},
        ),
    ],
)
def test_add_query(query, result):
    assert parse_patches(query) == result
