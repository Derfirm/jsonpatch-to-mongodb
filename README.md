# jsonpatch-to-mongodb

Convert [JSON patches](http://jsonpatch.com/) into a MongoDB update.

This is library can help converts json-patch into mongo-query, east adapt to known drivers.

## Example

```python
from jsonpatch_to_mongodb import parse_patches
patches = [{'op': 'add', 'path': '/foo/1', 'value': 'qux'}]
parse_patches(patches) # {'$push': {'foo': {'$each': ['qux'], '$position': 1}}}

```

also we can add `prefix` for patches and each key will be affected, useful when need update nested fields.
```python
from jsonpatch_to_mongodb import parse_patches
patches= [{'op': 'add', 'path': '/foo/1', 'value': 'qux'}]
parse_patches(patches, "test.") # {'$push': {'test.foo': {'$each': ['qux'], '$position': 1}}}
```

## Supported operation
- add
- test
- replace

## Partially supported operation
- remove (issue with unset in array, don't remove element in fact, just set as null)

## Not supported operation
- copy
- move

## Install

```
pip install jsonpatch-to-mongodb
```

## Test

```
make test
```

## License

MIT

Credits
This is a Python port of the [JavaScript](https://github.com/mongodb-js/jsonpatch-to-mongodb) and [Golang](https://github.com/ZaninAndrea/json-patch-to-mongo/) library jsonpatch-to-mongodb.