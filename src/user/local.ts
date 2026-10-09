import { isLang } from '../core/languages';
import { STORAGE_PREFIX } from '../config';
import { store } from '../core/storage';
import { emptyData, merge, normalize, type UserData } from './model';

/* Where UserData lives in this browser. Two entries: everything except code (small, written at once) and the code
   entries (written a moment after typing stops). */

const MAIN = 'ud';
const CODE = 'udcode';
const MIGRATED = 'udmigrated';

/** Older versions kept `solved` and one key per code file. Fold them into the new layout once. */
function migrateOld(): UserData {
  const out = emptyData();
  const solved = store.get<Record<string, { lang?: unknown; at?: unknown }>>('solved', {});
  for (const [id, v] of Object.entries(solved ?? {})) {
    if (v && isLang(v.lang) && typeof v.at === 'number') out.solved[id] = { lang: v.lang, at: v.at };
  }
  try {
    const prefix = STORAGE_PREFIX + 'code.';
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i);
      if (!k || !k.startsWith(prefix)) continue;
      const m = /^(.+)\.(python|javascript|cpp|java)$/.exec(k.slice(prefix.length));
      const text = m && JSON.parse(localStorage.getItem(k) ?? 'null');
      if (m && typeof text === 'string') out.code[`${m[1]}.${m[2]}`] = { text, at: 1 };
    }
  } catch {
    /* storage unavailable */
  }
  return out;
}

export function loadLocal(): UserData {
  const main = normalize(store.get<unknown>(MAIN, null));
  const code = normalize({ code: store.get<unknown>(CODE, null) }).code;
  let data: UserData = { ...main, code };
  if (!store.get<boolean>(MIGRATED, false)) {
    data = merge(data, migrateOld());
    store.set(MIGRATED, true);
    saveMain(data);
    saveCode(data);
  }
  return data;
}

export function saveMain(d: UserData): void {
  store.set(MAIN, { ...d, code: {} });
}

export function saveCode(d: UserData): void {
  store.set(CODE, d.code);
}

export function clearLocal(): void {
  store.set(MAIN, null);
  store.set(CODE, null);
}
