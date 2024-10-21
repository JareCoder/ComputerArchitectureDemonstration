import os
import time
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
    try:
        sharedMemory = sysv_ipc.SharedMemory(key, sysv_ipc.IPC_CREAT | sysv_ipc.IPC_EXCL, 1024, 0o666)
    except sysv_ipc.ExistentialError:
        print("Shared memory already exists. Removing and creating new one...")
        sysv_ipc.SharedMemory(key).remove()
        sharedMemory = sysv_ipc.SharedMemory(key, sysv_ipc.IPC_CREAT | sysv_ipc.IPC_EXCL, 1024, 0o666)
    except Exception as e:
        print("Error creating shared memory: " + str(e))
        exit(1)

    # Write to init pipe
    os.close(schedulerPipeRead)
    writeTo = os.fdopen(schedulerPipeWrite, 'w')
    writeTo.write(str(key))
    writeTo.close()

    sharedMemory.attach()
    print("Waiting for shared memory to be written to...")
    while True: # Funny loop to check first byte of shared memory
        flag = sharedMemory.read(1)
        if flag and flag[0] != 0:
            print("Shared memory written to!")
            break
        time.sleep(0.1)

    data = sharedMemory.read(1024).decode('utf-8').rstrip('\x00') # Strip null bytes and read
    dataList = data.split(",")
    
    # Convert to int
    try:
        dataList = [int(i) for i in dataList]
    except Exception as e:
        print("Error converting data to int. Aborting: " + str(e))
        exit(1)
    
    dataList.sort()
    print("\nSorted list from shared memory: ", dataList)

    print("\nDetaching and removing shared memory...")
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

print("Trying to attach to shared memory and write list...")
try:
    sharedMemoryRefInInit = sysv_ipc.SharedMemory(key)
    sharedMemoryRefInInit.write(",".join(schedulerList).encode('utf-8'))
    sharedMemoryRefInInit.detach()
    print("Shared memory write succesful!")
except Exception as e:
    print("Error attaching shared memory and writing: " + str(e))
        
print("Init process done! Waiting for scheduler to finish...")
os.waitpid(schedulerFork, 0)

# print("Scheduler list: ", schedulerList)