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
