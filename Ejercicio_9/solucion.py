"""Solución al Ejercicio 1: Encadenamiento en la biblioteca.

Implementación de encadenamiento hacia adelante (forward chaining) exhaustivo
y encadenamiento hacia atrás (backward chaining) dirigido por metas sobre
cláusulas definidas.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import yaml


# ==============================================================================
# 1. Representación de Átomos, Reglas y Base de Conocimiento
# ==============================================================================

_ATOM_REGEX = re.compile(r"^([A-Za-z_][\w]*)\s*(?:\((.*)\))?\s*$")


@dataclass(frozen=True)
class Atom:
    predicate: str
    args: tuple[str, ...]

    def __str__(self) -> str:
        if not self.args:
            return self.predicate
        return f"{self.predicate}({', '.join(self.args)})"


def is_variable(term: str) -> bool:
    """Una variable inicia con minúscula; una constante con mayúscula."""
    return bool(term) and term[0].islower()


def parse_atom(text: str) -> Atom:
    text = text.strip()
    match = _ATOM_REGEX.match(text)
    if not match:
        raise ValueError(f"No se pudo parsear el átomo: {text!r}")
    predicate, raw_args = match.group(1), match.group(2)
    if raw_args is None or raw_args.strip() == "":
        return Atom(predicate, ())
    args = tuple(part.strip() for part in raw_args.split(","))
    return Atom(predicate, args)


@dataclass(frozen=True)
class Rule:
    rule_id: str
    premises: tuple[Atom, ...]
    head: Atom

    def __str__(self) -> str:
        body = " ∧ ".join(str(p) for p in self.premises) if self.premises else "true"
        return f"{self.rule_id}: {body} → {self.head}"


@dataclass
class KnowledgeBase:
    facts: list[Atom]
    rules: list[Rule]
    query: Atom | None = None

    def clone(self) -> KnowledgeBase:
        return KnowledgeBase(list(self.facts), list(self.rules), self.query)


def load_kb(path: str | Path) -> KnowledgeBase:
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    facts = [parse_atom(item) for item in data.get("facts", [])]
    rules = []
    for i, item in enumerate(data.get("rules", []), start=1):
        rule_id = str(item.get("id", f"R{i}"))
        premises = tuple(parse_atom(p) for p in item.get("if", []))
        head = parse_atom(item["then"])
        rules.append(Rule(rule_id, premises, head))

    raw_query = data.get("query")
    query = parse_atom(raw_query) if raw_query else None
    return KnowledgeBase(facts, rules, query)


# ==============================================================================
# 2. Unificación y Sustituciones
# ==============================================================================

def apply_term(term: str, subst: dict[str, str]) -> str:
    seen: set[str] = set()
    while is_variable(term) and term in subst and term not in seen:
        seen.add(term)
        term = subst[term]
    return term


def apply_atom(atom: Atom, subst: dict[str, str]) -> Atom:
    return Atom(atom.predicate, tuple(apply_term(a, subst) for a in atom.args))


def _occurs(var: str, term: str, subst: dict[str, str]) -> bool:
    term = apply_term(term, subst)
    return var == term


def unify(a: Atom | str, b: Atom | str, subst: dict[str, str] | None = None) -> dict[str, str] | None:
    if subst is None:
        subst = {}
    else:
        subst = dict(subst)

    if isinstance(a, Atom) and isinstance(b, Atom):
        if a.predicate != b.predicate or len(a.args) != len(b.args):
            return None
        for left, right in zip(a.args, b.args):
            subst = unify(left, right, subst)
            if subst is None:
                return None
        return subst

    if isinstance(a, Atom) or isinstance(b, Atom):
        return None

    a = apply_term(a, subst)
    b = apply_term(b, subst)
    if a == b:
        return subst
    if is_variable(a):
        if _occurs(a, b, subst):
            return None
        subst[a] = b
        return subst
    if is_variable(b):
        if _occurs(b, a, subst):
            return None
        subst[b] = a
        return subst
    return None


def format_subst(subst: dict[str, str]) -> str:
    if not subst:
        return "{}"
    parts = ", ".join(f"{k}/{v}" for k, v in sorted(subst.items()))
    return "{" + parts + "}"


def standardize_rule(rule: Rule, counter: int) -> Rule:
    mapping: dict[str, str] = {}

    def rename(atom: Atom) -> Atom:
        new_args = []
        for arg in atom.args:
            if is_variable(arg):
                mapping.setdefault(arg, f"{arg}_{counter}")
                new_args.append(mapping[arg])
            else:
                new_args.append(arg)
        return Atom(atom.predicate, tuple(new_args))

    return Rule(rule.rule_id, tuple(rename(p) for p in rule.premises), rename(rule.head))


# ==============================================================================
# 3. Encadenamiento hacia adelante (Forward Chaining)
# ==============================================================================

@dataclass
class InferenceResult:
    proved: bool
    subst: dict[str, str] | None
    inferred: list[Atom]
    events: list[str] = field(default_factory=list)


def satisfy_premises(premises: tuple[Atom, ...], facts: list[Atom], subst: dict[str, str]) -> list[dict[str, str]]:
    if not premises:
        return [subst]
    first, rest = premises[0], premises[1:]
    goal = apply_atom(first, subst)
    results: list[dict[str, str]] = []
    for fact in facts:
        theta = unify(goal, fact, subst)
        if theta is not None:
            results.extend(satisfy_premises(rest, facts, theta))
    return results


def forward_chain(kb: KnowledgeBase, query: Atom, max_rounds: int = 50) -> InferenceResult:
    facts = list(kb.facts)
    inferred: list[Atom] = []
    events: list[str] = [
        f"Agenda (given facts): {', '.join(str(f) for f in facts) or '(empty)'}",
        f"Query: {query}",
    ]

    counter = 0
    for round_no in range(1, max_rounds + 1):
        new_atoms: list[Atom] = []
        events.append(f"--- round {round_no} ---")
        for rule in kb.rules:
            counter += 1
            fresh = standardize_rule(rule, counter)
            for theta in satisfy_premises(fresh.premises, facts, {}):
                head = apply_atom(fresh.head, theta)
                if head in facts or head in new_atoms:
                    continue
                new_atoms.append(head)
                inferred.append(head)
                events.append(f"Fire {rule.rule_id}  {format_subst(theta)}  ⇒  {head}")

        if not new_atoms:
            events.append("No new facts.")
            break
        facts.extend(new_atoms)

    for fact in facts:
        theta = unify(query, fact, {})
        if theta is not None:
            events.append(f"Query proved: {query}")
            return InferenceResult(True, theta, inferred, events)

    events.append("Query not proved.")
    return InferenceResult(False, None, inferred, events)


# ==============================================================================
# 4. Encadenamiento hacia atrás (Backward Chaining)
# ==============================================================================

def backward_chain(kb: KnowledgeBase, query: Atom, max_depth: int = 25) -> InferenceResult:
    events: list[str] = [f"Query: {query}"]
    counter = [0]
    visited_goals: list[Atom] = []

    def indent(depth: int) -> str:
        return "  " * depth

    def bc_or(goal: Atom, subst: dict[str, str], depth: int, stack: tuple[str, ...]) -> dict[str, str] | None:
        goal = apply_atom(goal, subst)
        key = str(goal)
        if key in stack:
            events.append(f"{indent(depth)}loop: {goal} already on the goal stack — skip")
            return None
        if depth > max_depth:
            events.append(f"{indent(depth)}max depth at {goal}")
            return None

        events.append(f"{indent(depth)}goal  {goal}")
        visited_goals.append(goal)

        # 1. Probar primero hechos
        for fact in kb.facts:
            theta = unify(goal, fact, subst)
            if theta is not None:
                events.append(f"{indent(depth)}fact   {fact}  {format_subst(theta)}")
                return theta

        # 2. Probar reglas en orden
        for rule in kb.rules:
            counter[0] += 1
            fresh = standardize_rule(rule, counter[0])
            theta = unify(goal, fresh.head, subst)
            if theta is None:
                continue
            events.append(f"{indent(depth)}rule   {rule.rule_id}  {format_subst(theta)}")
            answer = bc_and(fresh.premises, theta, depth + 1, stack + (key,))
            if answer is not None:
                return answer

        events.append(f"{indent(depth)}fail   {goal}")
        return None

    def bc_and(premises: tuple[Atom, ...], subst: dict[str, str], depth: int, stack: tuple[str, ...]) -> dict[str, str] | None:
        if not premises:
            return subst
        first, rest = premises[0], premises[1:]
        theta = bc_or(first, subst, depth, stack)
        if theta is None:
            return None
        return bc_and(rest, theta, depth, stack)

    found = bc_or(query, {}, 0, ())
    proved = found is not None
    events.append("Query proved." if proved else "Query not proved.")

    unique_goals: list[Atom] = []
    seen = set()
    for g in visited_goals:
        if str(g) not in seen:
            seen.add(str(g))
            unique_goals.append(g)

    return InferenceResult(proved, found, unique_goals, events)


# ==============================================================================
# 5. Ejecución Principal para la Tarea
# ==============================================================================

def run_assignment() -> None:
    kb_path = Path(__file__).resolve().parent / "biblioteca.yaml"
    if not kb_path.exists():
        kb_path = Path(__file__).resolve().parent.parent / "project" / "kb" / "biblioteca.yaml"

    kb = load_kb(kb_path)
    queries = ["AccesoNoche(Ana)", "AccesoNoche(Luis)", "AccesoNoche(Marta)"]

    print("=" * 70)
    print("EJERCICIO 1: ENCADENAMIENTO EN LA BIBLIOTECA")
    print("=" * 70)

    for q_str in queries:
        query = parse_atom(q_str)
        print(f"\n==================== CONSULTA: {query} ====================")
        fc = forward_chain(kb, query)
        bc = backward_chain(kb, query)

        print("\n--- Encadenamiento Hacia Adelante (Forward Chaining) ---")
        for line in fc.events:
            print(line)
        print(f"Resultado FC: {'SÍ (Probada)' if fc.proved else 'NO (No probada)'}")
        print(f"Átomos inferidos: {', '.join(str(a) for a in fc.inferred)}")

        print("\n--- Encadenamiento Hacia Atrás (Backward Chaining) ---")
        for line in bc.events:
            print(line)
        print(f"Resultado BC: {'SÍ (Probada)' if bc.proved else 'NO (No probada)'}")
        print(f"Metas visitadas: {', '.join(str(a) for a in bc.inferred)}")

    print("\n" + "=" * 70)
    print("EXPERIMENTO ADICIONAL: Hecho TieneCredencial(Luis)")
    print("=" * 70)
    kb_modified = kb.clone()
    kb_modified.facts.append(parse_atom("TieneCredencial(Luis)"))
    query_luis = parse_atom("AccesoNoche(Luis)")

    fc_mod = forward_chain(kb_modified, query_luis)
    bc_mod = backward_chain(kb_modified, query_luis)

    print("\n--- FC con TieneCredencial(Luis) ---")
    for line in fc_mod.events:
        print(line)
    print(f"Resultado FC: {'SÍ (Probada)' if fc_mod.proved else 'NO (No probada)'}")
    print(f"Total átomos inferidos: {', '.join(str(a) for a in fc_mod.inferred)}")

    print("\n--- BC con TieneCredencial(Luis) ---")
    for line in bc_mod.events:
        print(line)
    print(f"Resultado BC: {'SÍ (Probada)' if bc_mod.proved else 'NO (No probada)'}")


if __name__ == "__main__":
    run_assignment()

