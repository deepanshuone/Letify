"""Runs inside Pyodide (see pyWorker.ts). Compiles the visitor's code once, then runs one test case per call."""
import json, sys, io, time, traceback
sys.setrecursionlimit(3000)
_fn = None


def _fmt_exc():
    t, v, tb = sys.exc_info()
    lines = [fr.lineno for fr in traceback.extract_tb(tb) if fr.filename == 'solution.py']
    where = (' (line %d)' % lines[-1]) if lines else ''
    if isinstance(v, SyntaxError):
        where = ' (line %s)' % v.lineno
    return ''.join(traceback.format_exception_only(t, v)).strip() + where


def _prep(code, fn):
    global _fn
    ns = {'__name__': '__main__'}
    try:
        exec(compile(code, 'solution.py', 'exec'), ns)
    except BaseException:
        return json.dumps({'type': 'compile_error', 'message': _fmt_exc()})
    f = ns.get(fn)
    if f is None and 'Solution' in ns:
        try:
            f = getattr(ns['Solution'](), fn)
        except Exception:
            f = None
    if f is None:
        return json.dumps({'type': 'compile_error', 'message': 'Function ' + fn + ' is not defined. Keep the function name exactly as given.'})
    _fn = f
    return json.dumps({'type': 'ready'})


def _run1(args_json):
    args = json.loads(args_json)
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    t0 = time.perf_counter()
    try:
        r = _fn(*args)
        ms = (time.perf_counter() - t0) * 1000
        return json.dumps({'ok': True, 'value': r, 'ms': ms, 'stdout': buf.getvalue()[:4000]})
    except BaseException:
        return json.dumps({'ok': False, 'error': _fmt_exc(), 'stdout': buf.getvalue()[:4000]})
    finally:
        sys.stdout = old
