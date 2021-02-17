from relay_lib_seeed import *
import RobotRaconteur as RR
RRN=RR.RobotRaconteurNode.s
import RobotRaconteurCompanion as RRC
import numpy as np 
import time, traceback, threading, signal

class S7Impl(object):
	def __init__(self):
		#sensor
		self.tool_state=None
		#rolling
		self.signal_dict={'roll1':1,'grip1':2,'roll2':3,'grip2':4}
		self._lock = threading.Lock()
		self._streaming = False

	def open(self):
		relay_off(self.signal_dict['grip1'])
		relay_off(self.signal_dict['grip2'])

	def close(self):
		relay_on(self.signal_dict['grip1'])
		relay_on(self.signal_dict['grip2'])
	#sensor reading
	def threadfunc(self):
		while(self._streaming):
			with self._capture_lock:


	def StartStreaming(self):
		if (self._streaming):
			raise RR.InvalidOperationException("Already streaming")
		self._streaming=True
		t=threading.Thread(target=self.threadfunc)
		t.start()
	def StopStreaming(self):
		if (not self._streaming):
			raise RR.InvalidOperationException("Not streaming")
		self._streaming=False


with RR.ServerNodeSetup("s7_gripper",22222) as node_setup:
	RRC.RegisterStdRobDefServiceTypes(RRN)

	gripper_inst=S7Impl(tool_info)
    service_ctx = RRN.RegisterService("tool","com.robotraconteur.robotics.tool.Tool",gripper_inst)


    print("Press ctrl+c to quit")
    signal.sigwait([signal.SIGTERM,signal.SIGINT])