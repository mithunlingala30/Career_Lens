import { useState, useEffect, useCallback, useRef } from 'react';
import { errMsg } from '../services/api';

/** Runs an async loader whenever deps change. Returns {data, loading, error, status, reload}. */
export default function useFetch(loader, deps = [], enabled = true) {
  const [state, setState] = useState({ data: null, loading: enabled, error: '', status: 0 });
  const seq = useRef(0);
  const run = useCallback(() => {
    if (!enabled) { setState({ data: null, loading: false, error: '', status: 0 }); return Promise.resolve(); }
    const id = ++seq.current;
    setState((s) => ({ ...s, loading: true, error: '' }));
    return loader().then(
      (data) => id === seq.current && setState({ data, loading: false, error: '', status: 200 }),
      (e) => id === seq.current && setState({ data: null, loading: false, error: errMsg(e), status: e.response?.status || 0 })
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, enabled]);
  useEffect(() => { run(); }, [run]);
  return { ...state, reload: run };
}
