"""Part 5 - Utility-based agent (AIMA 4e Figure 2.14).

This agent keeps everything Part 3 (model-based reflex) has -- internal
state built from the percept sequence, given to you below unchanged --
and replaces its condition-action RULES with a single UTILITY FUNCTION:
every legal action is scored on one numeric scale that blends several
competing preferences (closer food is good, closer danger is bad,
repetition is mildly bad, and so on), and the agent takes whichever
action scores highest. That is the qualitative jump from Part 4: a
goal-based agent asks "does this satisfy the goal, or get me closer to
it"; a utility-based agent asks "how good is this, all things considered"
and can trade one desideratum off against another inside a single number.

Do NOT implement your own search (BFS, DFS, A*, ...). ``self.maze.distance``
is provided precisely so you never have to.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from pacman.maze import DIRECTION_NAMES, MazeModel

AGENT_NAME = "utility_based"

#: Ghost distance to report when no ghost is released (or none is
#: reachable), so "no ghosts" never reads as "ghost is right here".
NO_GHOST_DISTANCE = 10_000

#: The contribution keys that are weighted and sum to the total utility.
#: The rest of the contributions dict is raw evidence for reporting.
WEIGHTED_TERMS = (
    "food_distance",
    "regular_pellet",
    "power_pellet",
    "ghost",
    "continuation",
    "revisit",
    "backtrack",
)


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


@dataclass(frozen=True)
class UtilityWeights:
    """Named preferences. This is the agent's utility function, not the
    environment's performance measure (AIMA 4e Section 2.2 keeps those
    separate on purpose; so does this codebase -- see pacman/rules.py)."""

    # Tuned with headless trials on seeds 100-299 and checked on held-out
    # seeds. The main lesson: ghosts move exactly as fast as Pac-Man, so a
    # ghost chasing from behind can't catch an agent that keeps moving.
    # What loses games is flinching -- turning away from a ghost that isn't
    # an immediate threat, which usually means reversing into another one.
    # Several weights are 0.0 on purpose; each comment says why.

    # Food. Walking toward the nearest pellet is the whole plan. Landing
    # bonuses are 0.0: food_distance already scores a pellet tile as 0 steps,
    # and a power-pellet bonus made the agent spend power pellets in the
    # opening, when no ghost was near, instead of saving them.
    food_distance: float = -1.0
    regular_pellet: float = 0.0
    power_pellet: float = 0.0

    # Frightened ghosts run away at full speed and fright lasts only 2
    # seconds, so chasing (or detouring to eat) one mostly led the agent
    # toward ghosts right as they turned dangerous again.
    ghost_catch_frightened: float = 0.0
    ghost_close_frightened: float = 0.0

    # Dangerous ghosts, by maze distance from the landing tile. Landing on
    # one is fatal, and a ghost one step away can step onto you this turn.
    # Two or three steps away is not yet a threat; penalising it made the
    # agent turn back into pincers.
    ghost_collision: float = -5000.0
    ghost_one_step: float = -800.0
    ghost_two_steps: float = 0.0
    ghost_three_steps: float = 0.0

    # Reward per step of space from the nearest ghost beyond three steps,
    # counted up to ghost_safe_distance_cap steps. Off: any pull toward open
    # space competed with eating and made the agent wander.
    ghost_safe_distance: float = 0.0
    ghost_safe_distance_cap: float = 0.0

    # Memory (Part 3's internal state). Reversing is the costliest mistake
    # (it walks into whatever was following), then re-treading old tiles.
    continuation: float = 0.0
    revisit_per_visit: float = -0.8
    backtrack: float = -1.5


class UtilityBasedAgent:
    percept_class = Percept

    def __init__(self, maze: MazeModel):
        self.maze = maze
        self.weights = UtilityWeights()
        self.last_reason = "Waiting for first percept."

        # Internal state, carried over unchanged from Part 3.
        self.visit_counts: dict[tuple[int, int], int] = {}
        self.position_history: deque[tuple[int, int]] = deque(maxlen=4)
        self.revisit_decisions = 0
        self.backtrack_decisions = 0

    def update_internal_state(self, percept: Percept) -> None:
        """Same as Part 3: record that percept.player has been visited
        and append it to position_history. Provided -- you already built
        this once."""
        position = percept.player
        self.visit_counts[position] = self.visit_counts.get(position, 0) + 1
        self.position_history.append(position)

    def evaluate_action(
        self,
        percept: Percept,
        action: tuple[int, int],
    ) -> tuple[float, dict[str, float]]:
        """Score a single legal action.

        Returns ``(total_utility, contributions)`` where ``contributions``
        maps a term name to the signed number it added. Splitting scoring
        out from choosing is what lets you explain a decision instead of
        just making one.

        ``contributions`` must contain at least these keys:

            food_distance   revisit          food_distance_steps
            regular_pellet  backtrack        ghost_distance_steps
            power_pellet    continuation     revisit_count
            ghost

        The first two columns are weighted values that sum into the
        total. The third column is raw evidence, not weighted, used for
        reporting.

        Behaviour to implement:
          - Raise ValueError if ``action`` is not in ``percept.legal_actions``.
          - Work out the landing tile with ``self.maze.step``.
          - Pull food and ghost distances from ``self.maze.distance``
            (pass an empty/absent ghost set as a very large number, e.g.
            10_000, so "no ghosts released" never reads as "ghost is
            here").
          - When frightened, closer ghosts should be more attractive
            (negative distance coefficient), and landing on one is worth
            a lot.
          - When not frightened, landing on a ghost is disastrous, and
            ghosts one, two, or three steps away are progressively less
            alarming. Beyond that, more space is mildly good; cap it so
            the agent does not just run to the far corner and idle.
          - Penalise the landing tile in proportion to
            ``self.visit_counts``.
          - Penalise the landing tile if it equals
            ``self.position_history[-2]`` (the tile from two turns ago;
            only meaningful once history has at least 2 entries).
        """
        if action not in percept.legal_actions:
            raise ValueError(f"{action} is not a legal action here.")

        w = self.weights
        landing = self.maze.step(percept.player, action)

        food = percept.pellets | percept.power_pellets
        food_steps = self.maze.distance(landing, food) if food else 0

        ghosts = frozenset(percept.released_ghosts)
        ghost_steps = self.maze.distance(landing, ghosts) if ghosts else NO_GHOST_DISTANCE

        if ghost_steps >= NO_GHOST_DISTANCE:
            ghost = 0.0
        elif percept.frightened:
            if ghost_steps == 0:
                ghost = w.ghost_catch_frightened
            else:
                ghost = w.ghost_close_frightened * ghost_steps
        elif ghost_steps == 0:
            ghost = w.ghost_collision
        elif ghost_steps == 1:
            ghost = w.ghost_one_step
        elif ghost_steps == 2:
            ghost = w.ghost_two_steps
        elif ghost_steps == 3:
            ghost = w.ghost_three_steps
        else:
            ghost = w.ghost_safe_distance * min(ghost_steps, w.ghost_safe_distance_cap)

        revisit_count = self.visit_counts.get(landing, 0)
        just_left = (
            self.position_history[-2] if len(self.position_history) >= 2 else None
        )

        contributions = {
            "food_distance": w.food_distance * food_steps,
            "regular_pellet": w.regular_pellet if landing in percept.pellets else 0.0,
            "power_pellet": w.power_pellet if landing in percept.power_pellets else 0.0,
            "ghost": float(ghost),
            "continuation": w.continuation if action == percept.current_direction else 0.0,
            "revisit": w.revisit_per_visit * revisit_count,
            "backtrack": w.backtrack if landing == just_left else 0.0,
            "food_distance_steps": food_steps,
            "ghost_distance_steps": ghost_steps,
            "revisit_count": revisit_count,
        }
        total = float(sum(contributions[k] for k in WEIGHTED_TERMS))
        return total, contributions

    def choose_action(self, percept: Percept) -> tuple[int, int]:
        """Replace the starter policy below.

        Requirements:
          - If there are no legal actions, set ``last_reason`` to a string
            containing "No legal" and return ``(0, 0)``.
          - Otherwise call ``update_internal_state`` exactly once, score
            every legal action with ``evaluate_action``, and return the
            best one. Iterate in ``percept.legal_actions`` order and keep
            strictly-greater comparison so ties break the same way every
            time.
          - The returned action must always be legal.
          - Set ``self.last_reason`` to one short line containing the
            direction name and the tokens "U=", "food=", "ghost=", and
            "memory=", where memory is the sum of the revisit and
            backtrack contributions for the chosen action. Example:

                LEFT | U=-31.0 | food=3 | ghost=6 | memory=-2.0

            That line is drawn live in the game window -- the fastest way
            to debug a utility function is to watch a percept become a
            number and the number become a move.
        """
        if not percept.legal_actions:
            self.last_reason = "No legal actions available."
            return (0, 0)

        self.update_internal_state(percept)

        best_action = None
        best_utility = float("-inf")
        best_terms: dict[str, float] = {}
        for action in percept.legal_actions:
            utility, terms = self.evaluate_action(percept, action)
            if best_action is None or utility > best_utility:
                best_action = action
                best_utility = utility
                best_terms = terms

        if best_terms.get("revisit_count", 0) > 0:
            self.revisit_decisions += 1
        if best_terms.get("backtrack", 0.0) != 0.0:
            self.backtrack_decisions += 1

        memory = best_terms.get("revisit", 0.0) + best_terms.get("backtrack", 0.0)
        self.last_reason = (
            f"{DIRECTION_NAMES[best_action]} | U={best_utility:.1f} | "
            f"food={best_terms.get('food_distance_steps')} | "
            f"ghost={best_terms.get('ghost_distance_steps')} | memory={memory:.1f}"
        )
        return best_action
