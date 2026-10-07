from __future__ import annotations


def mask_identifier(value: str | None) -> str | None:
    if not value:
        return value
    if len(value) <= 4:
        return "*" * len(value)
    if len(value) <= 8:
        return f"{value[:1]}{'*' * (len(value) - 2)}{value[-1:]}"
    return f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}"


def masked_payload(payload: dict) -> dict:
    sensitive_keys = {"passport", "passportNumber", "taxId", "registrationNumber"}

    def mask(value):
        if isinstance(value, dict):
            return {
                key: mask_identifier(item) if key in sensitive_keys else mask(item)
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [mask(item) for item in value]
        return value

    return mask(payload)

