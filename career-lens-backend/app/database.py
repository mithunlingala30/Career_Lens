"""
Persistence layer.  Production = Firebase Firestore (FirestoreStore).  DB_BACKEND=local uses a JSON file (LocalStore)
with the identical interface - used by the automated tests and as an offline demo mode.

Documents are plain dicts with an integer `id` (doc id = str(id)) plus ISO-8601 `created_at` / `updated_at`.
Only equality filters are used, so no composite Firestore indexes are needed.
"""
import copy
import json
import os
import threading
from datetime import datetime, timezone

from .config import DB_BACKEND, FIREBASE_CREDENTIALS, FIREBASE_PROJECT_ID, LOCAL_DB_PATH


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def pair_id(a: int, b: int) -> int:
    """Deterministic integer id for per-(resume, X) documents, so re-running an analysis overwrites instead of duplicating."""
    return int(a) * 100000 + int(b)


class Batch:
    """Collects writes and applies them together (Firestore WriteBatch)."""
    def __init__(self, store):
        self.s, self.puts, self.deletes = store, [], []

    def put(self, col, doc):
        t = now_iso()
        doc = {**doc}
        doc.setdefault("created_at", t)
        doc["updated_at"] = t
        self.puts.append((col, doc))
        return doc

    def create(self, col, data, id=None):
        return self.put(col, {**data, "id": id if id is not None else self.s.next_id(col)})

    def delete(self, col, id):
        self.deletes.append((col, id))

    def commit(self):
        self.s._commit(self.puts, self.deletes)
        self.puts, self.deletes = [], []


class Store:
    """Shared logic; subclasses implement next_id, _get, _query, _commit, field_values."""
    def create(self, col, data, id=None):
        b = self.batch(); doc = b.create(col, data, id); b.commit(); return doc

    def put(self, col, doc):
        b = self.batch(); out = b.put(col, doc); b.commit(); return out

    def update(self, col, id, patch):
        cur = self._get(col, id)
        if cur is None:
            raise KeyError(f"{col}/{id}")
        cur.update(patch)
        return self.put(col, cur)

    def get(self, col, id):
        return self._get(col, id)

    def delete(self, col, id):
        self._commit([], [(col, id)])

    def where(self, col, **eq):
        return self._query(col, eq)

    def one(self, col, **eq):
        r = self._query(col, eq)
        return r[0] if r else None

    def all(self, col):
        return self._query(col, {})

    def count(self, col, **eq):
        return len(self._query(col, eq))

    def delete_where(self, col, **eq):
        docs = self._query(col, eq)
        self._commit([], [(col, d["id"]) for d in docs])
        return len(docs)

    def batch(self):
        return Batch(self)


class LocalStore(Store):
    def __init__(self, path=None):
        self.path, self.lock, self.data = path, threading.RLock(), {"_counters": {}}
        if path and os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                self.data = json.load(f)

    def _flush(self):
        if not self.path:
            return
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.data, f)
        os.replace(tmp, self.path)

    def next_id(self, col):
        with self.lock:
            c = self.data["_counters"]
            c[col] = c.get(col, 0) + 1
            self._flush()
            return c[col]

    def _get(self, col, id):
        d = self.data.get(col, {}).get(str(id))
        return copy.deepcopy(d) if d is not None else None

    def _query(self, col, eq):
        with self.lock:
            return [copy.deepcopy(d) for d in self.data.get(col, {}).values() if all(d.get(k) == v for k, v in eq.items())]

    def _commit(self, puts, deletes):
        with self.lock:
            for col, doc in puts:
                self.data.setdefault(col, {})[str(doc["id"])] = json.loads(json.dumps(doc))
            for col, id in deletes:
                self.data.get(col, {}).pop(str(id), None)
            self._flush()

    def field_values(self, col, field):
        with self.lock:
            return [d.get(field) for d in self.data.get(col, {}).values()]


class FirestoreStore(Store):
    def __init__(self):
        import firebase_admin
        from firebase_admin import credentials, firestore
        try:
            firebase_admin.get_app()
        except ValueError:
            if not os.path.exists(FIREBASE_CREDENTIALS):
                raise RuntimeError(
                    f"Firebase service-account key not found at {FIREBASE_CREDENTIALS}. In the Firebase console open Project settings -> "
                    "Service accounts -> Generate new private key, save the file there (or set FIREBASE_CREDENTIALS in .env).")
            opts = {"projectId": FIREBASE_PROJECT_ID} if FIREBASE_PROJECT_ID else None
            firebase_admin.initialize_app(credentials.Certificate(FIREBASE_CREDENTIALS), opts)
        self.db = firestore.client()

    def _ref(self, col, id):
        return self.db.collection(col).document(str(id))

    def next_id(self, col):
        from google.cloud.firestore import transactional
        ref = self.db.collection("_counters").document(col)

        @transactional
        def bump(txn):
            snap = ref.get(transaction=txn)
            n = ((snap.to_dict() or {}).get("value", 0) if snap.exists else 0) + 1
            txn.set(ref, {"value": n})
            return n
        return bump(self.db.transaction())

    def _get(self, col, id):
        snap = self._ref(col, id).get()
        return snap.to_dict() if snap.exists else None

    def _query(self, col, eq):
        from google.cloud.firestore_v1.base_query import FieldFilter
        q = self.db.collection(col)
        for k, v in eq.items():
            q = q.where(filter=FieldFilter(k, "==", v))
        return [s.to_dict() for s in q.stream()]

    def _commit(self, puts, deletes):
        ops = [("set", c, d) for c, d in puts] + [("del", c, i) for c, i in deletes]
        for i in range(0, len(ops), 400):               # Firestore limit: 500 writes per batch
            b = self.db.batch()
            for kind, col, x in ops[i:i + 400]:
                if kind == "set":
                    b.set(self._ref(col, x["id"]), x)
                else:
                    b.delete(self._ref(col, x))
            b.commit()

    def field_values(self, col, field):
        return [(s.to_dict() or {}).get(field) for s in self.db.collection(col).select([field]).stream()]


_store = None


def init_store() -> Store:
    global _store
    if _store is None:
        _store = FirestoreStore() if DB_BACKEND == "firestore" else LocalStore(LOCAL_DB_PATH)
    return _store


def get_store() -> Store:
    return init_store()
