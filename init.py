import os
import sys
import sysv_ipc
import random

# Init file for making children processes and getting random scheduling times
print("Init process started. Forking scheduler process...")

schedulerPipeRead, schedulerPipeWrite = os.pipe()

schedulerFork = os.fork()
if schedulerFork == 0: # Why does execl not work? Why do we need to fork and do if else?
    print("Scheduler process started!!!")

    key = 1234

    # Create a shared memory segment
    sharedMemory = sysv_ipc.SharedMemory(key, sysv_ipc.IPC_CREAT | sysv_ipc.IPC_EXCL, 1024, 0o666)

    # Write to init pipe
    os.close(schedulerPipeRead)
    writeTo = os.fdopen(schedulerPipeWrite, 'w')
    writeTo.write(str(key))
    writeTo.close()

    sharedMemory.detach()
    sysv_ipc.SharedMemory(key).remove()
else:
    os.close(schedulerPipeWrite)
    readFromScheduler = os.fdopen(schedulerPipeRead)
    key = readFromScheduler.read().strip()
    print("Key: ", key)

# Init
schedulerList = []

processes = 4
for i in range(processes):

    pipeRead, pipeWrite = os.pipe()

    forkPid = os.fork()
    if forkPid == 0:
        os.close(pipeRead)

        writeTo = os.fdopen(pipeWrite, 'w')
        writeTo.write(str(random.randint(0, 19)))
        writeTo.close()
        os._exit(0)

    else:
        os.close(pipeWrite)
        readFrom = os.fdopen(pipeRead)
        pipeData = readFrom.read().strip()
        schedulerList.append(pipeData)
        readFrom.close()
        

print("Scheduler list: ", schedulerList)