from dataclasses import is_dataclass, fields
from pydantic import BaseModel


def prepr(obj, indent=2, split_str=True):
    """
    ``prepr`` (pretty repr) returns a string representation of a nested object:
        - using each object's ``__repr__``
        - with a readable and consistent indentation structure, similar to pretty-printed JSON
        (unlike ``pprint``)

    Indentation is supported for the following types:
        - built-in types: str, dict, list, tuple
        - dataclasses
        - pydantic models

    TODO: add support for sets, frozensets, and namedtuples

    Other objects just have their ``__repr__`` inserted as-is.

    According to the Python documentation:

    > If at all possible, [the value returned by ``__repr__``] should look like a valid Python
    > expression that could be used to recreate an object with the same value (given an appropriate
    > environment).
    https://docs.python.org/3/reference/datamodel.html#object.__repr__

    If all nested objects' ``__repr__`` methods satisfy this property, the output of this function
    will also satisfy it.

    By default, strings containing newlines are displayed on multiple lines using
    string literal concatenation. This can be disabled with ``split_str=False``.
    See https://docs.python.org/3/reference/lexical_analysis.html#string-literal-concatenation

    :param obj: The object to pretty print.
    :param indent: Number of spaces for each indentation level.
    :param split_str: Whether to display strings containing newlines on multiple lines.
    """

    def _repr_nested(obj, level=0):
        if isinstance(obj, str):
            return print_string(obj, level)
        elif is_dataclass(obj):
            return repr_dataclass(obj, level)
        elif isinstance(obj, BaseModel):
            return repr_pydantic(obj, level)
        elif isinstance(obj, dict):
            return repr_dict(obj, level)
        elif isinstance(obj, (list, tuple)):
            return repr_sequence(obj, level)
        else:
            return repr(obj)

    def print_string(s, level):
        if "\n" in s and split_str:
            lines = s.split("\n")
            result = "\n"
            for i, line in enumerate(lines):
                if i == len(lines) - 1 and line == "":
                    break
                result += " " * (level + indent) + repr(line + ("\n" if i < len(lines) - 1 else ""))
                result += "\n"
            return result.rstrip()
        else:
            return repr(s)

    def repr_dataclass(obj, level):
        class_name = obj.__class__.__name__
        if not fields(obj):
            return f"{class_name}()"
        result = f"{class_name}(\n"
        for field in fields(obj):
            field_name = field.name
            field_value = getattr(obj, field_name)
            result += " " * (level + indent) + f"{field_name}="
            result += _repr_nested(field_value, level + indent)
            result += ",\n"
        result += " " * level + ")"
        return result

    def repr_pydantic(obj, level):
        class_name = obj.__class__.__name__
        if not obj.__fields__:
            return f"{class_name}()"
        result = f"{class_name}(\n"
        for field_name, field_value in obj:
            result += " " * (level + indent) + f"{field_name}="
            result += _repr_nested(field_value, level + indent)
            result += ",\n"
        result += " " * level + ")"
        return result

    def repr_dict(d, level):
        if not d:
            return "{}"
        result = "{\n"
        for key, value in d.items():
            result += " " * (level + indent) + repr(key) + ": "
            result += _repr_nested(value, level + indent)
            result += ",\n"
        result += " " * level + "}"
        return result

    def repr_sequence(seq, level):
        if not seq:
            return "[]" if isinstance(seq, list) else "()"
        bracket = "[]" if isinstance(seq, list) else "()"
        result = f"{bracket[0]}\n"
        for item in seq:
            result += " " * (level + indent)
            result += _repr_nested(item, level + indent)
            result += ",\n"
        result += " " * level + f"{bracket[1]}"
        return result

    return _repr_nested(obj)
