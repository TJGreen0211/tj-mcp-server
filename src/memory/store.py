"""Knowledge graph storage backed by a JSONL file."""

import json
from pathlib import Path
from typing import Any

from memory.config import get_settings


def _resolve_memory_path() -> Path:
    """Resolve memory file path from settings or default to package dir."""
    settings = get_settings()
    if settings.memory_file_path:
        p = Path(settings.memory_file_path)
        return p if p.is_absolute() else Path(__file__).parent / p

    return Path(__file__).parent / "memory.jsonl"


def _migrate_legacy(memory_path: Path) -> None:
    """Migrate legacy memory.json to memory.jsonl if needed."""
    old_path = memory_path.with_suffix(".json")
    if old_path.exists() and not memory_path.exists():
        print(
            f"DETECTED: Found legacy {old_path.name}, migrating to {memory_path.name}"
        )
        old_path.rename(memory_path)
        print(f"COMPLETED: Successfully migrated {old_path.name} to {memory_path.name}")


class KnowledgeGraphManager:
    """Manages a knowledge graph stored as JSONL on disk."""

    def __init__(self, memory_path: str | Path | None = None):
        self._path = Path(memory_path) if memory_path else _resolve_memory_path()
        _migrate_legacy(self._path)

    def _load_graph(self) -> dict[str, list[dict[str, Any]]]:
        """Load the graph from the JSONL file."""
        if not self._path.exists():
            return {"entities": [], "relations": []}

        lines = self._path.read_text(encoding="utf-8").splitlines()
        graph: dict[str, list[dict[str, Any]]] = {"entities": [], "relations": []}

        for line in lines:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            if item.get("type") == "entity":
                graph["entities"].append({
                    "name": item["name"],
                    "entityType": item["entityType"],
                    "observations": item["observations"],
                })
            elif item.get("type") == "relation":
                graph["relations"].append({
                    "from": item["from"],
                    "to": item["to"],
                    "relationType": item["relationType"],
                })

        return graph

    def _save_graph(self, graph: dict[str, list[dict[str, Any]]]) -> None:
        """Serialize the graph back to the JSONL file."""
        lines: list[str] = []
        for e in graph["entities"]:
            lines.append(json.dumps({
                "type": "entity",
                "name": e["name"],
                "entityType": e["entityType"],
                "observations": e["observations"],
            }))
        for r in graph["relations"]:
            lines.append(json.dumps({
                "type": "relation",
                "from": r["from"],
                "to": r["to"],
                "relationType": r["relationType"],
            }))
        self._path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

    def create_entities(self, entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Create new entities, skipping duplicates by name."""
        graph = self._load_graph()
        existing_names = {e["name"] for e in graph["entities"]}
        new = [e for e in entities if e["name"] not in existing_names]
        graph["entities"].extend(new)
        self._save_graph(graph)
        return new

    def create_relations(self, relations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Create new relations, skipping exact duplicates."""
        graph = self._load_graph()
        existing = {
            (r["from"], r["to"], r["relationType"]) for r in graph["relations"]
        }
        new = [
            r for r in relations
            if (r["from"], r["to"], r["relationType"]) not in existing
        ]
        graph["relations"].extend(new)
        self._save_graph(graph)
        return new

    def add_observations(
        self, observations: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Add observations to existing entities."""
        graph = self._load_graph()
        results: list[dict[str, Any]] = []

        for obs in observations:
            entity = next((e for e in graph["entities"] if e["name"] == obs["entityName"]), None)
            if not entity:
                raise ValueError(f"Entity with name {obs['entityName']} not found")
            new_obs = [c for c in obs["contents"] if c not in entity["observations"]]
            entity["observations"].extend(new_obs)
            results.append({
                "entityName": obs["entityName"],
                "addedObservations": new_obs,
            })

        self._save_graph(graph)
        return results

    def delete_entities(self, entity_names: list[str]) -> None:
        """Delete entities and all their relations."""
        graph = self._load_graph()
        names_set = set(entity_names)
        graph["entities"] = [e for e in graph["entities"] if e["name"] not in names_set]
        graph["relations"] = [
            r for r in graph["relations"]
            if r["from"] not in names_set and r["to"] not in names_set
        ]
        self._save_graph(graph)

    def delete_observations(self, deletions: list[dict[str, Any]]) -> None:
        """Delete specific observations from entities."""
        graph = self._load_graph()
        for d in deletions:
            entity = next((e for e in graph["entities"] if e["name"] == d["entityName"]), None)
            if entity:
                obs_set = set(d["observations"])
                entity["observations"] = [o for o in entity["observations"] if o not in obs_set]
        self._save_graph(graph)

    def delete_relations(self, relations: list[dict[str, Any]]) -> None:
        """Delete specific relations from the graph."""
        graph = self._load_graph()
        to_delete = {(r["from"], r["to"], r["relationType"]) for r in relations}
        graph["relations"] = [
            r for r in graph["relations"]
            if (r["from"], r["to"], r["relationType"]) not in to_delete
        ]
        self._save_graph(graph)

    def read_graph(self) -> dict[str, list[dict[str, Any]]]:
        """Read the entire knowledge graph."""
        return self._load_graph()

    def search_nodes(self, query: str) -> dict[str, list[dict[str, Any]]]:
        """Search entities by name, type, or observation content."""
        graph = self._load_graph()
        query_lower = query.lower()

        filtered_entities = [
            e for e in graph["entities"]
            if query_lower in e["name"].lower()
            or query_lower in e["entityType"].lower()
            or any(query_lower in o.lower() for o in e["observations"])
        ]

        filtered_names = {e["name"] for e in filtered_entities}
        filtered_relations = [
            r for r in graph["relations"]
            if r["from"] in filtered_names or r["to"] in filtered_names
        ]

        return {"entities": filtered_entities, "relations": filtered_relations}

    def open_nodes(self, names: list[str]) -> dict[str, list[dict[str, Any]]]:
        """Retrieve specific entities by name and their connected relations."""
        graph = self._load_graph()
        names_set = set(names)

        filtered_entities = [e for e in graph["entities"] if e["name"] in names_set]
        filtered_relations = [
            r for r in graph["relations"]
            if r["from"] in names_set or r["to"] in names_set
        ]

        return {"entities": filtered_entities, "relations": filtered_relations}
