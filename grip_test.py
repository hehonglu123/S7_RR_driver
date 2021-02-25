from relay_lib_seeed import *
import time

for i in range(5):
	relay_on(1)
	time.sleep(2)
	relay_off(1)
	relay_on(2)
	time.sleep(2)
	relay_off(2)