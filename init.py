import os
import sys
import sysv_ipc
import random

# Init file for making children processes and getting random scheduling times
print("Init process started. Forking scheduler process...")

schedulerPipeRead, schedulerPipeWrite = os.pipe()

schedulerFork = os.fork()
if schedulerFork == 0:
    print("Scheduler process started!!!")

    key = 1234

    # Create a shared memory segment
    sharedMemory = sysv_ipc.SharedMemory(key, sysv_ipc.IPC_CREAT | sysv_ipc.IPC_EXCL, 1024, 0o666)

    # Write to init pipe
    os.close(schedulerPipeRead)
    writeTo = os.fdopen(schedulerPipeWrite, 'w')
    writeTo.write(str(key))
    writeTo.close()

    # Wait until something is written into shared memory
    sharedMemory.attach()
    print("Waiting for shared memory to be written to...")
    while sharedMemory.read() == "": pass
    print("Shared memory written to!")
    data = sharedMemory.read().decode('utf-8')
    print("Data from shared memory: ", data)

    sharedMemory.detach()
    sysv_ipc.SharedMemory(key).remove()
    os._exit(0)
else:
    # Read from scheduler to know where to write
    os.close(schedulerPipeWrite)
    readFromScheduler = os.fdopen(schedulerPipeRead)
    key_str = readFromScheduler.read().strip()
    if key_str == "":
        print("Key is empty! Aborting...")
        exit(1)
    key = int(key_str)
    readFromScheduler.close()

    print("Key: ", key)

# Init
schedulerList = []

processes = 4
for i in range(processes):

    pipeRead, pipeWrite = os.pipe()

    forkPid = os.fork()
    if forkPid == 0:
        # Am child :3
        os.close(pipeRead)

        writeTo = os.fdopen(pipeWrite, 'w')
        writeTo.write(str(random.randint(0, 19)))
        writeTo.close()
        os._exit(0)

    else:
        # Read from children
        os.close(pipeWrite)
        readFrom = os.fdopen(pipeRead)
        pipeData = readFrom.read().strip()
        schedulerList.append(pipeData)
        readFrom.close()

try:
    print("Trying to attach to shared memory and write list...")
    sharedMemoryRefInInit = sysv_ipc.SharedMemory(key)
    sharedMemoryRefInInit.write(",".join(schedulerList).encode('utf-8'))
    sharedMemoryRefInInit.detach()
except Exception as e:
    print("Error attaching shared memory and writing: " + str(e))
        

# print("Scheduler list: ", schedulerList)