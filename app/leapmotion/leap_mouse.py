import sys

if (len(sys.argv) > 1 and sys.argv[1]=='x64'):
    sys.path.insert(0, './x64')
else :
    sys.path.insert(0, './x86')

import Leap
import threading
from pymouse import PyMouse
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture



def timer_disable_circle(controller):
    controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE)

def timer_disable_screen(controller):
    controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP)

def timer_disable_swipe(controller):
    controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)


class SampleListener(Leap.Listener):

    m=PyMouse()
    x_dim, y_dim = m.screen_size()

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
        controller.config.set("Gesture.ScreenTap.MinForwardVelocity", 10.0)
        controller.config.set("Gesture.ScreenTap.HistorySeconds", 1.0)
        controller.config.set("Gesture.ScreenTap.MinDistance", 10.0)
        controller.config.save()


    def on_frame(self,controller):
        frame = controller.frame()
        #print"Frame id: {}, timestamp: {}, hand: {}, fingers{}, tools: {}".format(frame.id, frame.timestamp,len(frame.hands),len(frame.fingers),len(frame.tools))

        if not frame.hands.is_empty:
            hand=frame.hands[0]
            fingers=hand.fingers
            if not fingers.is_empty and len(fingers)<2:
                #print fingers[0].tip_position.x
                #print fingers[0].tip_position.y
                self.m.move(((fingers[0].tip_position.x)+160)*self.x_dim/320,self.y_dim-((fingers[0].tip_position.y)-200)*self.y_dim/200)
                # can get radius and palm position print "Hand sphere radius: %f mm, palm position: %s" % (hand.sphere_radius, hand.palm_position)

                #can also get angles...

            for gesture in frame.gestures():
                if controller.is_gesture_enabled(Leap.Gesture.TYPE_CIRCLE):
                    if gesture.type == Leap.Gesture.TYPE_CIRCLE:
                        circle = CircleGesture(gesture)
                        self.m.click((circle.center.x+160)*self.x_dim/320,self.y_dim-(circle.center.y-200)*self.y_dim/200);
                        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE,False)
                        t=threading.Timer(2.0,timer_disable_circle,[controller])
                        t.start()

                if controller.is_gesture_enabled(Leap.Gesture.TYPE_SCREEN_TAP):
                    if len(fingers) == 2 :
                        if gesture.type == Leap.Gesture.TYPE_SCREEN_TAP:
                            tap =  ScreenTapGesture(gesture)
                            self.m.click(self.m.position()[0],self.m.position()[1])
                            controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP,False)
                            t=threading.Timer(1.0,timer_disable_screen,[controller])
                            t.start()

                if controller.is_gesture_enabled(Leap.Gesture.TYPE_SWIPE):
                    if len(fingers) == 3 :
                        if gesture.type == Leap.Gesture.TYPE_SWIPE:
                            sw_gest = SwipeGesture(gesture)
                            self.m.scroll(sw_gest.direction.y*10)
                            controller.enable_gesture(Leap.Gesture.TYPE_SWIPE,False)
                            t=threading.Timer(1.0,timer_disable_swipe,[controller])
                            t.start()


                #check if need to stop the alarm
            #   if hand.palm_position().y<-200 :






def main():
    listener = SampleListener()
    controller = Leap.Controller()

    controller.add_listener(listener)
    print"Enter to quit"
    sys.stdin.readline()

    controller.remove_listener(listener)

main()
