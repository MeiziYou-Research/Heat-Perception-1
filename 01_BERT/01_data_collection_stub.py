#!/usr/bin/env python3
"""Document the public input boundary for the text-analysis workflow.

The restricted source corpus is not distributed by this repository. This file
intentionally avoids embedding credentials, request URLs, unreconciled volume
thresholds, or unsupported access claims for source text and identifiers.
"""

from __future__ import annotations

import json

PUBLIC_INPUT_SCHEMA = {
    "public_demo_required": ["example_id", "text", "label", "month", "example_category", "is_synthetic"],
    "public_demo_optional": ["group_id"],
    "month_encoding": "integer 1-12",
    "restrictions": (
        "Original X/Twitter text and user metadata are not included. "
        "Use the small synthetic examples only to inspect the shared classification workflow. "
        "Production inputs are restricted and are documented separately from the demo schema."
    ),
}


if __name__ == "__main__":
    print(json.dumps(PUBLIC_INPUT_SCHEMA, indent=2))
