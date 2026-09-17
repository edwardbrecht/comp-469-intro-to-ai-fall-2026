# Chapter 2 Write-Up

Name:
Date:

Keep this to three or four pages. Answer from the code in front of you | 
not from the textbook in general. A correct answer that could have been
written without ever opening this project will not get full marks.

---

## 1. PEAS description (5 points)

Describe this task environment using AIMA Section 2.3.1. This is one
description for the whole environment -- all six of your agents share it.

**Performance measure.**
> What is the agent actually judged on? Name the function and the file.
> List every term in it |  including the ones that cost points.

**Environment.**
> The maze |  the ghosts |  the pellets |  the clock. Mention anything that
> changes while an agent is deciding.

**Actuators.**
> What can an agent actually do? Be precise about how many actions it
> takes per turn and what happens if it picks an illegal one.

**Sensors.**
> What can an agent perceive? Name the mechanism that decides this |  not
> just the list of possible fields -- and say why different parts of this
> project declare different subsets of them.

---

## 2. Environment properties (6 points)

One row per dimension from AIMA Figure 2.6. Justify each from something
specific in the code |  and name it.

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
particular implementation. Pick one |  and make the case for the answer you
did *not* put in the table.
Some agents only have access to knowing the result of taking an action ie what is right next to them. In those cases the environment is only partially observable.

---

## 3. Six agents |  six figures (6 points)

One row per part. Name the AIMA Section 2.4 figure it matches |  and the
ONE concrete thing that part adds over the part before it (not a
restatement of what it does overall -- the specific delta).

| Part | Figure | What it adds over the previous part |
|---|---|---|
| 1. Table-driven | | (nothing to compare against -- say instead what makes it infeasible) |
| 2. Simple reflex | | |
| 3. Model-based reflex | | |
| 4. Goal-based | | |
| 5. Utility-based | | |
| 6. Learning | | |

**Two follow-ups:**

> For Part 2/3: you had a choice between `ghosts` and `released_ghosts`
> in your percepts. Say which you took and what the other one would have
> cost you.

> For Part 6: map the four boxes of AIMA Figure 2.15 (performance
> element |  critic |  learning element |  problem generator) onto specific
> names in `learning_agent.py`.

---

## 4. Performance measure vs. utility function (5 points)

These are two different things |  and this codebase keeps them in two
different places on purpose -- one in `pacman/rules.py` |  imposed by the
environment designer |  and one inside `utility_based_agent.py` |  chosen by
you.

**Where does each one live?**
> File and function/class for both.

**Name one place they disagree.**
> Find something your utility function rewards (or punishes) that the
> performance measure does not |  or the reverse. Explain why that gap
> exists and whether it is a flaw.

**Why does AIMA insist on the distinction?**
> Answer in your own words |  in three or four sentences.

---

## 5. Rational is not the same as successful (4 points)

Run some `hard` trials with your Part 5 (or Part 6) agent and find a seed
where it lost.

**Seed:**

**What happened.**
> Replay it with `python tools/play.py --difficulty hard --agent
> utility_based --seed N` and describe the sequence.

**Why the losing decision was still rational.**
> AIMA Section 2.2.2 separates rationality from omniscience. Use it. What
> did the agent not know |  and could it have known it given the percept it
> was handed and the "no search" rule every part in this project follows?

**What would have to change for that decision to be irrational?**

---

## 6. Trial results across all six parts (4 points)

Paste the summary table from `results/summary.csv` (both difficulties) | 
and a row for the trained `learning` agent from
`results/learned_weights.json`.

| agent | difficulty | trials | win_rate | caught_rate | mean_score | mean_decisions | mean_backtracks | mean_performance | stdev_performance |
|---|---|---|---|---|---|---|---|---|---|
| table_driven | normal | 30 | 0.0 | 1.0 | 77.0 | 12.23 | 1.1 | -927.65 | 20.0 |
| simple_reflex | normal | 30 | 0.0 | 1.0 | 898.0 | 116.3 | 7.0 | -139.26 | 347.71 |
| model_based | normal | 30 | 0.0 | 1.0 | 602.67 | 84.3 | 1.5 | -417.19 | 89.97 |
| goal_based | normal | 30 | 0.133 | 0.867 | 712.33 | 98.47 | 10.83 | 70.97 | 1210.01 |
| utility_based | normal | 30 | 0.8 | 0.2 | 972.33 | 88.77 | 7.27 | 2340.05 | 1416.15 |
| learning | normal | 30 | 0.0 | 1.0 | 338.33 | 44.13 | 8.63 | -687.76 | 217.81 | 
| greedy | normal | 30 | 0.6 | 0.4 | 1091.0 | 79.9 | 6.93 | 1861.15 | 1819.58 |
| random | normal | 30 | 0.0 | 1.0 | 190.67 | 33.2 | 11.87 | -839.71 | 129.68 |


| agent | difficulty | trials | win_rate | caught_rate | mean_score | mean_decisions | mean_backtracks | mean_performance | stdev_performance |
|---|---|---|---|---|---|---|---|---|---|
| table_driven | hard | 30 | 0.0 | 1.0 | 70.0 | 9.23 | 1.0 | -933.85 | 0.09 |
| simple_reflex | hard | 30 | 0.0 | 1.0 | 143.33 | 14.97 | 0.2 | -860.06 | 128.63 |
| model_based | hard | 30 | 0.0 | 1.0 | 578.0 | 59.0 | 0.43 | -434.67 | 54.74 |
| goal_based | hard | 30 | 0.233 | 0.767 | 682.0 | 71.43 | 6.9 | 353.91 | 1494.56 |
| utility_based | hard | 30 | 0.067 | 0.933 | 579.33 | 63.23 | 5.17 | -243.65 | 871.84 |
| learning | hard | 30 | 0.0 | 1.0 | 650.0 | 55.83 | 8.5 | -378.17 | 309.44 |
| greedy | hard | 30 | 0.033 | 0.967 | 161.67 | 14.9 | 0.4 | -742.11 | 758.66 |
| random | hard | 30 | 0.0 | 1.0 | 131.33 | 21.9 | 6.2 | -885.45 | 8.87 |


**Interpretation |  five to eight sentences.**
> Do not restate the numbers. Trace the progression: what does each part
> buy over the one before it |  in terms of the agent structures involved
> rather than raw numbers? `mean_decisions` and `mean_backtracks` are the
> interesting columns for Parts 2 vs. 3 (memory); win rate and mean
> performance are the interesting columns for Parts 4 vs. 5 (goals vs.
> utility); the before/after numbers in `learned_weights.json` are the
> interesting ones for Part 6. If any part did NOT improve on the one
> before it in your results |  say so and explain why -- that is a real
> finding |  not something to hide.

---

## Optional

Anything you tried that did not work |  or a weight you tuned and then
reverted. Not graded |  but useful to me.
