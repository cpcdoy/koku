import hashlib
import sys
import numpy as np
import pyopencl as cl
import hashlib
import random
import struct
import time
import logging

class gpu_miner:
    def __init__(self, logger):
        self.logger = logger
        try:
            #platform = cl.get_platforms()[0]
            #devices = platform.get_devices(cl.device_type.GPU)
            #self.context = cl.Context(devices, None, None)
            self.context = cl.create_some_context()
            self.devices = self.context.get_info(cl.context_info.DEVICES)
            self.queue = cl.CommandQueue(self.context, properties=cl.command_queue_properties.PROFILING_ENABLE)

            kernelFile = open('gpu/chady256.cl', 'r')
            self.miner = cl.Program(self.context, kernelFile.read()).build()
            kernelFile.close()

            self.WORK_GROUP_SIZE = 0
            self.preferred_multiple = 0
            for device in self.devices:
                self.WORK_GROUP_SIZE += self.miner.sha256_crypt_kernel.get_work_group_info(cl.kernel_work_group_info.WORK_GROUP_SIZE, device)
                self.preferred_multiple = cl.Kernel(self.miner, 'sha256_crypt_kernel').get_work_group_info(cl.kernel_work_group_info.PREFERRED_WORK_GROUP_SIZE_MULTIPLE, device)

            self.logger.info('Best workgroup size :' + str(self.WORK_GROUP_SIZE))
            self.logger.info('Preferred multiple: ' + str(self.preferred_multiple))

            self.nounce_begin = 0
            self.data_info = np.zeros(1, np.uint32)
            self.data_info[0] = 76

            self.globalThreads = self.WORK_GROUP_SIZE * 100
            self.localThreads  = 1

            self.blocks = np.zeros(self.data_info[0] * self.globalThreads, np.uint8)

            self.difficulty = 2**11

            self.logger.info("HERE")

        except Exception as inst:
            self.logger.exception("Init")
            self.logger.error(type(inst))
            self.logger.error((inst.args))

    def set_block(self, block):
        try:
            self.logger.info('set block 1')
            b = block
            self.logger.info('set block 1')
            self.logger.info(b)
            b2 = b.getPack()
            self.logger.info('set block 1')
            self.logger.info(len(b2))
            self.logger.info('set block 1')
            self.logger.info(np.frombuffer(b2[:], np.uint8))
            self.def_block = b
            self.data_info[0] = len(b2);
        except Exception as inst:
            self.logger.exception("Set block")
            self.logger.error(type(inst))
            self.logger.error((inst.args))

    def compute_hashes(self):
        self.logger.info(self.data_info)
        self.logger.info(self.blocks)
        output = np.zeros(8 * self.globalThreads, np.uint32)
        mf = cl.mem_flags

        self.blocks_tmp = np.zeros(self.globalThreads, Block)

        not_found = True
        passes = 0
        global_index = 0
        data_len = self.data_info[0]
        b = self.def_block
        while not_found:
            self.logger.info('Pass ' + passes)
            passes += 1
            for i in range(self.globalThreads):
                b.pad = self.nounce_begin + global_index

                self.blocks[i * data_len: (i + 1) * data_len] = np.frombuffer(b.getPack()[:], np.uint8)
                self.blocks_tmp[i] = b
                #self.logger.info(self.blocks[i*data_len:(i+1)*data_len])
                global_index += 1

            self.logger.info('Transfering data...')
            data_info_buf = cl.Buffer(self.context, mf.READ_ONLY  | mf.USE_HOST_PTR, hostbuf=self.data_info)
            plain_key_buf = cl.Buffer(self.context, mf.READ_ONLY  | mf.USE_HOST_PTR, hostbuf=self.blocks)
            output_buf = cl.Buffer(self.context, mf.WRITE_ONLY | mf.USE_HOST_PTR, hostbuf=output)

            self.logger.info('Starting computation...')
            exec_evt = self.miner.sha256_crypt_kernel(self.queue, (self.globalThreads, ), (self.localThreads, ), data_info_buf,  plain_key_buf, output_buf)
            exec_evt.wait()
            cl.enqueue_read_buffer(self.queue, output_buf, output).wait()

            for j in range(self.globalThreads):
                if output[j * 8] < self.difficulty:
                    for i in range(8):
                        self.logger.info(format(output[j * 8 + i], '02x'))
                    not_found = False
                    return self.blocks_tmp[i]
                #self.logger.info('Truth: ', hashlib.sha256(self.blocks[j * self.data_info[0]:(j+1) * self.data_info[0]]).hexdigest())
                #self.logger.info('')
            self.logger.info('Time to compute: ' + 1e-9 * (exec_evt.profile.end - exec_evt.profile.start))
