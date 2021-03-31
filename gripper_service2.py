from relay_lib_seeed import *
import RobotRaconteur as RR
RRN=RR.RobotRaconteurNode.s
import RobotRaconteurCompanion as RRC
from RobotRaconteurCompanion.Util.DateTimeUtil import DateTimeUtil
import numpy as np 
import time, traceback, threading, signal
from gpiozero import Button

class StateMachine(object):
	def __init__(self, S7_obj):
		# self.machine= {0 : self.released,
		#    1 : self.rolling,
		#    2 : self.gripping,
		#    3 : self.gripped}
		self.S7_obj=S7_obj
	def machine(self):
		if self.S7_obj.state==0:
			self.released()
		elif self.S7_obj.state==1:
			self.rolling()
		elif self.S7_obj.state==2:
			self.gripping()
		elif self.S7_obj.state==3:
			self.gripped()
		else:
			self.releasing()
	def released(self):	
		if self.S7_obj.switch.is_pressed:
			self.S7_obj.state=1
			self.S7_obj.roll()
		return
	def rolling(self):
		if self.S7_obj.fabric_present.is_pressed:
			self.S7_obj.state=2
			self.S7_obj.roll_off()
			self.S7_obj.close()
	def gripping(self):
		if not self.S7_obj.switch.is_pressed:
			self.S7_obj.state=3
	def gripped(self):
		if self.S7_obj.switch.is_pressed:
			self.S7_obj.state=4
			self.S7_obj.open()
		return
	def releasing(self):
		if not self.S7_obj.switch.is_pressed:
			self.S7_obj.state=0
		return

class S7Impl(object):
	def __init__(self):
		#sensor
		# self.tool_state=None
		#rolling
		self.port_dict={'roll1':1,'grip1':2,'roll2':3,'grip2':4}
		self._lock = threading.Lock()
		self._streaming = False


		self.switch1=Button(22, pull_up=False)#22: mechanical switch
		self.fabric_present1=Button(17, pull_up=False)#17: detection sensor
		self.switch2=Button(23, pull_up=False)#22: mechanical switch
		self.fabric_present2=Button(18, pull_up=False)#17: detection sensor
		self.sensor_list=[0,0,0,0]	#gripper1 fabric_present, switch, gripper2 fabric_present, switch
		self.tool_state_type=RRN.NewStructure("com.robotraconteur.robotics.tool.ToolState")
		self._date_time_util = DateTimeUtil(RRN)

		self.state=0
		self.state_machine=StateMachine(self)

	def roll(self):
		relay_on(self.port_dict['roll1'])
		relay_on(self.port_dict['roll2'])
	def roll_off(self):
		relay_off(self.port_dict['roll1'])
		relay_off(self.port_dict['roll2'])
	def open(self):
		relay_off(self.port_dict['grip1'])
		relay_off(self.port_dict['grip2'])

	def close(self):
		relay_on(self.port_dict['grip1'])
		relay_on(self.port_dict['grip2'])
	#sensor reading
	def threadfunc(self):
		while(self._streaming):
			time.sleep(0.002)
			with self._lock:
				try:
					ToolState=self.tool_state_type
					self.sensor_list=[0,0,0,0]
					if self.fabric_present1.is_pressed:
						self.sensor_list[0]=1
					if self.switch1.is_pressed:
						self.sensor_list[1]=1
					if self.fabric_present2.is_pressed:
						self.sensor_list[3]=1
					if self.switch2.is_pressed:
						self.sensor_list[4]=1
					ToolState.sensor=self.sensor_list
					ToolState.ts=self._date_time_util.TimeSpec3Now()
					self.tool_state.OutValue=ToolState
					# self.state_machine.machine()
					# print(self.state)
				except:
					traceback.print_exc()

				


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

	def setf_param(self,param_name, value):
		if value.data:
			relay_on(self.port_dict[param_name])
		else:
			relay_off(self.port_dict[param_name])


with RR.ServerNodeSetup("abb_s7_gripper",22222) as node_setup:
	RRC.RegisterStdRobDefServiceTypes(RRN)

	gripper_inst=S7Impl()
	service_ctx = RRN.RegisterService("tool","com.robotraconteur.robotics.tool.Tool",gripper_inst)

	gripper_inst.StartStreaming()
	print("Press ctrl+c to quit")
	signal.sigwait([signal.SIGTERM,signal.SIGINT])