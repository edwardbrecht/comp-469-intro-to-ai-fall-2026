# Chapter 2 Write-Up

Name:
Date:

Keep this to three or four pages. Answer from the code in front of you,
not from the textbook in general. A correct answer that could have been
written without ever opening this project will not get full marks.

---

## 1. PEAS description (5 points)

Describe this task environment using AIMA Section 2.3.1. This is one
description for the whole environment -- all six of your agents share it.

**Performance measure.**
> What is the agent actually judged on? Name the function and the file.
> List every term in it, including the ones that cost points.

Pac-Man earns points for eating regular pellets, power pellets, and frightened ghosts, and gets a big bonus for clearing the maze in full. It loses points if a ghost catches it, and for taking too many turns or immediately turning back the way it came.

**Environment.**
> The maze, the ghosts, the pellets, the clock. Mention anything that
> changes while an agent is deciding.

The environment is the Pac-Man maze, which includes walls, pellets, power pellets, Pac-Man, ghosts, and a timer. While Pac-Man plays, things that change are that pellets disappear when eaten, power pellets make ghosts frightened for a short time, and ghosts move around the maze. On hard difficulty, ghosts will move faster.

**Actuators.**
> What can an agent actually do? Be precise about how many actions it
> takes per turn and what happens if it picks an illegal one.

Pac-Man during each turn can choose to move left, right, up, or down. If the move is legal, Pac-Man moves one tile in that direction. If the move would hit a wall, Pac-Man stays where he is, but the turn still counts.

**Sensors.**
> What can an agent perceive? Name the mechanism that decides this, not
> just the list of possible fields -- and say why different parts of this
> project declare different subsets of them.

Depending on the agent, it can be told its own location, its current direction, where pellets and power pellets are, where ghosts are, what moves are legal, and whether ghosts are frightened. Different agents get different information because each part of the assignment is testing a different type of AI agent.

---

## 2. Environment properties (6 points)

One row per dimension from AIMA Figure 2.6. Justify each from something
specific in the code, and name it.

| Property | This environment is... | Why (cite the code) |
|---|---|---|
| Fully or partially observable | Fully | maze.distance() searches the entire environment |
| Single-agent or multi-agent | Multi | Ghosts act as antagonists |
| Deterministic or nondeterministic |  Deterministic | Ghosts are the only other animated entitied, and rules._choose_ghost_action() is not random |
| Episodic or sequential | Episodic | choose_action() functions for all agents are based only on the immediate situation determined by it's percepts |
| Static or dynamic | Static | choose_action() is complete within a single frame for all agents |
| Discrete or continuous | Discrete | maze.LEVEL is constant and a finite size. Additionally, rules._run_tick() provides a frame within which the player and ghosts act |
| Known or unknown | Known | rules.py dictates only a few simple static interactions; agent knows to avoid ghosts unless they are frightened and to go after pellets |

**Follow-up.** Two of these have an argument on both sides in this
particular implementation. Pick one, and make the case for the answer you
did *not* put in the table.
Some agents only have access to knowing the result of taking an action ie what is right next to them. In those cases the environment is only partially observable.

---

## 3. Six agents, six figures (6 points)

One row per part. Name the AIMA Section 2.4 figure it matches, and the
ONE concrete thing that part adds over the part before it (not a
restatement of what it does overall -- the specific delta).

| Part | Figure | What it adds over the previous part |
|---|---|---|
| 1. Table-driven | 2.7 | A table-driven agent needs a saved move for every possible history of the game. Since there are too many possible histories, the table would become too large to store and therefore impractical to use |
| 2. Simple reflex | 2.10 | Replaces the giant table with simple rules based only on what it sees right now |
| 3. Model-based reflex | 2.11 / 2.12 | Adds memory of visited tiles and recent movement |
| 4. Goal-based | 2.13 | Adds a goal, to get food or move away from danger |
| 5. Utility-based | 2.14 | Gives each possible move a score and picks the best one |
| 6. Learning | 2.15 | Adjusts its utility weights between games based on performance |

**Two follow-ups:**

> For Part 2/3: you had a choice between `ghosts` and `released_ghosts`
> in your percepts. Say which you took and what the other one would have
> cost you.

For Part 2/3, we used `released_ghosts`, which are the ghosts that have left the ghost house and can move around the maze. If we used `ghosts` instead, Pac-Man would also react to ghosts still stuck in the ghost house, which could make it avoid danger that is not actually a threat yet.

> For Part 6: map the four boxes of AIMA Figure 2.15 (performance
> element, critic, learning element, problem generator) onto specific
> names in `learning_agent.py`.

Performance element: `self.performance_element`. It is the Part 5 UtilityBasedAgent that chooses moves.
Learning element: `learn()`. It keeps new weights if they performed better, or switches back to the old best weights if they performed worse.
Critic: `learn(performance)`. This score comes from the environment after each game.
Problem generator: `propose_new_weights()`. It makes small random changes to the weights to try in the next game.

---

