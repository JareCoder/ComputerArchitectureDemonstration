import os
import sysv_ipc

print("Scheduler process started!!!")

key = 1234

# Create a shared memory segment
sharedMemory = sysv_ipc.SharedMemory(key, sysv_ipc.IPC_CREX | sysv_ipc.IPC_EXCL, 1024, 0o666)

# Write to init pipe
os.close(schedulerPipeRead)
writeTo = os.fdopen(schedulerPipeWrite, 'w')
writeTo.write(str(sharedMemory.key))
writeTo.close()


sharedMemory.detach()
sysv_ipc.SharedMemory(key).remove()