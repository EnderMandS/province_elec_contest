# By: EnderMandS - 周日 7月 17 2022

import sensor, image, time
from pyb import LED, Timer, Pin

# Const define
RED_ = 0
GREEN_ = 1
PI_ = 3.14159265358979
R_ = 25

# Board LED init
red_led     = LED(1)
green_led   = LED(2)
blue_led    = LED(3)
ir_leds     = LED(4)

# Traffic light threadhold
GREEN_THRESHOLD_ = (75, 91, -107, -59, 61, 88)
YELLOW_THRESHOLD_ = (75, 91, -24, 18, 56, 88)
RED_THRESHOLD_ = (43, 65, 62, 83, 51, 74)

# I/O init
valid_pin = Pin('P5', Pin.OUT_PP, Pin.PULL_DOWN)    # 数据输出有效IO
signal_pin = Pin('P6', Pin.OUT_PP, Pin.PULL_DOWN)   # 数据输出IO
valid_pin.low()     # 定义高电平为数据有效
signal_pin.low()    # 定义高电平为绿灯、低电平为红灯

# Timer callback
def Tim14Callback(timer):   # LED工作指示
    pass
    #green_led.toggle()

# Timer init
tim14 = Timer(14, freq = 2)
tim14.callback(Tim14Callback)

# Sensor init
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)

# Clock init
clock = time.clock()

def trafficColorGet(img, c, color_threshold):
    rec_area = ( c.x()-c.r(), c.y()-c.r(), 2*c.r(), 2*c.r() )
    x_stride = y_stride = c.r()-10
    area_threshold = (int)(PI_*c.r()*c.r()*0.25)
    return img.find_blobs([color_threshold],
        roi = rec_area,
        x_stride = x_stride, y_stride = y_stride,
        area_threshold = area_threshold,
        pixels_threshold = 10, merge = False)

def trafficLightFind(img):
    circles = img.find_circles(threshold = 5250,
        x_margin = 10, y_margin = 10, r_margin = 10,
        r_min = 10, r_max = 40, r_step = 5)
    for c in circles:
        rec_area = ( c.x()-c.r(), c.y()-c.r(), 2*c.r(), 2*c.r() )
        #img.draw_rectangle(rec_area, color = (255, 0, 0), thickness = 1)

        blobs = trafficColorGet(img, c, RED_THRESHOLD_)
        for blo in blobs:
            img.draw_rectangle(blo.rect())

while(True):
    clock.tick()
    img = sensor.snapshot()
    trafficLightFind(img)
    print(clock.fps())
