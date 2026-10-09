import { useEffect, useRef, useState, type PointerEvent } from 'react';
import { Highlighted } from '../Highlighted';

/* The one moving thing on the landing page: Two Sum solved with a hash map, step by step, then the tests tick green.
   It is a loop of 17 frames. With "reduce motion" switched on it shows the finished frame and stays still. */

const NUMS = [3, 8, 2, 11, 7];
const TARGET = 9;
const FOUND_AT = 4; // frame in which 7 meets the 2 stored earlier
const TESTS = 7;
const FRAMES = 17;
const STILL_FRAME = 14;
const STEP_MS = 760;

const CODE = `def twoSum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return [seen[target - x], i]
        seen[x] = i
    return []`;

function useFrame(): number {
  const [frame, setFrame] = useState(STILL_FRAME);
  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    let t = 0;
    setFrame(0);
    const id = setInterval(() => {
      t = (t + 1) % FRAMES;
      setFrame(t);
    }, STEP_MS);
    return () => clearInterval(id);
  }, []);
  return frame;
}

/** The card leans a little towards the pointer, like a real object on a desk. Skipped when motion is reduced. */
function useTilt() {
  const ref = useRef<HTMLDivElement>(null);
  const move = (e: PointerEvent<HTMLDivElement>) => {
    const el = ref.current;
    if (!el || e.pointerType !== 'mouse' || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const r = el.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width - 0.5;
    const y = (e.clientY - r.top) / r.height - 0.5;
    el.style.setProperty('--ry', `${(-7 + x * 10).toFixed(2)}deg`);
    el.style.setProperty('--rx', `${(3 - y * 8).toFixed(2)}deg`);
  };
  const leave = () => {
    ref.current?.style.removeProperty('--ry');
    ref.current?.style.removeProperty('--rx');
  };
  return { ref, move, leave };
}

const SPARKS = Array.from({ length: 14 }, (_, k) => {
  const a = (k / 14) * Math.PI * 2;
  const far = 46 + (k % 3) * 18;
  return { x: Math.cos(a) * far, y: Math.sin(a) * far - 10, r: (k % 2 ? 1 : -1) * (80 + k * 12), d: (k % 4) * 0.04, c: ['#7FE8C0', '#9387FF', '#4FC3F7', '#F5B85A'][k % 4]! };
});

export function HeroDemo() {
  const frame = useFrame();
  const tilt = useTilt();
  const i = Math.min(frame, FOUND_AT);
  const found = frame >= FOUND_AT;
  const partner = NUMS.indexOf(TARGET - NUMS[FOUND_AT]!);
  const lit = frame < 6 ? 0 : Math.min(TESTS, frame - 5);
  const passed = lit === TESTS;
  const need = TARGET - NUMS[i]!;
  const seen = NUMS.slice(0, i);

  return (
    <div className="lp-stage" ref={tilt.ref} onPointerMove={tilt.move} onPointerLeave={tilt.leave}>
    <div className="lp-demo" role="img" aria-label="Animated example. A list of five numbers is scanned for two that add up to 9. The pair 2 and 7 is found, then all 7 test cases pass.">
      <div className="lp-demo-bar" aria-hidden="true">
        <span className="lp-file">two_sum.py</span>
        <span className="lp-lang">Python</span>
      </div>
      <div className="lp-viz" aria-hidden="true">
        <div className="lp-target">
          Find two numbers that add up to <b>{TARGET}</b>
        </div>
        <div className="lp-cells">
          {NUMS.map((n, k) => {
            const isNow = k === i;
            const isPair = found && (k === FOUND_AT || k === partner);
            const isSeen = k < i && !isPair;
            return (
              <div key={k} className={`lp-cell${isNow ? ' now' : ''}${isSeen ? ' seen' : ''}${isPair ? ' pair' : ''}`}>
                <b>{n}</b>
                <small>{k}</small>
                {isNow && <i className="lp-ptr">i</i>}
              </div>
            );
          })}
        </div>
        <p className="lp-say">
          {found ? (
            <>
              Need {TARGET} - {NUMS[FOUND_AT]} = <b>{need}</b>, and {need} is already stored. The answer is [{partner}, {FOUND_AT}].
            </>
          ) : (
            <>
              Need {TARGET} - {NUMS[i]} = <b>{need}</b>. Not stored yet, so store {NUMS[i]}.
            </>
          )}
        </p>
        <div className="lp-seen">
          <span>seen</span>
          {seen.length === 0 && <em>empty</em>}
          {seen.map((n, k) => (
            <code key={k}>
              {n}:{k}
            </code>
          ))}
        </div>
      </div>
      <pre className="lp-code" aria-hidden="true">
        <Highlighted code={CODE} lang="python" />
      </pre>
      <div className="lp-tests" aria-hidden="true">
        <span className="lp-dots">
          {Array.from({ length: TESTS }, (_, k) => (
            <i key={k} className={k < lit ? 'on' : ''} />
          ))}
        </span>
        {frame === 12 && (
          <span className="lp-pop">
            {SPARKS.map((s, k) => (
              <i key={k} style={{ '--x': `${s.x}px`, '--y': `${s.y}px`, '--r': `${s.r}deg`, '--d': `${s.d}s`, '--c': s.c } as React.CSSProperties} />
            ))}
          </span>
        )}
        <span className={`lp-verdict${passed ? ' ok' : ''}`}>{passed ? 'Accepted' : lit > 0 ? 'Running tests' : 'Ready'}</span>
        <span className="lp-count tnum">
          {lit} of {TESTS}
        </span>
      </div>
    </div>
    </div>
  );
}
