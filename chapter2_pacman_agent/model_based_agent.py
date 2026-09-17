"""Part 3 - Model-based reflex agent (AIMA 4e Figures 2.11 / 2.12).

This agent adds exactly one thing on top of Part 2: internal state,
updated every turn from the percept sequence, that lets it distinguish "I
have already cleared this tile" from "this tile just happens to be
empty". It is still a REFLEX agent -- action selection is still a short
list of condition-action rules, not a scored search over alternatives
(that upgrade is Part 5). The rules just get to consult memory as one
more condition now.

Rules 1-3 below (ghost avoidance, eating a frightened ghost, taking an
adjacent pellet) are carried over from Part 2 -- you already built this
logic once, so it is filled in for you. What is new, and what you TODO
here, is the internal state itself and the rule that uses it.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from pacman.maze import DIRECTION_NAMES, MazeModel

AGENT_NAME = "model_based"


@dataclass(frozen=True)
class Percept:
    player: tuple[int, int]
    current_direction: tuple[int, int]
    pellets: frozenset[tuple[int, int]]
    power_pellets: frozenset[tuple[int, int]]
    released_ghosts: tuple[tuple[int, int], ...]
    legal_actions: tuple[tuple[int, int], ...]
    frightened_time_remaining: float

    @property
    def frightened(self) -> bool:
        return self.frightened_time_remaining > 0.0


class ModelBasedAgent:
    percept_class = Percept

    def __init__(self, maze: MazeModel):
        self.maze = maze
        self.last_reason = "Waiting for first percept."

        self.visit_counts: dict[tuple[int, int], int] = {}
        self.position_history: deque[tuple[int, int]] = deque(maxlen=4)
        self.revisit_decisions = 0
        self.backtrack_decisions = 0


    def update_internal_state(self, percept: Percept) -> None:
        """Fold this percept into memory. Called once per turn, before any
        action is chosen. Record that percept.player has been visited
        (increment its count in visit_counts) and append it to
        position_history."""

        self.visit_counts[percept.player] = self.visit_counts.get(percept.player, 0) + 1
        self.position_history.append(percept.player)
        return

    def choose_action(self, percept: Percept) -> tuple[int, int]:
        if not percept.legal_actions:
            self.last_reason = "No legal move."
            return (0, 0)

        self.update_internal_state(percept)

        ghosts = set(percept.released_ghosts)
        landing = {
            action: self.maze.step(percept.player, action)
            for action in percept.legal_actions
        }

        # Rule 1: never step onto a dangerous ghost if another option exists.
        safe = [
            action
            for action, tile in landing.items()
            if percept.frightened or tile not in ghosts
        ]
        if not safe:
            safe = list(percept.legal_actions)
            rule = "cornered"
        else:
            rule = "safe"

        # Rule 2: eat an adjacent frightened ghost.
        if percept.frightened:
            for action in safe:
                if landing[action] in ghosts:
                    return self._commit(action, "eat frightened ghost")

        # Rule 3: step onto an adjacent power pellet, then an adjacent pellet.
        for action in safe:
            if landing[action] in percept.power_pellets:
                return self._commit(action, "adjacent power pellet")
        for action in safe:
            if landing[action] in percept.pellets:
                return self._commit(action, "adjacent pellet")

        # Rules 4 and 5: don't reverse into the tile from two turns ago
        # unless it's the only safe option, then pick the least-visited tile.
        backtrack_tile = (
            self.position_history[-2]
            if len(self.position_history) >= 2
            else None
        )

        non_backtrack = [
            action
            for action in safe
            if landing[action] != backtrack_tile
        ]

        if not non_backtrack:
            non_backtrack = safe

        best_action = min(
            non_backtrack,
            key=lambda action: self.visit_counts.get(landing[action], 0),
        )
        chosen_tile = landing[best_action]

        if self.visit_counts.get(chosen_tile, 0) > 0:
            self.revisit_decisions += 1

        if chosen_tile == backtrack_tile:
            self.backtrack_decisions += 1

        return self._commit(best_action, "Rules 4 and 5")

    def _commit(self, action: tuple[int, int], rule: str) -> tuple[int, int]:
        self.last_reason = f"{DIRECTION_NAMES[action]} | rule: {rule}"
        return action