## 4. Performance measure vs. utility function (5 points)

These are two different things, and this codebase keeps them in two
different places on purpose -- one in `pacman/rules.py`, imposed by the
environment designer, and one inside `utility_based_agent.py`, chosen by
you.

**Where does each one live?**
> File and function/class for both.

The performance measure is Simulation.performance() in pacman/rules.py.
It scores the full game after it ends. It starts with the game score
(10 per pellet, 50 per power pellet, 200 per ghost eaten), adds a 2000
bonus for a win, subtracts 1000 if Pac-Man is caught, subtracts 0.20 per
decision, and subtracts 2.0 per immediate backtrack.

The utility function is in utility_based_agent.py. The preferences are
stored in the UtilityWeights dataclass. UtilityBasedAgent.evaluate_action()
uses those weights to score each legal move. Then choose_action() picks the
move with the highest score. It judges the tile Pac-Man would move to, not the
full game.

**Name one place they disagree.**
> Find something your utility function rewards (or punishes) that the
> performance measure does not, or the reverse. Explain why that gap
> exists and whether it is a flaw.

One difference is how they treat frightened ghosts. The performance measure
gives 200 points for eating one, but our ghost_catch_frightened and
ghost_close_frightened weights are both 0. This means the utility function
does not try to chase ghosts while Pac-Man is powered up. The power_pellet
weight is also 0, even though a power pellet is worth 50 points.

We chose those values based on our tests. Frightened ghosts run away at full
speed, and the effect lasts 2 seconds (POWER_DURATION_MS). Pac-Man could not
catch them most of the time. Chasing also pulled Pac-Man away from food and
put it near other ghosts. With a chase weight of -0.1, the win rate over 200
practice games dropped from about 80% to about 20%. A power pellet bonus of
0.5 made the agent eat power pellets too early, even when no ghost was nearby.
This dropped the win rate to about 10%. Since a win is worth 2000 points and
getting caught costs 1000, giving up some ghost points was worth it if the
agent won more games.

We do not think this is a flaw. On normal difficulty, the agent ate 21 ghosts
across 30 games, while the ghost-blind greedy baseline ate 46. However, our
agent won 80% of its games compared with 60% for greedy, and its mean
performance was 2340 instead of 1861. The utility function does not need to
copy every part of the performance measure. It needs to choose moves that lead
to a better result. The downside is that it may pass up a ghost that it
could have eaten safely.

**Why does AIMA insist on the distinction?**
> Answer in your own words, in three or four sentences.

The performance measure is how the designer judges the final result. The
utility function is how the agent estimates which move is best. AIMA keeps
them separate because the agent's estimate may not match what the designer
wants. This lets us check whether the agent's choices lead to a better score
instead of letting the agent define success for itself.

---

## 5. Rational is not the same as successful (4 points)

Run some `hard` trials with your Part 5 (or Part 6) agent and find a seed
where it lost.

**Seed:** 13 on hard, with utility_based. The same seed on normal is a win.

**What happened.**
> Replay it with `python tools/play.py --difficulty hard --agent
> utility_based --seed 13` and describe the sequence.

About 12 seconds into the game, the agent had almost cleared the maze. After
eating the pellet at (8,15), only two pellets were left on the far-left side.
The agent turned around and followed the bottom corridor because it was the
shortest route. One ghost entered the corridor from the left while another
came down the right side behind Pac-Man. At (8,11), moving left would have
gone onto the first ghost and moving right would have sent Pac-Man back toward
the second one. Going up had the best utility score, -11.6, so the agent chose
it. On hard difficulty, ghosts move every 110 ms while Pac-Man moves every 135
ms. The first ghost moved twice and caught Pac-Man at (7,11), with
two pellets still left. The final score was 870 and the performance was
-165.2. On normal difficulty, the same seed ended in a win with a performance
of 3253.8.

**Why the losing decision was still rational.**
> AIMA Section 2.2.2 separates rationality from omniscience. Use it. What
> did the agent not know, and could it have known it given the percept it
> was handed and the "no search" rule every part in this project follows?

Section 2.2.2 explains that a rational agent picks the action it expects to
work best based on what it has seen and what it knows. This does not mean it
knows what will happen. Going up had the highest utility. The other two choices
were worse or would cause Pac-Man to get caught. The agent did not know the
ghost speed because its percept included the positions in released_ghosts but
not ghost_period_ms. It also could not know each ghost's next move because the
ghosts chase 80% of the time and move at random the rest of the time. The agent
also did not know that (7,11) led toward a dead end. It would have needed to
look several moves ahead, but the project does not allow search. Based on the
information it had, going up was a rational choice even though it lost.

**What would have to change for that decision to be irrational?**

The decision would be irrational if the percept included the ghost speed or
difficulty and the agent treated a ghost two steps away as safe. It would be
ignoring information it had. It would also be irrational if the agent kept
losing hard games in the same way but never changed its weights. A Part 6
agent trained on hard difficulty could learn to make ghost_two_steps negative.
The choice would also be irrational if another legal move had a higher utility
score and the agent ignored it, or if it moved left onto the ghost with a
utility of -5009.6.

