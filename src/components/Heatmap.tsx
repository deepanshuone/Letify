import { useMemo } from 'react';

const WEEKS = 53;
const CELL = 11;
const GAP = 3;
const STEP = CELL + GAP;
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const DAY_MS = 86_400_000;

const key = (t: number) => new Date(t).toISOString().slice(0, 10);

export const level = (n: number) => (n <= 0 ? 0 : n === 1 ? 1 : n <= 3 ? 2 : n <= 6 ? 3 : 4);

export interface HeatCell {
  day: string;
  count: number;
  week: number;
  dow: number;
}

/** The last 53 weeks ending with the week of `today` (weeks start on Sunday). */
export function heatCells(activity: Record<string, number>, today: string): HeatCell[] {
  const end = Date.parse(today + 'T00:00:00Z');
  const dow = new Date(end).getUTCDay();
  const start = end - (7 * (WEEKS - 1) + dow) * DAY_MS;
  const out: HeatCell[] = [];
  for (let t = start, i = 0; t <= end; t += DAY_MS, i++) {
    const day = key(t);
    out.push({ day, count: activity[day] ?? 0, week: Math.floor(i / 7), dow: i % 7 });
  }
  return out;
}

function monthTotals(cells: HeatCell[]): { label: string; count: number; days: number }[] {
  const map = new Map<string, { label: string; count: number; days: number }>();
  for (const c of cells) {
    const k = c.day.slice(0, 7);
    const m = map.get(k) ?? { label: `${MONTHS[Number(c.day.slice(5, 7)) - 1]} ${c.day.slice(0, 4)}`, count: 0, days: 0 };
    m.count += c.count;
    if (c.count) m.days++;
    map.set(k, m);
  }
  return [...map.values()];
}

export function Heatmap({ activity, today }: { activity: Record<string, number>; today: string }) {
  const cells = useMemo(() => heatCells(activity, today), [activity, today]);
  const total = cells.reduce((a, c) => a + c.count, 0);
  const labels = cells.filter((c) => c.dow === 0 && Number(c.day.slice(8, 10)) <= 7);
  const months = monthTotals(cells);
  const width = WEEKS * STEP;
  const height = 7 * STEP + 16;
  return (
    <div>
      <div className="heat-scroll">
        <svg className="heat" width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`${total} submissions in the last year`}>
          {labels.map((c) => (
            <text key={c.day} x={c.week * STEP} y={10} className="heat-label">
              {MONTHS[Number(c.day.slice(5, 7)) - 1]}
            </text>
          ))}
          {cells.map((c) => (
            <rect key={c.day} className={`hm hm${level(c.count)}`} x={c.week * STEP} y={16 + c.dow * STEP} width={CELL} height={CELL} rx={2.5}>
              <title>{`${c.count} submission${c.count === 1 ? '' : 's'} on ${c.day}`}</title>
            </rect>
          ))}
        </svg>
      </div>
      <div className="heat-legend" aria-hidden="true">
        Less
        {[0, 1, 2, 3, 4].map((l) => (
          <svg key={l} width={CELL} height={CELL}>
            <rect className={`hm hm${l}`} width={CELL} height={CELL} rx={2.5} />
          </svg>
        ))}
        More
      </div>
      <details className="heat-table">
        <summary>Show as a table</summary>
        <table>
          <thead>
            <tr>
              <th scope="col">Month</th>
              <th scope="col">Submissions</th>
              <th scope="col">Active days</th>
            </tr>
          </thead>
          <tbody>
            {months.map((m) => (
              <tr key={m.label}>
                <th scope="row">{m.label}</th>
                <td className="tnum">{m.count}</td>
                <td className="tnum">{m.days}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </div>
  );
}
