# 2MMR10-Palletization

For all your palletization needs.

Run with `python palletization.py [options] [dataset]`

General `options`:
- `sort:xxx`: sorts the items by metric `xxx` in {`none`, `rand`, `volume`, `side`}. Other than none none and random random, this sorts in decreasing order. This is relevant for greedy and for `level_03`.
- `no_dots`: visualization will not display extreme points.
- `no_vis`: visualization will not be created.
- `histo`: only creates histograms of the data, does not run algorithms.
- `validate`: checks which properties are satisfied by an input solution.

Greedy `options`:
- `greedy_01`, `greedy_02`, `greedy_03`: specifies to use greedy algorithm. First has no look-ahead, second has one-step look-ahead, third has one-step look-ahead with weighted counting.
- `onequeue`: when the greedy algorithm fails to place a box, it will be tried after all other boxes have been tried (put at end of queue) (default).
- `twoqueue`: when the greedy algorithm fails to place a box, it will be tried after the first successful placement of another box (kept in separate queue).
- `weight_const`, `flat`, `weight_top`, `weight_center`, `weight_center_flat`, `weight_center_top`, `flat_top`, `weight_center_flat_top`: specifies the weight / utility functions used in `greedy_03`. Constant corresponds to `greedy_02`, flat values low height on boxes, weight top values low top height, weight center values boxes far from center. The others correspond to linear combinations of these (each component with weight 1).

Layers `options`:
- `level_01`, `level_02`, `level_03`: specifies to use layer approach. First tries all side-lengths as layer height, second does the same but allows for fixing an item in the layer, third constructs layer for a fixed item chosen by sorting the items by some metric (default decreasing volume).
- `total`, `density`: whether the layers approach should optimize a layer for total volume in the layer, or for density of the layer (default total).
- `support`: the layers approach enforces strong stability.
- `freeform`: the layers approach does not enforce strong stability (default).
- `fix_p`: the layers approach fixes an item in the to-be-generated layer (for `level_01` and `level_02`) or fixes the height of the layer to the height of the item (`level_03`).

Examples:\
`palletization.py greedy_01 sort:volume twoqueue dataset.csv`\
`palletization.py greedy_03 sort:volume twoqueue weight_top dataset.csv`\
`palletization.py level_03 sort:volume density support fix_p dataset.csv`\
`palletization.py validate solution.csv`
