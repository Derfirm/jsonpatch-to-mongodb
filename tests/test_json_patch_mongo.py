import json
from pathlib import Path

import jsonpatch
import pytest

from jsonpatch_to_mongodb import parse_patches


def load_params_from_json(json_path):
    with open(json_path) as f:
        return json.load(f)


@pytest.fixture(
    scope="module",
    params=load_params_from_json(
        Path(__file__).parent / "snapshots/tests_various_op.json"
    ),
)
def scenarios(request):
    return request.param


@pytest.mark.parametrize(
    "base, operation",
    [
        (
            {"details": {"parts": [{"id": "p001", "name": "abc"}]}},
            [
                {
                    "op": "add",
                    "path": "/details/parts/1",
                    "value": {"id": "p002", "name": "xyz"},
                }
            ],
        ),
        ({"foo": "bar"}, [{"op": "add", "path": "/baz", "value": "qux"}]),
        ({"foo": ["bar", "baz"]}, [{"op": "add", "path": "/foo/1", "value": "qux"}]),
        (
            {"foo": "bar"},
            [{"op": "add", "path": "/child", "value": {"grandchild": {}}}],
        ),  # nested
        ({"foo": ["bar"]}, [{"op": "add", "path": "/foo/-", "value": ["abc", "def"]}]),
        ({"foo": None}, [{"op": "add", "path": "/foo", "value": 1}]),
    ],
)
def test_correct_add(mongodb, base, operation):
    query = parse_patches(operation, "test.")
    raise Exception(query)
    apply_patch_result = jsonpatch.apply_patch(base, operation)

    result = mongodb["test_collection"].insert_one(base)
    object_id = result.inserted_id
    mongodb["test_collection"].update_one({"_id": object_id}, query)

    assert apply_patch_result == mongodb["test_collection"].find_one(
        {"_id": object_id}, projection={"_id": False}
    )


def test_operations(scenarios, mongodb):
    base = scenarios["doc"]
    operation = scenarios["patch"]
    expects = scenarios["expected"]
    apply_patch_result = jsonpatch.apply_patch(base, operation)

    query = parse_patches(operation)

    result = mongodb["test_collection"].insert_one(base)
    object_id = result.inserted_id
    mongodb["test_collection"].update_one({"_id": object_id}, query)

    assert (
        expects
        == mongodb["test_collection"].find_one(
            {"_id": object_id}, projection={"_id": False}
        )
        == apply_patch_result
    ), scenarios["comment"]
