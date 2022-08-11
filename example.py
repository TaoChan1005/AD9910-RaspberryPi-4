#!/usr/bin/python
from AD9910 import *


OSK = 4
PWR = 5
RST = 6
PF0 = 17
PF1 = 27
PF2 = 22
IOP = 18

ad9910 = AD9910(PWR=PWR, RST=RST, PF0=PF0, PF1=PF1, PF2=PF2, OSK=OSK, IO_update=IOP, dev=0, bus=0, spi_speed=Speed._62_5_MHz)
ad9910.crf_init()
phase = pi*1.5
fpa = ad9910.output_sigel_tone(freq=122.2, amp=100, phase=phase)

fpa = [round(i, 3) for i in fpa]
print("freq={f}Hz\tphase={p}pi\tamplitude={a}%".format(f=fpa[0], p=round(fpa[1]/pi, 4), a=fpa[2]))
