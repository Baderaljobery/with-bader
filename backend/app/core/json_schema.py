from pydantic import BaseModel


def _force_strict_schema(node: dict) -> None:
    if "properties" in node:
        node["additionalProperties"] = False
        node["required"] = list(node["properties"].keys())
        for child in node["properties"].values():
            if isinstance(child, dict):
                _force_strict_schema(child)

    items = node.get("items")
    if isinstance(items, dict):
        _force_strict_schema(items)

    for union_key in ("anyOf", "oneOf", "allOf"):
        for variant in node.get(union_key, []):
            if isinstance(variant, dict):
                _force_strict_schema(variant)


def build_strict_json_schema(model: type[BaseModel]) -> dict:
    """Post-process a pydantic-generated JSON schema into the strict shape
    OpenAI-compatible structured outputs require: every object disallows
    additional properties and lists all its properties as required (fields
    already accept null/empty-default values, so "required" here just means
    "must appear in the output", not "must be non-null")."""
    schema = model.model_json_schema()
    _force_strict_schema(schema)
    for def_schema in schema.get("$defs", {}).values():
        _force_strict_schema(def_schema)
    return schema
