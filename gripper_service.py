from relay_lib_seeed import *
import RobotRaconteur as RR
RRN=RR.RobotRaconteurNode.s
import RobotRaconteurCompanion as RRC
import numpy as np 
import time, traceback, threading, signal
from gpiozero import Button


class S7Impl(object):
	def __init__(self):
		#sensor
		self.tool_state=None
		#rolling
		self.port_dict={'roll1':1,'grip1':2,'roll2':3,'grip2':4}
		self._lock = threading.Lock()
		self._streaming = False
		self.switch=Button(22, pull_up=False)
		self.fabric_present=Button(17, pull_up=False)
		self.sensor_list=[0,0,0,0]	#gripper1 fabric_present, switch, gripper2 fabric_present, switch
		self.tool_state_type=RRN.NewStructure("com.robotraconteur.robotics.tool.ToolState")

	def open(self):
		relay_off(self.port_dict['grip1'])
		# relay_off(self.port_dict['grip2'])

	def close(self):
		relay_on(self.port_dict['grip1'])
		# relay_on(self.port_dict['grip2'])
	#sensor reading
	def threadfunc(self):
		while(self._streaming):
			with self._capture_lock:
				ToolState=self.tool_state_type
				self.sensor_list=[0,0,0,0]
				if self.fabric_present.is_pressed:
					self.sensor_list[0]=1
				if self.switch.is_pressed:
					self.sensor_list[1]=1
				ToolState.sensor=self.sensor_list[0]
				self.tool_state.OutValue=ToolState
				


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