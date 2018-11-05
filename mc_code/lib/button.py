from time import sleep_ms, ticks_ms, ticks_diff
from machine import Pin
from _thread import start_new_thread
import gc

class Button:

  def __init__(self, pid='P10', longms=1000):
    self.pressms = 0
    self.longms = longms
    self.pin = Pin(pid, mode=Pin.IN, pull=Pin.PULL_UP)
    self.pin.callback(Pin.IRQ_FALLING | Pin.IRQ_RISING, self.press)

  def long(self):
    pass

  def short(self):
    pass

  def press(self, pin):
    # If never pressed, store press time
    if self.pressms == 0: self.pressms = ticks_ms()
    else:
      # If pressed within 500 ms of first press, discard (button bounce)
      if ticks_diff(self.pressms, ticks_ms()) < 500: return

    # Wait for value to stabilize for 10 ms
    i = 0
    while i < 10:
      sleep_ms(1)
      if self.pin() == 1: i = 0
      else: i+=1

    # Measure button press duration
    while self.pin() == 0:
      i+=1
      if(i > self.longms): break
      sleep_ms(1)

    # Trigger short or long press
    if(i > self.longms):
      start_new_thread(self.long, ())
    else:
      start_new_thread(self.short, ())

    # Wait for button release
    while self.pin() == 0: pass
    self.pressms = 0
    gc.collect()
