"""Part 2 - Simple reflex agent (AIMA 4e Figure 2.10).

Every decision must be a short, ORDERED list of condition-action rules
applied to the CURRENT percept only. No internal state is allowed in this
part -- that is what Part 3 adds. Once you finish this one, run it in the
window (``python tools/play.py --agent simple_reflex``) and watch it clear
the pellets near it quickly, then pace back and forth once that corridor
is empty: it cannot tell "I already cleared this" from "this was always
empty", because both look like the same percept. That failure is exactly
why AIMA moves on to model-based reflex agents next.

"""

from __future__ import annotations

from dataclasses import dataclass

from pacman.maze import DIRECTION_NAMES, MazeModel

AGENT_NAME = "simple_reflex"


@dataclass(frozen=True)
class Percept:
    player: tuple[int, int]
    pellets: frozenset[tuple[int, int]]
    power_pellets: frozenset[tuple[int, int]]
    legal_actions: tuple[tuple[int, int], ...]
    current_direction: tuple[int, int]
    released_ghosts: tuple[tuple[int, int], ...]
    frightened_time_remaining: float

    @property
    def frightened(self) -> bool:
        """True while power-pellet mode is active. Works once you add
        frightened_time_remaining above."""
        return getattr(self, "frightened_time_remaining", 0.0) > 0.0


class SimpleReflexAgent:
    percept_class = Percept

    def __init__(self, maze: MazeModel):
        self.maze = maze
        self.last_reason = "Waiting for first percept."

    def choose_action(self, percept: Percept) -> tuple[int, int]:
        """Apply, in order, the first rule that fires:

          1. If there are no legal actions, set last_reason to a string
             containing "No legal" and return (0, 0).
          2. Never step onto a tile occupied by a dangerous (non-frightened)
             released ghost, UNLESS every legal action does (then you have
             no choice -- take any legal action).
          3. If frightened, and a ghost is on an adjacent (safe-filtered)
             tile, step onto it.
          4. Otherwise, if an adjacent tile has a power pellet, take it.
          5. Otherwise, if an adjacent tile has a regular pellet, take it.
          6. Otherwise, keep going in ``percept.current_direction`` if that
             is still one of your safe options.
          7. Otherwise, take the first safe action.

        Use ``self.maze.step(percept.player, action)`` to find the tile
        each action lands on. Use ``self._commit`` to set last_reason and
        return a chosen action in one place, so every branch reports the
        same way -- see its docstring.
        """
        if percept.legal_actions == ():
            self.last_reason = "No legal"
            return (0, 0)

        safe_actions = list(percept.legal_actions)
        for action in percept.legal_actions:
            next_location = self.maze.step(percept.player, action)
            if percept.released_ghosts.__contains__(next_location):
                if percept.frightened_time_remaining > 0:
                    return self._commit(action, "Rule 3")
                if len(safe_actions) > 1:
                    safe_actions.remove(action)
                    continue
                else:
                    return self._commit(action, "Rule 2")
            elif percept.power_pellets.__contains__(next_location):
                return self._commit(action, "Rule 4")
            elif percept.pellets.__contains__(next_location):
                return self._commit(action, "Rule 5")
        if safe_actions.__contains__(percept.current_direction):
                return self._commit(percept.current_direction, "Rule 6")
        return self._commit(safe_actions[0], "Rule 7")

    def _commit(self, action: tuple[int, int], rule: str) -> tuple[int, int]:
        """Set last_reason to e.g. 'RIGHT | rule: adjacent pellet' and
        return action. Call this from every branch of choose_action
        instead of setting last_reason by hand in each one."""
        self.last_reason = f"{DIRECTION_NAMES[action]} | rule: {rule}"
        return action
