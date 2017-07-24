import sys
from miner.gpu_miner import gpu_miner
from common.block import Block

gpu_miner = gpu_miner()
b = Block("73475cb40a568e8da8a045ced110137e159f890ac4da883b6b17dc651b3a8049", "a4244aa43ddd6e3ef9e64bb80f4ee952f68232aa008d3da9c78e3b627e5675c8")

gpu_miner.set_blocks_count(3)
gpu_miner.add_block(b)
gpu_miner.add_block(b)
gpu_miner.add_block(b)

gpu_miner.compute_hashes()
