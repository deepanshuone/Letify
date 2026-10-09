"""Shared registry for the problem bank. Every module in data/bank/ imports from here."""
import random

P = []          # problems, in registration order
CHECKS = {}     # id -> (brute_force_fn, random_args_generator(r), compare_mode)
VALIDATE = {}   # id -> fn(tests) that asserts extra properties of the generated tests (e.g. unique answers)


def add(**kw):
    P.append(kw)
    return kw


def rnd(seed):
    return random.Random(seed)


def gen_arr(r, lo=-6, hi=6, nmin=0, nmax=9):
    return [r.randint(lo, hi) for _ in range(r.randint(nmin, nmax))]
