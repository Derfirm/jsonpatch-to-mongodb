from collections import defaultdict
from enum import Enum
from typing import Any, Dict, List

__all__ = ("Operations", "to_dot", "parse_patches")


class Operations(str, Enum):
    ADD = "add"
    REMOVE = "remove"
    REPLACE = "replace"
    COPY = "copy"
    MOVE = "move"
    TEST = "test"


def _escape_token(token: str) -> str:
    to_escape = (
        ("~0", "~"),
        ("~1", "/"),
    )
    for old, new in to_escape:
        token = token.replace(old, new)

    return token


def to_dot(token: str) -> str:
    if token.startswith("/"):
        token = token[1:]
    token = token.replace("/", ".")
    return _escape_token(token)


def parse_patches(patches: List[Dict[str, Any]], prefix: str = "") -> Dict[str, Any]:
    results = defaultdict(dict)
    for patch in patches:
        path = to_dot(patch["path"])
        path = prefix + path

        if patch["op"] == Operations.ADD:
            parts = path.split(".")
            if len(parts) == 1 and parts[-1].isalpha():
                results["$set"][path] = patch["value"]

            elif len(parts) == 1 and parts[-1].isdigit():
                results["$push"][path] = {
                    "$each": [patch["value"]],
                }
            elif len(parts) <= 1:
                raise ValueError("Dotted parts must be more than one")

            position_part = parts[-1]
            key = ".".join(parts[:-1])
            # if you need to refer to the end of an array you can use "-" instead of an index.
            if position_part == "-":
                # another add operation to this same array has been parsed
                if key in results["$push"]:
                    if (
                        isinstance(results["$push"][key], dict)
                        and "$each" in results["$push"][key]
                    ):
                        results["$push"][key]["$each"].append(patch["value"])
                    else:
                        # convert the pushed content from a single value to a list of values
                        results["$push"][key] = {"$each": [results["$push"][key]]}
                        results["$push"][key]["$each"].append(patch["value"])

                    # adding both to specific locations and to the end of the array is not supported
                    if (
                        isinstance(results["$push"][key], dict)
                        and "$position" in results["$push"][key]
                    ):
                        raise ValueError(
                            "Unsupported Operation! can't use add op with mixed positions"
                        )
                else:
                    # no other add operations to this same array have been parsed yet
                    # simply push the value passed
                    results["$push"][key] = patch["value"]
            else:
                if position_part.isdigit():
                    position = int(position_part)

                    if key in results["$push"]:
                        position_diff = position - results["$push"][key]["$position"]
                        if position_diff > len(results["$push"][key]["$each"]):
                            raise ValueError(
                                "Unsupported Operation! can use add op only with contiguous positions"
                            )

                        results["$push"][key]["$each"].insert(
                            position_diff, patch["value"]
                        )
                        results["$push"][key]["$position"] = min(
                            results["$push"][key]["$position"], position
                        )
                    else:
                        results["$push"][key] = {
                            "$each": [patch["value"]],
                            "$position": position,
                        }
                elif position_part.isalpha():
                    results["$set"][path] = patch["value"]
                else:
                    raise ValueError(
                        f"position must be a numeric or alpha, not {position_part}"
                    )

        elif patch["op"] == Operations.REPLACE:
            results["$set"][path] = patch["value"]

        elif patch["op"] == Operations.REMOVE:
            results["$unset"][path] = 1

        elif patch["op"] == Operations.TEST:
            continue
        else:
            # TODO also parse MOVE and COPY
            raise ValueError(f"unsupported operation {patch['op']}")
    return dict(results)
