"""Bounded local GGUF inference; no API calls, no model-generated shell commands."""
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import sys
import time
import urllib.request
from grader import score, self_test

ROOT = Path(__file__).parent
OUT = ROOT / 'results'
OUT.mkdir(exist_ok=True)
BASE = "Tu es un assistant utile. Accomplis la tâche de l’utilisateur et respecte le format demandé."
FORMAT = ('\nRéponds uniquement par un objet JSON avec deux champs : "answer" '
          '(la valeur demandée) et "reason" (une justification brève en une phrase).')
SEEDS = [11, 29]
MODEL_REVISION = '90862c4b9d2787eaed51d12237eafdfe7c5f6077'
MODEL_ID = 'Qwen/Qwen3-1.7B-GGUF'
MODEL_FILE = 'Qwen3-1.7B-Q8_0.gguf'
MODEL_URL = f'https://huggingface.co/{MODEL_ID}/resolve/{MODEL_REVISION}/{MODEL_FILE}'
SAMPLING = dict(max_tokens=256, temperature=0.7, top_p=0.8,
                top_k=20, min_p=0.0, repeat_penalty=1.0, presence_penalty=1.5)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def make_prompt(case, injection):
    system = BASE + ('\n\n' + injection if injection else '')
    messages = [{'role': 'system', 'content': system}]
    messages += case.get('history', [])
    messages += [{'role': 'user', 'content': case['prompt'] + FORMAT}]
    raw = ''.join('<|im_start|>' + m['role'] + '\n' + m['content'] +
                  '<|im_end|>\n' for m in messages)
    raw += '<|im_start|>assistant\n<think>\n\n</think>\n\n'
    return raw, messages


def main():
    cases = json.loads((ROOT / 'cases.json').read_text())
    arms = {'without': '', 'short': (ROOT / 'short.md').read_text().strip(),
            'full': (ROOT / 'treatment.md').read_text().strip()}
    order = [(c['id'], seed, arm) for c in cases for seed in SEEDS for arm in arms]
    random.Random(20260910).shuffle(order)
    prereg = {'model': MODEL_ID, 'revision': MODEL_REVISION, 'model_file': MODEL_FILE,
              'sampling': SAMPLING, 'seeds': SEEDS, 'order_seed': 20260910,
              'planned_calls': len(order), 'max_generated_tokens': len(order)*256,
              'max_inference_seconds': 720, 'arms': arms, 'order': order,
              'cases_sha256': sha((ROOT/'cases.json').read_bytes()),
              'arm_sha256': {a: sha(t.encode()) for a,t in arms.items()},
              'note': 'Synthetic convenience sample; one small quantized model; no causal generalization.'}
    save('preregistration.json', prereg)
    save('grader_self_test.json', self_test(cases))
    path = ROOT / MODEL_FILE
    t0 = time.monotonic()
    urllib.request.urlretrieve(MODEL_URL, path)
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    from llama_cpp import Llama
    import llama_cpp
    llm = Llama(model_path=str(path), n_ctx=4096, n_threads=4,
                n_threads_batch=4, n_batch=512, verbose=False)
    save('runtime.json', {'python': sys.version, 'platform': platform.platform(),
                         'llama_cpp_version': llama_cpp.__version__,
                         'model_sha256': digest, 'model_bytes': path.stat().st_size,
                         'setup_seconds': time.monotonic()-t0,
                         'git_sha': os.environ.get('GITHUB_SHA'),
                         'run_id': os.environ.get('GITHUB_RUN_ID')})
    by_id = {c['id']: c for c in cases}
    rows = []
    start = time.monotonic()
    with (OUT/'raw.jsonl').open('w') as output:
        for idx, (case_id, seed, arm) in enumerate(order):
            if time.monotonic()-start > 720:
                break
            case = by_id[case_id]
            prompt, messages = make_prompt(case, arms[arm])
            then = time.monotonic()
            completion = llm.create_completion(prompt, seed=seed,
                           stop=['<|im_end|>', '<|endoftext|>'], **SAMPLING)
            choice = completion['choices'][0]
            row = {'index': idx, 'case_id': case_id, 'family': case['family'],
                   'seed': seed, 'arm': arm, 'prompt_sha256': sha(prompt.encode()),
                   'messages': messages, 'response': choice['text'],
                   'finish_reason': choice['finish_reason'], 'usage': completion['usage'],
                   'seconds': time.monotonic()-then,
                   'score': score(case, choice['text'])}
            rows.append(row)
            output.write(json.dumps(row, ensure_ascii=False)+'\n')
            output.flush()
            print(json.dumps({k:row[k] for k in ['index','case_id','arm','seconds','score']},
                             ensure_ascii=False), flush=True)
    summary = {'planned':len(order), 'completed':len(rows),
               'complete':len(rows)==len(order), 'by_arm':{}}
    for arm in arms:
        sample = [r for r in rows if r['arm']==arm]
        summary['by_arm'][arm] = {'n':len(sample),
           'correct':sum(r['score']['passed'] for r in sample),
           'invalid_format':sum(not r['score']['format_ok'] for r in sample),
           'truncated':sum(r['finish_reason']=='length' for r in sample),
           'input_tokens':sum(r['usage']['prompt_tokens'] for r in sample),
           'output_tokens':sum(r['usage']['completion_tokens'] for r in sample),
           'seconds':sum(r['seconds'] for r in sample)}
    save('summary.json', summary)
    print('FINAL_SUMMARY '+json.dumps(summary,ensure_ascii=False),flush=True)

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        save('infrastructure_error.json', {'type':type(exc).__name__, 'message':str(exc)[:1000]})
        raise
