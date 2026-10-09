import type { Lang } from '../types';

/* A small tokenizer: enough colour for the four supported languages without shipping a full editor library. */

export type TokenClass = 'com' | 'str' | 'num' | 'kw' | 'ty' | 'fn';
export interface Token {
  text: string;
  cls?: TokenClass;
}

const KW: Record<Lang, string> = {
  python:
    'False None True and as assert async await break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield',
  javascript:
    'async await break case catch class const continue debugger default delete do else export extends finally for function if import in instanceof let new of return super switch this throw try typeof var void while with yield null true false undefined',
  cpp: 'alignas auto break case catch class const constexpr continue default delete do else enum explicit extern false for friend goto if inline namespace new noexcept nullptr operator private protected public return sizeof static struct switch template this throw true try typedef typename union using virtual void volatile while',
  java: 'abstract assert break case catch class continue default do else enum extends final finally for if implements import instanceof interface new null package private protected public return static super switch synchronized this throw throws try true false void volatile while',
};

const TY: Record<Lang, string> = {
  python: 'int str list dict set tuple bool float len range enumerate sorted min max sum abs zip map filter print reversed any all',
  javascript: 'Array Object Map Set Math Number String Boolean JSON Infinity NaN console parseInt Symbol Promise',
  cpp: 'int long short char bool double float unsigned signed string vector map set unordered_map unordered_set pair deque queue stack priority_queue array size_t min max sort swap cout cin endl',
  java: 'int long short char byte boolean double float String Integer Long List ArrayList Map HashMap Set HashSet Deque ArrayDeque Queue LinkedList Arrays Math Collections Stack Character StringBuilder Object',
};

const KWSET = {} as Record<Lang, Set<string>>;
const TYSET = {} as Record<Lang, Set<string>>;
for (const l of Object.keys(KW) as Lang[]) {
  KWSET[l] = new Set(KW[l].split(' '));
  TYSET[l] = new Set(TY[l].split(' '));
}

const NUM = String.raw`(\b0[xX][0-9a-fA-F_]+\b|\b\d[\d_]*(?:\.\d+)?(?:[eE][+-]?\d+)?\b)`;
const ID = String.raw`([A-Za-z_$][\w$]*)`;
const STR_BASIC = String.raw`"(?:\\.|[^"\\\n])*"?|'(?:\\.|[^'\\\n])*'?`;

// Groups: 1 comment, 2 string, 3 number, 4 identifier
const RE_SRC: Record<Lang, string> = {
  python: String.raw`(#[^\n]*)|("""[\s\S]*?(?:"""|$)|'''[\s\S]*?(?:'''|$)|${STR_BASIC})|${NUM}|${ID}`,
  javascript: String.raw`(\/\/[^\n]*|\/\*[\s\S]*?(?:\*\/|$))|(\x60(?:\\[\s\S]|[^\x60\\])*\x60?|${STR_BASIC})|${NUM}|${ID}`,
  cpp: String.raw`(\/\/[^\n]*|\/\*[\s\S]*?(?:\*\/|$)|^[ \t]*#[^\n]*)|(${STR_BASIC})|${NUM}|${ID}`,
  java: String.raw`(\/\/[^\n]*|\/\*[\s\S]*?(?:\*\/|$))|(${STR_BASIC})|${NUM}|${ID}`,
};

/** Split code into tokens. Joining every `text` gives back the exact input. */
export function tokenize(code: string, lang: Lang): Token[] {
  const src = RE_SRC[lang];
  const re = new RegExp(src, lang === 'cpp' ? 'gm' : 'g');
  const out: Token[] = [];
  let last = 0;
  let m: RegExpExecArray | null;
  while ((m = re.exec(code)) !== null) {
    if (m[0].length === 0) {
      re.lastIndex++;
      continue;
    }
    if (m.index > last) out.push({ text: code.slice(last, m.index) });
    let cls: TokenClass | undefined;
    if (m[1]) cls = 'com';
    else if (m[2]) cls = 'str';
    else if (m[3]) cls = 'num';
    else if (m[4]) {
      if (KWSET[lang].has(m[4])) cls = 'kw';
      else if (TYSET[lang].has(m[4])) cls = 'ty';
      else if (code.charAt(re.lastIndex) === '(') cls = 'fn';
    }
    out.push(cls ? { text: m[0], cls } : { text: m[0] });
    last = re.lastIndex;
  }
  if (last < code.length) out.push({ text: code.slice(last) });
  return out;
}