---

## 6. Trial results across all six parts (4 points)

Paste the summary table from `results/summary.csv` (both difficulties),
and a row for the trained `learning` agent from
`results/learned_weights.json`.

| agent | difficulty | trials | win_rate | caught_rate | mean_score | mean_decisions | mean_backtracks | mean_performance | stdev_performance |
|---|---|---|---|---|---|---|---|---|---|
| table_driven | normal | 30 | 0.0 | 1.0 | 77.0 | 12.23 | 1.1 | -927.65 | 20.0 |
| simple_reflex | normal | 30 | 0.0 | 1.0 | 898.0 | 116.3 | 7.0 | -139.26 | 347.71 |
| model_based | normal | 30 | 0.0 | 1.0 | 602.67 | 84.3 | 1.5 | -417.19 | 89.97 |
| goal_based | normal | 30 | 0.133 | 0.867 | 712.33 | 98.47 | 10.83 | 70.97 | 1210.01 |
| utility_based | normal | 30 | 0.8 | 0.2 | 972.33 | 88.77 | 7.27 | 2340.05 | 1416.15 |
| learning | normal | 30 | 0.167 | 0.833 | 593.33 | 73.73 | 7.1 | 64.39 | 1431.18 |
| greedy | normal | 30 | 0.6 | 0.4 | 1091.0 | 79.9 | 6.93 | 1861.15 | 1819.58 |
| random | normal | 30 | 0.0 | 1.0 | 190.67 | 33.2 | 11.87 | -839.71 | 129.68 |

| agent | difficulty | trials | win_rate | caught_rate | mean_score | mean_decisions | mean_backtracks | mean_performance | stdev_performance |
|---|---|---|---|---|---|---|---|---|---|
| table_driven | hard | 30 | 0.0 | 1.0 | 70.0 | 9.23 | 1.0 | -933.85 | 0.09 |
| simple_reflex | hard | 30 | 0.0 | 1.0 | 143.33 | 14.97 | 0.2 | -860.06 | 128.63 |
| model_based | hard | 30 | 0.0 | 1.0 | 578.0 | 59.0 | 0.43 | -434.67 | 54.74 |
| goal_based | hard | 30 | 0.233 | 0.767 | 682.0 | 71.43 | 6.9 | 353.91 | 1494.56 |
| utility_based | hard | 30 | 0.067 | 0.933 | 579.33 | 63.23 | 5.17 | -243.65 | 871.84 |
| learning | hard | 30 | 0.0 | 1.0 | 638.33 | 50.87 | 3.23 | -378.31 | 232.29 |
| greedy | hard | 30 | 0.033 | 0.967 | 161.67 | 14.9 | 0.4 | -742.11 | 758.66 |
| random | hard | 30 | 0.0 | 1.0 | 131.33 | 21.9 | 6.2 | -885.45 | 8.87 |

Trained `learning` agent, from `results/learned_weights.json` (mean performance over 20 held-out seeds, 9001-9020; 80 training episodes):

| agent | difficulty | mean_performance before training | mean_performance after training | change |
|---|---|---|---|---|
| learning | normal | -68.31 | 393.87 | +462.18 |

**Interpretation, five to eight sentences.**
> Do not restate the numbers. Trace the progression: what does each part
> buy over the one before it, in terms of the agent structures involved
> rather than raw numbers? `mean_decisions` and `mean_backtracks` are the
> interesting columns for Parts 2 vs. 3 (memory); win rate and mean
> performance are the interesting columns for Parts 4 vs. 5 (goals vs.
> utility); the before/after numbers in `learned_weights.json` are the
> interesting ones for Part 6. If any part did NOT improve on the one
> before it in your results, say so and explain why -- that is a real
> finding, not something to hide.

Part 1 does not get far because its table only knows its heading and legal
moves, so it cannot see food or ghosts. Part 2 adds rules for nearby tiles,
which helps it survive longer, but it has no memory and often moves back and
forth after eating the nearby food. Part 3 adds memory, and on normal it makes
fewer decisions and backtracks than Part 2, but its performance gets worse
because it visits new tiles while only avoiding ghosts that are one step away.
Part 4 is the first agent to win games because it runs when a ghost gets within
three steps, but switching between fleeing and eating causes many backtracks.
Part 5 scores food, danger, and memory together instead of using one goal at a
time, which leads to a large improvement on normal and lets it beat the greedy
baseline. Part 4 does better than Part 5 on hard because the Part 5 weights
only respond to a ghost one step away, while Part 4 starts running sooner.
Part 6 starts with weak weights and uses hill climbing, which improves its
performance on the held-out games. It still falls behind the hand-tuned Part 5
agent because each change is tested on only four games, so the training does
not find the stronger weights found through longer testing.

---

## Optional

Anything you tried that did not work, or a weight you tuned and then
reverted. Not graded, but useful to me.
