"""
Pilot protocol state machine.

The protocol enforces, in code, the temporal order required by the
authoritative design — most importantly:

  * Family C (hidden verification) may be generated ONLY after every
    arm's interaction/private-critique phase has fully completed, and
  * each phase runs in its own session (the arm layer enforces fresh
    contexts; the protocol records the session boundary).

The generator itself is a pure function; this module owns the gate.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .generator import Task, generate_family_c


class ProtocolError(RuntimeError):
    pass


@dataclass
class ProtocolLog:
    started_iso: str = ""
    interaction_completed_iso: Optional[str] = None
    family_c_generated_iso: Optional[str] = None
    family_c_attempted_before: List[str] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "started_iso": self.started_iso,
            "interaction_completed_iso": self.interaction_completed_iso,
            "family_c_generated_iso": self.family_c_generated_iso,
            "family_c_attempted_before": list(self.family_c_attempted_before),
            "events": list(self.events),
        }


class PilotProtocol:
    """State machine guarding the generation of Family C."""

    def __init__(self) -> None:
        self.log = ProtocolLog(
            started_iso=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        self._interaction_done = False
        self._family_c_generated = False

    def event(self, name: str, **extra: Any) -> None:
        entry = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                 "event": name}
        entry.update(extra)
        self.log.events.append(entry)

    def mark_interaction_complete(self) -> None:
        """Called after ALL arms have finished their interaction /
        private-critique phase (and the retention and transfer legs for
        arms that run before Family C generation)."""
        if self._interaction_done:
            return
        self._interaction_done = True
        self.log.interaction_completed_iso = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.event("interaction_complete")

    def interaction_complete(self) -> bool:
        return self._interaction_done

    def generate_family_c(self, seed: int, tier: int,
                          spec: Optional[Dict[str, Any]] = None
                          ) -> List[Task]:
        """The hidden-verification family.  Refuses to run before the
        interaction phase has completed, and refuses to run twice."""
        if not self._interaction_done:
            self.log.family_c_attempted_before.append(time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
            raise ProtocolError(
                "Family C generation attempted before the interaction "
                "phase completed — refused by protocol gate")
        if self._family_c_generated:
            raise ProtocolError("Family C already generated for this run")
        tasks = generate_family_c(seed=seed, tier=tier, spec=spec)
        self._family_c_generated = True
        self.log.family_c_generated_iso = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.event("family_c_generated", seed=seed, tier=tier,
                   task_ids=[t.task_id for t in tasks])
        return tasks

    def to_dict(self) -> Dict[str, Any]:
        return self.log.to_dict()
