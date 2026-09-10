"""Run with `python -m cost_router --help` from the repository checkout."""
import argparse
import json
import sys

from jsonschema.exceptions import ValidationError

from .capabilities import check_manifest
from .handoff import validate_handoff
from .router import route
from .validation import clock, load_json, validate


def main(argv=None):
    parser = argparse.ArgumentParser(description='Validate contracts or recommend an evidence-scoped route.')
    commands = parser.add_subparsers(dest='command', required=True)
    routing = commands.add_parser('route', help='Recommend a plan; never launch a surface')
    routing.add_argument('request')
    routing.add_argument('--at', help='Explicit historical time for fixture replay; omit for current evaluation')
    checking = commands.add_parser('validate', help='Validate a saved contract; does not prove live tool access')
    checking.add_argument('schema', choices=['request', 'capabilities', 'handoff', 'decision'])
    checking.add_argument('file')
    checking.add_argument('--at', help='Explicit historical time for replay')
    args = parser.parse_args(argv)
    try:
        if args.command == 'route':
            result = route(load_json(args.request), now=args.at)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0 if result['status'] == 'routed' else 3
        packet = load_json(args.file)
        if args.schema == 'handoff':
            validate_handoff(packet, now=args.at)
        elif args.schema == 'capabilities':
            check_manifest(packet, clock(args.at))
        else:
            validate(args.schema, packet)
        print(json.dumps({'valid': True, 'schema': args.schema, 'live_preflight': False}))
        return 0
    except (OSError, ValueError, ValidationError) as error:
        message = error.message if isinstance(error, ValidationError) else str(error)
        print(json.dumps({'error': message}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
