from collections import OrderedDict


class Current:
    """Model the current lock-held callback and recursive pending-flush ordering."""

    def __init__(self):
        self.handlers = OrderedDict()
        self.pending = []
        self.locked = False
        self.log = []

    def listen(self, name, callback):
        if self.locked:
            self.pending.append(("listen", name, callback))
        else:
            self.handlers[name] = callback

    def unlisten(self, name):
        if self.locked:
            self.pending.append(("unlisten", name))
        else:
            self.handlers.pop(name, None)

    def emit(self, label):
        if self.locked:
            self.pending.append(("emit", label))
            return

        self.locked = True
        try:
            for name, callback in list(self.handlers.items()):
                self.log.append((label, name))
                callback(self)
        finally:
            self.locked = False

        pending, self.pending = self.pending, []
        for action in pending:
            if action[0] == "listen":
                self.listen(action[1], action[2])
            elif action[0] == "unlisten":
                self.unlisten(action[1])
            else:
                self.emit(action[1])


class SnapshotQueue:
    """Candidate B: callback snapshots, immediate mutations, selected child emits."""

    class Frame:
        def __init__(self, label, handlers):
            self.label = label
            self.handlers = handlers
            self.children = []

    def __init__(self):
        self.handlers = OrderedDict()
        self.current = None
        self.log = []

    def listen(self, name, callback):
        self.handlers[name] = callback

    def unlisten(self, name):
        self.handlers.pop(name, None)

    def emit(self, label):
        frame = self.Frame(label, list(self.handlers.items()))
        if self.current is not None:
            self.current.children.append(frame)
            return
        self._run(frame)

    def _run(self, frame):
        parent = self.current
        self.current = frame
        for name, callback in frame.handlers:
            self.log.append((frame.label, name))
            callback(self)
        for child in frame.children:
            self._run(child)
        self.current = parent


def scenario(actions_a, actions_b=()):
    def run(model_type):
        model = model_type()
        fired = {"A": False, "B": False}

        def c(_model):
            return

        def apply(manager, actions):
            for action in actions:
                if action == "listenC":
                    manager.listen("C", c)
                elif action == "unlistenB":
                    manager.unlisten("B")
                elif action == "unlistenC":
                    manager.unlisten("C")
                elif action == "emitA1":
                    manager.emit("nested-A1")

        def a(manager):
            if fired["A"]:
                return
            fired["A"] = True
            apply(manager, actions_a)

        def b(manager):
            if fired["B"]:
                return
            fired["B"] = True
            apply(manager, actions_b)

        model.listen("A", a)
        model.listen("B", b)
        model.emit("outer")
        return model.log

    return run


simple_cases = [
    ("unlisten-before-emit", ("unlistenB", "emitA1"), ()),
    ("listen-before-emit", ("listenC", "emitA1"), ()),
    ("emit-before-unlisten", ("emitA1", "unlistenB"), ()),
    ("emit-before-listen", ("emitA1", "listenC"), ()),
    ("later-callback-remove", ("listenC", "emitA1"), ("unlistenC",)),
]

for name, actions_a, actions_b in simple_cases:
    run = scenario(actions_a, actions_b)
    current = run(Current)
    candidate = run(SnapshotQueue)
    assert current == candidate, (name, current, candidate)
    print(f"PASS {name}: {current}")


def deep(model_type):
    model = model_type()
    fired = {"A": False, "B": False, "C": False}

    def c(manager):
        if fired["C"]:
            return
        fired["C"] = True
        manager.emit("nested-C")

    def a(manager):
        if fired["A"]:
            return
        fired["A"] = True
        manager.listen("C", c)
        manager.emit("nested-A1")
        manager.unlisten("B")
        manager.emit("nested-A2")

    def b(manager):
        if fired["B"]:
            return
        fired["B"] = True
        manager.unlisten("C")
        manager.emit("nested-B")

    model.listen("A", a)
    model.listen("B", b)
    model.emit("outer")
    return model.log


current = deep(Current)
candidate = deep(SnapshotQueue)
print("CURRENT deep:", current)
print("CANDIDATE_B deep:", candidate)
assert current != candidate
print("NEGATIVE candidate B changes nested child-emission ordering/selection")
