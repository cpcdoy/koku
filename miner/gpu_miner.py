import hashlib
import sys
import numpy as np
import pyopencl as cl
import hashlib
import random
import struct
import time

class Block:

    def __init__(self, prev, root):
        self.prev = prev
        self.root = root
        self.time = int(round(time.time()))
        self.bits = 20
        self.pad = 42#random.randrange(2 ** 32)

    def __str__(self):
        return "<Block prev:%s root:%s time:%d bits:%d pad:%d>" % (self.prev, self.root, self.time, self.bits, self.pad)

    def getPack(self):
        prev_encode = self.prev.encode()
        root_encode = self.root.encode()

        return struct.pack('ssIII', prev_encode, root_encode, self.time, self.bits, self.pad)

def checkChain(chain):
    prev = None
    for b in chain:
        if not prev is None and prev != b.prev:
            return False
        m = hashlib.sha256()
        m.update(b.getPack())
        prev = m.digest()
    return True

class gpu_miner:
    def __init__(self):
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

        self.nounce_begin = 0
        self.data_info = np.zeros(1, np.uint32)
        self.data_info[0] = 16;

        self.globalThreads = self.WORK_GROUP_SIZE * 100
        self.localThreads  = 1

        self.blocks = np.zeros(self.data_info[0] * self.globalThreads, bytes)

    def set_block(self, block):
        b = block
        print(b)
        b2 = b.getPack()
        print(len(b2))
        self.def_block = b
        self.data_info[0] = len(b2);

    def compute_hashes(self):
        print(self.data_info)
        print(self.blocks)
        output = np.zeros(8 * self.globalThreads, np.uint32)
        mf = cl.mem_flags

        not_found = True
        passes = 0
        while not_found:
            print('Pass ', passes)
            passes += 1
            for i in range(0, self.globalThreads, 16):
                b = self.def_block
                b.pad = self.nounce_begin + i
                self.blocks[i:i+16] = np.frombuffer(b.getPack()[:], np.uint8)

            print('Transfering data...')
            data_info_buf = cl.Buffer(self.context, mf.READ_ONLY  | mf.USE_HOST_PTR, hostbuf=self.data_info)
            plain_key_buf = cl.Buffer(self.context, mf.READ_ONLY  | mf.USE_HOST_PTR, hostbuf=self.blocks)
            output_buf = cl.Buffer(self.context, mf.WRITE_ONLY | mf.USE_HOST_PTR, hostbuf=output)

            print('Starting computation...')
            exec_evt = self.miner.sha256_crypt_kernel(self.queue, (self.globalThreads, ), (self.localThreads, ), data_info_buf,  plain_key_buf, output_buf)
            exec_evt.wait()
            cl.enqueue_read_buffer(self.queue, output_buf, output).wait()

            self.nounce_begin += self.globalThreads

            for j in range(self.globalThreads):
                for i in range(8):
                    print(format(output[j * 8 + i], '02x'))
                print('')
            #print(output)
            #    print('Truth: ', hashlib.sha256(self.blocks[j * self.data_info[0]:(j+1) * self.data_info[0]]).hexdigest())
            print('Time to compute: ', 1e-9 * (exec_evt.profile.end - exec_evt.profile.start))


gpu_miner = gpu_miner()
b = Block("73475cb40a568e8da8a045ced110137e159f890ac4da883b6b17dc651b3a8049", "a4244aa43ddd6e3ef9e64bb80f4ee952f68232aa008d3da9c78e3b627e5675c8")

gpu_miner.set_block(b)

gpu_miner.compute_hashes()
