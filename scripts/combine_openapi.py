#!/usr/bin/env python3
"""
Combine modular OpenAPI specification files into a single file.
This script resolves all $ref pointers and outputs a complete OpenAPI document.
"""

import yaml
import json
import os
import argparse
from pathlib import Path


def resolve_ref(ref, root_dir):
    """Resolve a $ref pointer to a file."""
    if not ref.startswith('./'):
        return None  
    
    parts = ref.split('#/')
    file_path = parts[0]
    json_pointer = parts[1] if len(parts) > 1 else None
    
    full_path = os.path.join(root_dir, file_path)
    with open(full_path, 'r') as f:
        content = yaml.safe_load(f)
    
    if json_pointer:
        for key in json_pointer.split('/'):
            if key in content:
                content = content[key]
            else:
                raise KeyError(f"Could not resolve pointer {json_pointer} in {file_path}")
    
    return content


def resolve_refs_recursive(obj, root_dir):
    """Recursively resolve all $ref pointers in an object."""
    if isinstance(obj, dict):
        if '$ref' in obj and isinstance(obj['$ref'], str) and obj['$ref'].startswith('./'):
            resolved = resolve_ref(obj['$ref'], root_dir)
            if resolved:
                obj.update(resolved)
                resolve_refs_recursive(obj, root_dir)
        else:
            for key, value in list(obj.items()):
                obj[key] = resolve_refs_recursive(value, root_dir)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            obj[i] = resolve_refs_recursive(item, root_dir)
    return obj


def combine_openapi_files(main_file, output_file=None):
    """Combine OpenAPI files by resolving all references."""
    with open(main_file, 'r') as f:
        spec = yaml.safe_load(f)
    root_dir = os.path.dirname(main_file)
    resolved_spec = resolve_refs_recursive(spec, root_dir)
    if output_file:
        with open(output_file, 'w') as f:
            yaml.dump(resolved_spec, f, sort_keys=False)
    return resolved_spec


def main():
    parser = argparse.ArgumentParser(description='Combine modular OpenAPI specification files.')
    parser.add_argument('main_file', help='Path to the main OpenAPI specification file')
    parser.add_argument('-o', '--output', help='Output file path (defaults to stdout)')
    parser.add_argument('--json', action='store_true', help='Output as JSON instead of YAML')
    args = parser.parse_args()
    resolved_spec = combine_openapi_files(args.main_file, args.output if not args.json else None)
    if args.json:
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(resolved_spec, f, indent=2)
        else:
            print(json.dumps(resolved_spec, indent=2))
    elif not args.output:
        print(yaml.dump(resolved_spec, sort_keys=False))


if __name__ == "__main__":
    main()
