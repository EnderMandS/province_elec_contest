# By: EnderMandS - 周日 7月 17 2022

import sensor, image, time
from pyb import LED, Timer, Pin


# Const define
RED_ = 0
GREEN_ = 1
YELLOW_ = 2

PI_ = 3.14159265358979

ROUNDNESS_THRESHOLD_ = 0.85
FILTER_FRAME_CNT_ = 5

GREEN_THRESHOLD_ = (72, 95, -128, -48, 12, 86)
RED_THRESHOLD_ = (50, 80, 50, 100, 30, 100)
YELLOW_THRESHOLD_ = (70, 100, -20, 20, 0, 127)

YELLOW_X_TOLERANCE_ = 10
YELLOW_Y_TOLERANCE_ = 10

# Board LED init
red_led     = LED(1)
green_led   = LED(2)
blue_led    = LED(3)

class TrafficLightFilter:
    def __init__(self):
        self.count = 0
        self.status = False

    def iterate(self, status_input):
        if status_input == self.status :
            self.count = 0
        else :
            self.count = self.count + 1
            if self.count >= FILTER_FRAME_CNT_ :
                self.reverse()

    def clear(self) :
        self.count = 0
        self.status = False

    def reverse(self) :
        self.count = 0
        if self.status :
            self.status = False
        else :
            self.status = True


class TrafficLight:
    def __init__(self):
        self.current_color = GREEN_
        self.available = False
        # Filter init
        self.red_filter     = TrafficLightFilter()
        self.yellow_filter  = TrafficLightFilter()
        self.green_filter   = TrafficLightFilter()
        self.total_filter   = TrafficLightFilter()

    def trafficColorGet(self, img, c, color_threshold):
        rec_area = ( c.x()-c.r(), c.y()-c.r(), 2*c.r(), 2*c.r() )
        x_stride = y_stride = c.r()-10
        area_threshold = (int)(PI_*c.r()*c.r()*0.25)

        if x_stride<5:
            x_stride = y_stride = 5
        if area_threshold < 5:
            area_threshold = 5

        return img.find_blobs([color_threshold],
            roi = rec_area,
            x_stride = x_stride, y_stride = y_stride,
            area_threshold = area_threshold,
            pixels_threshold = 10, merge = False)

    def trafficLightFind(self, img):
        circles = img.find_circles(threshold = 5000,
            x_margin = 10, y_margin = 10, r_margin = 10,
            r_min = 10, r_max = 50, r_step = 2)

        if circles == [] :
            self.total_filter.iterate(False)
        else :
            red_find = yellow_find = green_find = False

            for c in circles:
                rec_area = ( c.x()-c.r(), c.y()-c.r(), 2*c.r(), 2*c.r() )
                img.draw_rectangle(rec_area, color = (0, 0, 255))

                red_blobs = self.trafficColorGet(img, c, RED_THRESHOLD_)
                for blo in red_blobs:
                    if blo.roundness()>ROUNDNESS_THRESHOLD_ :
                        img.draw_rectangle(blo.rect(), color = (255, 0, 0))
                        red_find = True

                green_blobs = self.trafficColorGet(img, c, GREEN_THRESHOLD_)
                for blo in green_blobs:
                    if blo.roundness()>ROUNDNESS_THRESHOLD_ :
                        img.draw_rectangle(blo.rect(), color = (0, 255, 0))
                        green_find = True

                yellow_blobs = self.trafficColorGet(img, c, YELLOW_THRESHOLD_)
                for blo in yellow_blobs:
                    if blo.roundness()>ROUNDNESS_THRESHOLD_ :
                        img.draw_rectangle(blo.rect(), color = (255, 255, 0))
                        yellow_find = True

            if (not red_find) and (not green_find) and (not yellow_find) :
                self.total_filter.iterate(False)
            else :
                self.total_filter.iterate(True)

            self.red_filter.iterate(red_find)
            self.yellow_filter.iterate(yellow_find)
            self.green_filter.iterate(green_find)

    def filterOutcome(self):
        if self.total_filter.status :
            self.available = True
            if self.red_filter.status :
                self.current_color = RED_
                red_led.on()
            elif self.yellow_filter.status :
                self.current_color = YELLOW_
                red_led.on()
                green_led.on()
            elif self.green_filter.status :
                self.current_color = GREEN_
                green_led.on()
            else :
                self.available = False
                red_led.off()
                green_led.off()
                blue_led.off()

        else :
            self.available = False
            red_led.off()
            green_led.off()
            blue_led.off()


# Sensor init
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(True)
sensor.set_auto_whitebal(False)

# Clock init
clock = time.clock()

## Timer callback
#def Tim14Callback(timer):   # LED工作指示
    #pass

## Timer init
#tim14 = Timer(14, freq = 1)
#tim14.callback(Tim14Callback)

traffic_light = TrafficLight()

while(True):
    clock.tick()
    img = sensor.snapshot()
    traffic_light.trafficLightFind(img)
    traffic_light.filterOutcome()
    print(clock.fps())
