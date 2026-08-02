#!/usr/bin/env python3
"""Apply the bounded inherited Worker-global receiver repair.

Target source fence:
  teamleaderleo/workerd@18a117c28773cd7aa0ee599e03439c5fbbf06584

Run from a clean workerd checkout at that exact revision. The script aborts if
any expected source fragment differs, so it must not silently patch a moved
head. Format and execute the target-native tests after application.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path.cwd()


def replace_once(path: str, old: str, new: str) -> None:
    file_path = ROOT / path
    text = file_path.read_text()
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one match, found {count}")
    file_path.write_text(text.replace(old, new, 1))


def replace_exact_count(path: str, old: str, new: str, expected: int) -> None:
    file_path = ROOT / path
    text = file_path.read_text()
    count = text.count(old)
    if count != expected:
        raise RuntimeError(
            f"{path}: expected {expected} matches for {old!r}, found {count}"
        )
    file_path.write_text(text.replace(old, new))


GLOBALS = "types/src/transforms/globals.ts"

replace_once(
    GLOBALS,
    """      const declarations = collectNamedDeclarations(node);
      const visitor = createGlobalScopeVisitor(ctx, checker, declarations);
      return ts.visitEachChild(node, visitor, ctx);
""",
    """      const declarations = collectNamedDeclarations(node);
      const contextGlobalDeclarations = collectContextGlobalDeclarations(
        ctx,
        checker,
        declarations
      );
      const transformedDeclarations = replaceContextGlobalDeclarations(
        declarations,
        contextGlobalDeclarations
      );
      const visitor = createGlobalScopeVisitor(
        ctx,
        checker,
        transformedDeclarations,
        contextGlobalDeclarations
      );
      return ts.visitEachChild(node, visitor, ctx);
""",
)

replace_once(
    GLOBALS,
    "function widenContextGlobalScopeDeclaration(\n",
    "function widenContextGlobalDeclaration(\n",
)

replace_once(
    GLOBALS,
    """function createGlobalScopeVisitor(
  ctx: ts.TransformationContext,
  checker: ts.TypeChecker,
  declarations: Map<string, NamedDeclaration[]>
): ts.Visitor {
""",
    """function collectContextGlobalDeclarations(
  ctx: ts.TransformationContext,
  checker: ts.TypeChecker,
  declarations: Map<string, NamedDeclaration[]>
): Map<NamedDeclaration, NamedDeclaration> {
  const roots = declarations.get('ServiceWorkerGlobalScope');
  assert.strictEqual(
    roots?.length,
    1,
    `Expected one transformed ServiceWorkerGlobalScope declaration, got ${roots?.length ?? 0}`
  );

  const result = new Map<NamedDeclaration, NamedDeclaration>();
  const visit = (node: NamedDeclaration): void => {
    if (result.has(node)) return;
    result.set(node, widenContextGlobalDeclaration(ctx, node));

    for (const clause of node.heritageClauses ?? []) {
      for (const superType of clause.types) {
        const declaration = getHeritageDeclaration(
          checker,
          declarations,
          superType,
          superType
        );
        // The generated source and current Worker-global hierarchy are
        // top-level. Nested declarations retain checker identity for extraction
        // but cannot be replaced in this top-level declaration map.
        if (ts.isSourceFile(declaration.parent)) visit(declaration);
      }
    }
  };

  visit(roots[0]);
  return result;
}

function replaceContextGlobalDeclarations(
  declarations: Map<string, NamedDeclaration[]>,
  replacements: Map<NamedDeclaration, NamedDeclaration>
): Map<string, NamedDeclaration[]> {
  const result = new Map<string, NamedDeclaration[]>();
  for (const [name, named] of declarations) {
    result.set(
      name,
      named.map((declaration) => replacements.get(declaration) ?? declaration)
    );
  }
  return result;
}

function createGlobalScopeVisitor(
  ctx: ts.TransformationContext,
  checker: ts.TypeChecker,
  declarations: Map<string, NamedDeclaration[]>,
  contextGlobalDeclarations: Map<NamedDeclaration, NamedDeclaration>
): ts.Visitor {
""",
)

replace_once(
    GLOBALS,
    """  const serviceWorkerGlobalScopeVisitor: ts.Visitor = (node) => {
    if (
      (ts.isInterfaceDeclaration(node) || ts.isClassDeclaration(node)) &&
      node.name !== undefined &&
      node.name.text === 'ServiceWorkerGlobalScope'
    ) {
      const globalScope = widenContextGlobalScopeDeclaration(ctx, node);
      return [globalScope, ...extractGlobalNodes(globalScope)];
    }
    return node;
  };
""",
    """  const serviceWorkerGlobalScopeVisitor: ts.Visitor = (node) => {
    if (
      (ts.isInterfaceDeclaration(node) || ts.isClassDeclaration(node)) &&
      node.name !== undefined
    ) {
      const contextGlobal = contextGlobalDeclarations.get(node);
      if (node.name.text === 'ServiceWorkerGlobalScope') {
        assert(contextGlobal !== undefined);
        return [contextGlobal, ...extractGlobalNodes(contextGlobal)];
      }
      if (contextGlobal !== undefined) return contextGlobal;
    }
    return node;
  };
""",
)

replace_once(
    "types/test/transforms/globals.spec.ts",
    """    .replaceAll(
      'this: __JSG_GENERATED_RECEIVER__<EventTarget<EventMap>>',
      'this: EventTarget<EventMap>'
    )
""",
    """    .replaceAll(
      'this: __JSG_GENERATED_RECEIVER__<EventTarget<EventMap>>',
      'this: EventTarget<EventMap> | typeof globalThis | null | void'
    )
""",
)

replace_exact_count(
    "types/test/index.spec.ts",
    "this: EventTarget<EventMap>,",
    "this: EventTarget<EventMap> | typeof globalThis | null | void,",
    2,
)

inherited_type_test = ROOT / "types/test/types/inherited-global-receiver.ts"
if inherited_type_test.exists():
    raise RuntimeError(f"{inherited_type_test}: file already exists")
inherited_type_test.write_text(
    """const inheritedType = 'fetch' as const;
const inheritedHandler = (
  event: WorkerGlobalScopeEventMap[typeof inheritedType]
) => void event;

const fromSelf = self.addEventListener;
fromSelf(inheritedType, inheritedHandler);
fromSelf.call(undefined, inheritedType, inheritedHandler);
fromSelf.call(null, inheritedType, inheritedHandler);
fromSelf.call(globalThis, inheritedType, inheritedHandler);
fromSelf.call(self, inheritedType, inheritedHandler);

// @ts-expect-error Unrelated objects are not legal owning receivers.
fromSelf.call({}, inheritedType, inheritedHandler);

const target = new EventTarget<{ probe: Event }>();
const targetHandler = (event: Event) => void event;
const fromTarget = target.addEventListener;
fromTarget('probe', targetHandler);
fromTarget.call(undefined, 'probe', targetHandler);
fromTarget.call(null, 'probe', targetHandler);
fromTarget.call(globalThis, 'probe', targetHandler);
fromTarget.call(self, 'probe', targetHandler);
fromTarget.call(target, 'probe', targetHandler);

// @ts-expect-error Unrelated objects are not legal owning receivers.
fromTarget.call({}, 'probe', targetHandler);
"""
)

print("Applied inherited Worker-global ancestry receiver repair.")
print("Next: format, run focused tests, run //types/..., and regenerate snapshots.")
