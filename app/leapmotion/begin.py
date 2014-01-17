import sys

if (len(sys.argv) > 1 and sys.argv[1]=='x64'):
	sys.path.insert(0, './x64')
else :
	sys.path.insert(0, './x86')

import Leap
import threading
from pymouse import PyMouse
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture



def timer_Disable(controller):
	controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE)


class SampleListener(Leap.Listener):
	def on_init(self,controller):
		print"initialized"

	def on_disconnect(self,controller):
		print"Disconnected"
	def on_exit(self,controller):
		print"Exited"

		

	def on_connect(self, controller):
		print"connected"
		#enable gesture
		#circle movement by a finger
		controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE)
		#straight line movement by the hand with finger extended
		controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP)
		#forward tapping movement by finger
		controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP)
		#downward ""
		controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)

	def on_frame(self,controller):
		m=PyMouse()
		x_dim, y_dim = m.screen_size()
		frame = controller.frame()
		print"Frame id: {}, timestamp: {}, hand: {}, fingers{}, tools: {}".format(frame.id, frame.timestamp,len(frame.hands),len(frame.fingers),len(frame.tools))

		if not frame.hands.is_empty:
			hand=frame.hands[0]
			fingers=hand.fingers
			if not fingers.is_empty:
				print fingers[0].tip_position.x
				print fingers[0].tip_position.y
				m.move(((fingers[0].tip_position.x)+160)*x_dim/320,y_dim-((fingers[0].tip_position.y)-200)*y_dim/200)
				#alculate avg position
				avg_pos = Leap.Vector()
				for finger in fingers:
					avg_pos+=finger.tip_position
				avg_pos /= len(fingers)
				print "Hand has ablablabl"

				# can get radius and palm position print "Hand sphere radius: %f mm, palm position: %s" % (hand.sphere_radius, hand.palm_position)

				#can also get angles...


		for gesture in frame.gestures():
			if controller.is_gesture_enabled(Leap.Gesture.TYPE_CIRCLE):
				if gesture.type == Leap.Gesture.TYPE_CIRCLE:
					circle = CircleGesture(gesture)
					m.click((circle.center.x+160)*x_dim/320,y_dim-(circle.center.y-200)*y_dim/200);
					if circle.center.x <0: #&& circle.center.y>230:
						print"upper left"
					else:
						print"right" 
					controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE,False)
					t=threading.Timer(2.0,timer_Disable,[controller])
					t.start()


def main():
	listener = SampleListener()
	controller = Leap.Controller()
	
	controller.add_listener(listener)
	print"Enter to quit"
	sys.stdin.readline()

	controller.remove_listener(listener)

main()
