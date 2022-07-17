# By: EnderMandS - 周日 7月 17 2022

import sensor, image, time
from pyb import LED, Timer, Pin

# Const define
RED_ = 0
GREEN_ = 1

# Board LED init
red_led     = LED(1)
green_led   = LED(2)
blue_led    = LED(3)
ir_leds     = LED(4)

# I/O init
valid_pin = Pin('P5', Pin.OUT_PP, Pin.PULL_DOWN)    # 数据输出有效IO
signal_pin = Pin('P6', Pin.OUT_PP, Pin.PULL_DOWN)   # 数据输出IO
valid_pin.low()     # 定义高电平为数据有效
signal_pin.low()    # 定义高电平为绿灯、低电平为红灯

# Timer callback
def Tim14Callback(timer):   # LED工作指示
    green_led.toggle()

# Timer init
tim14 = Timer(14, freq = 2)
tim14.callback(Tim14Callback)

# Sensor init
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)

# Clock init
clock = time.clock()

while(True):
    clock.tick()
    img = sensor.snapshot()
    print(clock.fps())
