# By: EnderMandS - 周日 7月 17 2022

import sensor, image, time
from pyb import LED, Timer, Pin, UART
import ustruct


# Const define
NOT_AVAILABLE_ = 0
RED_ = 1
GREEN_ = 2
YELLOW_ = 3

PI_ = 3.14159265358979

ROUNDNESS_THRESHOLD_ = 0.8
FILTER_FRAME_CNT_ = 5

GREEN_THRESHOLD_ = (72, 95, -128, -48, 12, 86)
RED_THRESHOLD_ = (50, 80, 50, 100, 30, 100)
YELLOW_THRESHOLD_ = (70, 100, -20, 20, 0, 127)

# Board LED init
red_led     = LED(1)
green_led   = LED(2)
blue_led    = LED(3)

# 
P0 = Pin('P0', Pin.OUT_PP)
P1 = Pin('P1', Pin.OUT_PP)
P0.low()
P1.low()

# class TrafficLightFilter:
#     def __init__(self):
#         self.count = 0
#         self.status = False

#     def iterate(self, status_input):
#         if status_input == self.status :
#             self.count = 0
#         else :
#             self.count = self.count + 1
#             if self.count >= FILTER_FRAME_CNT_ :
#                 self.reverse()

#     def clear(self) :
#         self.count = 0
#         self.status = False

#     def reverse(self) :
#         self.count = 0
#         if self.status :
#             self.status = False
#         else :
#             self.status = True

FILTER_UP_THRESHOLD_ = 3
FILTER_DOWN_THRESHOLD_ = 10
class TrafficLightFilter:
    def __init__(self):
        self.count = 0
        self.status = False

    def iterate(self, status_input:bool):
        if status_input == self.status :
            self.count = 0
        else:
            ++self.count
            if self.status==False:
                if self.count >= FILTER_UP_THRESHOLD_:
                    self.reverse()
            else:
                if self.count >= FILTER_DOWN_THRESHOLD_:
                    self.reverse()

    def reverse(self):
        self.count = 0
        if self.status:
            self.status = False
        else:
            self.status = True


class TrafficLight:
    def __init__(self):
        self.current_color = GREEN_
        # Filter init
        self.red_filter     = TrafficLightFilter()
        self.yellow_filter  = TrafficLightFilter()
        self.green_filter   = TrafficLightFilter()
        self.total_filter   = TrafficLightFilter()


    def trafficColorGet(self, img, c, color_threshold):
        rec_area = ( c.x()-c.r(), c.y()-c.r(), 2*c.r(), 2*c.r() )
        x_stride = y_stride = c.r()-10
        area_threshold = (int)(PI_*c.r()*c.r()*0.5)

        if x_stride<5:
            x_stride = y_stride = 5
        if area_threshold < 5:
            area_threshold = 5

        return img.find_blobs([color_threshold],
            roi = rec_area,
            x_stride = x_stride, y_stride = y_stride,
            area_threshold = area_threshold,
            pixels_threshold = 10, merge = True)

    def colorFind(self, img, c, color_threshold):
        area = (c.x()-c.r()/2, c.y()-c.r()/2, c.r(), c.r())

        statistics = img.get_statistics(roi=area)
        if color_threshold(0)<statistics.l_mode()<color_threshold(1) and \
           color_threshold(2)<statistics.a_mode()<color_threshold(3) and \
           color_threshold(4)<statistics.a_mode()<color_threshold(5):
            return True
        return False

    def trafficLightFind(self, img):
        circles = img.find_circles(threshold = 5000,
            x_margin = 10, y_margin = 10, r_margin = 10,
            r_min = 10, r_max = 50, r_step = 2)

        if circles == [] :
            self.total_filter.iterate(False)
            self.red_filter.iterate(False)
            self.green_filter.iterate(False)
            self.yellow_filter.iterate(False)
        else :
            red_find = yellow_find = green_find = False

            for c in circles:
                rec_area = ( c.x()-c.r(), c.y()-c.r(), 2*c.r(), 2*c.r() )
                img.draw_rectangle(rec_area, color = (0, 0, 255))

                # red_blobs = self.trafficColorGet(img, c, RED_THRESHOLD_)
                # for blo in red_blobs:
                #     if blo.roundness()>ROUNDNESS_THRESHOLD_ :
                #         img.draw_rectangle(blo.rect(), color = (255, 0, 0))
                #         red_find = True

                # green_blobs = self.trafficColorGet(img, c, GREEN_THRESHOLD_)
                # for blo in green_blobs:
                #     if blo.roundness()>ROUNDNESS_THRESHOLD_ :
                #         img.draw_rectangle(blo.rect(), color = (0, 255, 0))
                #         green_find = True

                # yellow_blobs = self.trafficColorGet(img, c, YELLOW_THRESHOLD_)
                # for blo in yellow_blobs:
                #     if blo.roundness()>ROUNDNESS_THRESHOLD_ :
                #         img.draw_rectangle(blo.rect(), color = (255, 255, 0))
                #         yellow_find = True

                red_find = self.colorFind(img, c, RED_THRESHOLD_)
                green_find = self.colorFind(img, c, GREEN_THRESHOLD_)
                yellow_find = self.colorFind(img, c, YELLOW_THRESHOLD_)

                if red_find:
                    img.draw_circle(c, color=(255, 0, 0))
                if green_find:
                    img.draw_circle(c, color=(0, 255, 0))
                if yellow_find:
                    img.draw_circle(c, color=(255, 255, 0))

            if (not red_find) and (not green_find) and (not yellow_find) :
                self.total_filter.iterate(False)
            else :
                self.total_filter.iterate(True)

            self.red_filter.iterate(red_find)
            self.yellow_filter.iterate(yellow_find)
            self.green_filter.iterate(green_find)

    def filterOutcome(self):
        if self.total_filter.status :
            if self.red_filter.status :
                self.current_color = RED_
                red_led.on()
                P0.high()   # 1
                P1.low()
                return
            elif self.yellow_filter.status :
                self.current_color = YELLOW_
                red_led.on()
                green_led.on()
                P0.high()   # 3
                P1.high()
                return
            elif self.green_filter.status :
                self.current_color = GREEN_
                green_led.on()
                P0.low()    # 2
                P1.high()
                return

        self.current_color = NOT_AVAILABLE_
        P0.low()    # 0
        P1.low()
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

# Uart init P4-TX P5-RX
uart = UART(3, 9600, timeout_char = 100 )
uart.init(9600, bits=8, parity=None, stop=1, timeout_char = 100)

traffic_light = TrafficLight()

while(True):
    clock.tick()
    img = sensor.snapshot()
    traffic_light.trafficLightFind(img)
    traffic_light.filterOutcome()
    uart.write(ustruct.pack("<b",traffic_light.current_color))
    print(clock.fps())
