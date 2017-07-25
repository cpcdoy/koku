#!/usr/bin/python

import hashlib
import sys
import numpy as np
import pyopencl as cl

class gpu_miner:
    def __init__(self):
        self.curr_block_index = 0
        self.block_count = 0

        platform = cl.get_platforms()[0]

        devices = platform.get_devices(cl.device_type.GPU)
        self.context = cl.Context(devices, None, None)
        self.queue = cl.CommandQueue(self.context, properties=cl.command_queue_properties.PROFILING_ENABLE)

        kernelFile = open('chady256.cl', 'r')
        self.miner = cl.Program(self.context, kernelFile.read()).build()
        kernelFile.close()

        self.WORK_GROUP_SIZE = 0
        self.preferred_multiple = 0
        for device in devices:
            self.WORK_GROUP_SIZE += self.miner.sha256_crypt_kernel.get_work_group_info(cl.kernel_work_group_info.WORK_GROUP_SIZE, device)
            preferred_multiple = cl.Kernel(self.miner, 'sha256_crypt_kernel').get_work_group_info(cl.kernel_work_group_info.PREFERRED_WORK_GROUP_SIZE_MULTIPLE, device)

        print('Best workgroup size :', self.WORK_GROUP_SIZE)
        print('Preferred multiple :', preferred_multiple)

        self.data_info = np.zeros(1, np.uint32)
        self.data_info[0] = 32 * 2 + 4 * 3;

    def set_blocks_count(self, count):
        self.block_count = count
        self.blocks = np.zeros(count * self.data_info[0], bytes)

    def add_block(self, block):
        self.blocks[self.curr_block_index * self.data_info[0]] = block.getPack()
        self.curr_block_index += 1

    def compute_hashes(self):
        print(self.data_info)
        print(self.blocks)
        globalThreads = self.WORK_GROUP_SIZE * self.block_count
        localThreads  = 1
        output = np.zeros(8 * self.block_count, np.uint32)

        mf = cl.mem_flags

        print('Transfering data...')
        data_info_buf = cl.Buffer(self.context, mf.READ_ONLY  | mf.USE_HOST_PTR, hostbuf=self.data_info)
        plain_key_buf = cl.Buffer(self.context, mf.READ_ONLY  | mf.USE_HOST_PTR, hostbuf=self.blocks)
        output_buf = cl.Buffer(self.context, mf.WRITE_ONLY | mf.USE_HOST_PTR, hostbuf=output)

        print('Starting computation...')
        exec_evt = self.miner.sha256_crypt_kernel(self.queue, (globalThreads, ), (localThreads, ), data_info_buf,  plain_key_buf, output_buf)
        exec_evt.wait()
        cl.enqueue_read_buffer(self.queue, output_buf, output).wait()

        for j in range(self.block_count):
            for i in range(8):
                print(format(output[j * 8 + i], '02x'))
            print('Truth: ', hashlib.sha256(self.blocks[j * self.data_info[0]:(j+1) * self.data_info[0]]).hexdigest())

        print('Time to compute: ', 1e-9 * (exec_evt.profile.end - exec_evt.profile.start))
