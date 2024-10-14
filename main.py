import os
import sys
import sysv_ipc


print("Starting...")

# We need to fork this instance into at least 2 processes. The init script and the scheduler.

initFork = os.fork()

if initFork == 0:
    os.execl(sys.executable, sys.executable, "init.py")



