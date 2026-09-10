"""Deterministic scoring. Reference answers never enter a model prompt."""
import ast
import json
import math
import os
from pathlib import Path
import subprocess
import sys

SAFE_NODES = (ast.Expression, ast.Constant, ast.Name, ast.Load, ast.Store,
              ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare, ast.IfExp,
              ast.Call, ast.GeneratorExp, ast.ListComp, ast.comprehension,
              ast.List, ast.Tuple, ast.Subscript, ast.Slice,
              ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod,
              ast.USub, ast.UAdd, ast.Not, ast.And, ast.Or,
              ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
              ast.Is, ast.IsNot, ast.In, ast.NotIn)
SAFE_FUNCS = dict(sum=sum, len=len, next=next, min=min, max=max, abs=abs,
                  list=list, tuple=tuple, sorted=sorted, float=float, int=int)

def parse_response(text):
    text = text.strip()
    if text.startswith('```') and text.endswith('```'):
        text = text.split('\n', 1)[-1].rsplit('```', 1)[0].strip()
    try:
        obj = json.loads(text)
    except (ValueError, TypeError):
        return None
    return obj if isinstance(obj, dict) and 'answer' in obj else None

def _evaluate_expression(payload):
    import resource
    resource.setrlimit(resource.RLIMIT_CPU, (1, 1))
    resource.setrlimit(resource.RLIMIT_AS, (192 * 1024**2, 192 * 1024**2))
    expr = payload['answer']
    if not isinstance(expr, str) or len(expr) > 1200:
        return {'passed': False, 'error': 'expression_length_or_type'}
    tree = ast.parse(expr, mode='eval')
    nodes = list(ast.walk(tree))
    if len(nodes) > 120 or any(not isinstance(n, SAFE_NODES) for n in nodes):
        return {'passed': False, 'error': 'disallowed_ast'}
    if any(isinstance(n, ast.Name) and n.id.startswith('_') for n in nodes):
        return {'passed': False, 'error': 'disallowed_name'}
    if any(isinstance(n, ast.Constant) and isinstance(n.value, (float, int))
           and abs(n.value) > 1000 for n in nodes):
        return {'passed': False, 'error': 'oversized_constant'}
    if any(isinstance(n, ast.Call) and
           (not isinstance(n.func, ast.Name) or n.func.id not in SAFE_FUNCS)
           for n in nodes):
        return {'passed': False, 'error': 'disallowed_call'}
    compiled = compile(tree, '<candidate>', 'eval')
    details = []
    for xs, expected in payload['tests']:
        try:
            value = eval(compiled, {'__builtins__': SAFE_FUNCS, 'xs': xs.copy()}, {})
            ok = value is None if expected is None else (
                isinstance(value, (int, float)) and not isinstance(value, bool)
                and math.isclose(value, expected, rel_tol=1e-9, abs_tol=1e-9))
            details.append({'input': xs, 'expected': expected,
                            'actual': repr(value), 'pass': ok})
        except Exception as exc:
            details.append({'input': xs, 'pass': False,
                            'error': type(exc).__name__})
    return {'passed': all(d['pass'] for d in details), 'tests': details}

def score(case, text):
    obj = parse_response(text)
    if obj is None:
        return {'passed': False, 'format_ok': False, 'error': 'invalid_json_or_answer'}
    answer = obj['answer']
    result = {'format_ok': True, 'parsed_answer': answer}
    if case['kind'] == 'expression':
        try:
            proc = subprocess.run([sys.executable, '-I', str(Path(__file__).resolve()),
                                   '--expression-check'],
                                  input=json.dumps({'answer': answer, 'tests': case['tests']}),
                                  text=True, capture_output=True, timeout=3,
                                  env={'PATH': os.defpath})
            result.update(json.loads(proc.stdout))
        except Exception as exc:
            result.update(passed=False, error='expression_worker_' + type(exc).__name__)
    elif case['kind'] == 'number':
        try:
            number = float(str(answer).replace(',', '.'))
            result['passed'] = math.isfinite(number) and math.isclose(
                number, case['expected'], rel_tol=1e-9, abs_tol=1e-9)
        except (ValueError, TypeError):
            result['passed'] = False
    else:
        result['passed'] = str(answer).strip().upper() == case['expected']
    return result

def self_test(cases):
    checks = 0
    for case in cases:
        assert score(case, json.dumps({'answer': case['expected']}))['passed'], case['id']
        checks += 1
        assert not score(case, '{"answer":"INCORRECT"}')['passed'], case['id']
        checks += 1
        assert not score(case, 'not JSON')['passed'], case['id']
        checks += 1
    for case_id, expr in [('CODE01', 'sum(xs)/len(xs)'),
                          ('CODE02', 'next((x for x in xs if x and x % 2 == 0), None)')]:
        case = next(c for c in cases if c['id'] == case_id)
        assert not score(case, json.dumps({'answer': expr}))['passed']
        checks += 1
    for expr in ["__import__('os').getcwd()", 'xs.__class__', '10**1000000']:
        case = next(c for c in cases if c['id'] == 'CODE01')
        assert not score(case, json.dumps({'answer': expr}))['passed']
        checks += 1
    return {'grader_checks_passed': checks}

if __name__ == '__main__':
    if '--expression-check' in sys.argv:
        try:
            print(json.dumps(_evaluate_expression(json.load(sys.stdin))))
        except Exception as exc:
            print(json.dumps({'passed': False, 'error': type(exc).__name__}))
    else:
        cases = json.loads((Path(__file__).parent / 'cases.json').read_text())
        print(json.dumps(self_test(cases)))
