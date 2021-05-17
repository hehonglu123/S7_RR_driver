from relay_lib_seeed import *
import RobotRaconteur as RR
RRN=RR.RobotRaconteurNode.s
import RobotRaconteurCompanion as RRC
from RobotRaconteurCompanion.Util.DateTimeUtil import DateTimeUtil
import numpy as np 
import time, traceback, threading, signal
from gpiozero import Button

class S7Impl(object):
	def __init__(self):

		self.tool_state_type=RRN.NewStructure("com.robotraconteur.robotics.tool.ToolState")
		self._date_time_util = DateTimeUtil(RRN)

	def open(self):
		relay_off(1)

	def close(self):
		relay_on(1)



with RR.ServerNodeSetup("abb_s7_gripper",22222) as node_setup:
	RRC.RegisterStdRobDefServiceTypes(RRN)

	gripper_inst=S7Impl()
	service_ctx = RRN.RegisterService("tool","com.robotraconteur.robotics.tool.Tool",gripper_inst)

	print("Press ctrl+c to quit")
	signal.sigwait([signal.SIGTERM,signal.SIGINT])