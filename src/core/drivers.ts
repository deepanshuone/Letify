import type { PType, Problem, TestCase, Value } from '../types';
import { TYPE } from './languages';

/** Every result line printed by a C++ / Java driver starts with this marker. */
export const MARK = '@@R@@';

type ProblemSig = Pick<Problem, 'fn' | 'params' | 'ret'>;

/*
 * stdin format used for C++ / Java: the first line is T (number of tests), then every argument of every test.
 *   int: n | bool: 0/1 | string: one token ("" stands for the empty string)
 *   int[]: length then items | int[][]: row count, then each row as length + items
 */
export function fmtArg(v: Value, t: PType): string {
  if (t === 'int') return String(v);
  if (t === 'bool') return v ? '1' : '0';
  if (t === 'string') return v === '' ? '""' : String(v);
  if (t === 'int[]') {
    const a = v as number[];
    return `${a.length} ${a.join(' ')}`.trimEnd();
  }
  const m = v as number[][];
  return `${m.length}\n${m.map((r) => `${r.length} ${r.join(' ')}`.trimEnd()).join('\n')}`.trimEnd();
}

export function buildStdin(p: Pick<Problem, 'params'>, tests: Pick<TestCase, 'args'>[]): string {
  const lines = [String(tests.length)];
  for (const t of tests) {
    t.args.forEach((a, i) => lines.push(fmtArg(a, p.params[i]![1])));
  }
  return lines.join('\n') + '\n';
}

const CPP_HELPERS = String.raw`
static long long rdI(){ long long x; cin >> x; return x; }
static bool rdB(){ int x; cin >> x; return x != 0; }
static string rdS(){ string s; cin >> s; if(s == "\"\"") s = ""; return s; }
static vector<int> rdV(){ int n; cin >> n; vector<int> v(n); for(int i = 0; i < n; i++) cin >> v[i]; return v; }
static vector<vector<int>> rdM(){ int r; cin >> r; vector<vector<int>> m(r); for(int i = 0; i < r; i++) m[i] = rdV(); return m; }
static void pr(int x){ cout << x; }
static void pr(bool b){ cout << (b ? "true" : "false"); }
static void pr(const string& s){ cout << '"' << s << '"'; }
static void pr(const vector<int>& v){ cout << '['; for(size_t i = 0; i < v.size(); i++){ if(i) cout << ','; cout << v[i]; } cout << ']'; }
static void pr(const vector<vector<int>>& m){ cout << '['; for(size_t i = 0; i < m.size(); i++){ if(i) cout << ','; pr(m[i]); } cout << ']'; }
`;

/** Number of lines the C++ driver puts before the visitor's code (used to fix compiler line numbers). */
export const CPP_PREFIX_LINES = 3;
export const JAVA_PREFIX_LINES = 3;

export function cppProgram(p: ProblemSig, code: string): string {
  const rd: Record<PType, string> = {
    int: '(int)rdI()',
    bool: 'rdB()',
    string: 'rdS()',
    'int[]': 'rdV()',
    'int[][]': 'rdM()',
  };
  const decl = p.params.map(([, t], i) => `        ${TYPE.cpp[t]} p${i} = ${rd[t]};`).join('\n');
  const call = p.params.map((_, i) => `p${i}`).join(', ');
  return (
    '#include <bits/stdc++.h>\nusing namespace std;\n\n' +
    code +
    '\n' +
    CPP_HELPERS +
    '\nint main(){\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    int T;\n    cin >> T;\n    while(T--){\n' +
    decl +
    '\n' +
    `        ${TYPE.cpp[p.ret]} r = Solution().${p.fn}(${call});\n` +
    `        cout << "\\n${MARK}";\n        pr(r);\n        cout << "\\n" << flush;\n    }\n    return 0;\n}\n`
  );
}

const JAVA_HELPERS = String.raw`
    static Scanner sc;
    static int[] rdV(){ int n = sc.nextInt(); int[] a = new int[n]; for(int i = 0; i < n; i++) a[i] = sc.nextInt(); return a; }
    static int[][] rdM(){ int r = sc.nextInt(); int[][] m = new int[r][]; for(int i = 0; i < r; i++) m[i] = rdV(); return m; }
    static String rdS(){ String s = sc.next(); return s.equals("\"\"") ? "" : s; }
    static String js(int x){ return String.valueOf(x); }
    static String js(boolean b){ return b ? "true" : "false"; }
    static String js(String s){ return "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"") + "\""; }
    static String js(int[] a){ StringBuilder sb = new StringBuilder("["); for(int i = 0; i < a.length; i++){ if(i > 0) sb.append(','); sb.append(a[i]); } return sb.append(']').toString(); }
    static String js(int[][] m){ StringBuilder sb = new StringBuilder("["); for(int i = 0; i < m.length; i++){ if(i > 0) sb.append(','); sb.append(js(m[i])); } return sb.append(']').toString(); }
`;

export function javaProgram(p: ProblemSig, code: string): string {
  const rd: Record<PType, string> = {
    int: 'sc.nextInt()',
    bool: '(sc.nextInt() != 0)',
    string: 'rdS()',
    'int[]': 'rdV()',
    'int[][]': 'rdM()',
  };
  const decl = p.params.map(([, t], i) => `            ${TYPE.java[t]} p${i} = ${rd[t]};`).join('\n');
  const call = p.params.map((_, i) => `p${i}`).join(', ');
  return (
    'import java.util.*;\nimport java.io.*;\n\n' +
    code +
    '\n\npublic class Main {' +
    JAVA_HELPERS +
    '    public static void main(String[] args){\n        sc = new Scanner(new BufferedInputStream(System.in));\n        int T = sc.nextInt();\n        for(int t = 0; t < T; t++){\n' +
    decl +
    '\n' +
    `            ${TYPE.java[p.ret]} r = new Solution().${p.fn}(${call});\n` +
    `            System.out.print("\\n${MARK}" + js(r) + "\\n");\n            System.out.flush();\n        }\n    }\n}\n`
  );
}
