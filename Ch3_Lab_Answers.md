# Lab 3
## Problem 1: Formulating a Search Problem
### A) Minimal State Representation
- position_x (0,7)
- position_y (0,4)
- orientation (North, West, South, East)
- can_move_forward (Yes, No)
- at_specimen (Yes, No)
- specimens_photographed (List(Position)[0:6])

We leave out the location of the launch cell because this is implicit in the first state and can be recalled when the task is complete.

### B) Number of States
$$ 8 * 5 * 4 * 2 * 2 * 7 = 4,480 $$
All variables listed above are utilized in this system and included in this figure.

### C) Goal Test
GOAL_CONDITION: specimens_photographed.LENGTH == 6

RESULT((0,0,North,Yes,No,NULL), TurnLeft) = (0,0,West,No,No,NULL)

### D) Tidal Channel
In the situation of Column 5 being a tidal channel which may only be passed if less than 12 actions have been taken so far the following must be added to the state:
- num_actions_taken (0, 12)
- channel_crossed (Yes, No)
- can_cross_back (Yes, No)

A single Boolean such as channelOpen is not sufficient for planning; the robot will not know how much time it has to cross or return from across the channel without the above.

Updated number of states:

$$ 8 * 5 * 4 * 2 * 2 * 7 * 13 * 2 * 2 = 232,960 $$

## Problem 2: State-Space Graph vs. Search Tree
### A) Search Tree
d = 0: S

d = 1: S, S-A, S-B

d = 2: S, S-A, S-A-B, S-A-C, S-B, S-B-A, S-B-C (7 nodes)

d = 3: S, S-A, S-A-B, S-A-B-A, S-A-B-C, S-A-C, S-A-C-G, S-B, S-B-A, S-B-A-B, S-B-A-C, S-B-C, S-B-C-G (13 nodes)

### B) Finite vs Infinite
The search tree is infinite because of the cycle created by the edges between A and B.

### C) Cycle Checking
With cycle checking up to the parent node, at d = 3 there are now 11 nodes. The tree now is finite and the complete search graph is represented at d = 3 with 11 nodes.

### D) Redundancy
A redundant path that still appears in more than one node even with cycle checking is C-G; C can be arrived at from both A and B. BEST-FIRST-SEARCH is one method that handles redundancy.

## Problem 3: Tracing BFS, DFS, and UCS
### A) BFS
- Expansion Order: S, A, C, E, B, D, G
- Returned Path: S-C-G
- Path Cost: 8
### B) DFS
- Pop Order: S, A, B, A(x), B, D, G
- Returned Path: S-A-B-D-G
- Path Cost: 13
### C) UCS
| Pop # | Node popped (g) | Frontier after the pop | Reached-table replacement |
| ----| ------ | -------- | ----- |
| 1 | S(0) | A(1), C(3), E(4) | none |
| 2 | A(1) | B(1+1=2), C(3), E(4) | A |
| 3 | B(2) | A(2+1=3), D(2+7=9), C(3), E(4)  | A, B |
| 4 | C(3) | D(9), D(3+1=4), G(3+11=14), E(4) | A, B, C |
| 5 | E(4) | D(9), D(4), G(14), F(4+1=5) | A, B, C, E |
| 6 | D(4) | G(14), F(5), G(4+4=8)  | A, B, C, E, D |
| 7 | F(5) | G(14, G(8), G(5+6 = 11)) | A, B, C, E, D, F |
| 8 | G(8) | N/A | A, B, C, E, D, F |
| 9 | N/A | N/A | N/A |

- Returned Path: S-C-D-G
- Path Cost: 8
- Returned on Pop #: 8

### D) UCS & Generation
If UCS performed the goal test upon node generation it would return S-C-G with cost 14 on pop #4.
### E) Buggy Code
The described buggy code would return the following path: S-C-G. This is not the same path as in b). This path is returned because using append() and popleft() is a FIFO structure and acts as a BFS so the path that generates / reaches G in the fewest number of steps will be returned.
## Problem 4: Depth-Limited and Iterative Deepening Search
### A)
| l | Nodes popped, in order | Returns |
| --- | --- | --- |
| 0 | A | cutoff |
| 1 | A, B, C, D | cutoff |
| 2 | A, B, E, F, C, H, D, I, J, K | cutoff |
| 3 | A, B, E, L, F, C, H, M, N | A-C-H-N |

### B) No Goal
With no goal state, l = 3 would return cutoff. Iterative deepening would stop at l = 4 and would return failure as no new nodes were expanded and no goal was reached.

### C) IDS vs BFS

For b = 3 and d = 4:

$$ N(IDS) = (4)3 + (3)3^2 + (2)3^3 + 3^4 = 174 $$
$$ N(BFS) = 3 + 3^2 + 3^3 + 3^4 = 120 $$
$$ Overhead = \frac{(174 - 120)}{120} * 100 = 45\%  $$

The difference in overhead has to do with a smaller tree and depth making each repetition more costly from a percentage standpoint; broader trees and a deeper depth lead a smaller percentage difference.

