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
f0 = 100
# fpa = ad9910.output_single_tone(freq=f0, amp=100, phase=phase)

# fpa = [round(i, 3) for i in fpa]
# print("freq={f}Hz\tphase={p}pi\tamplitude={a}%".format(f=fpa[0], p=round(fpa[1]/pi, 4), a=fpa[2]))

lower = f0
lower = 1
upper = 10*K
dt = 4*nano*50000
df = 0.2
# sleep(5)
# asf=ASF(amp_100=100,dt=0)
# ad9910.send_data(asf.generate())6
# ad9910.send_data([INSTR.AuxDAC.value,0x00, 0x00, 0x00, 0x7F])
ad9910.set_amplitute(100)
sweep_info = ad9910.output_sweep_freq(lower=lower, upper=upper, dt=dt, df=df)
dt = round(sweep_info[2]/u, 3)
sweep_info = [round(i, 3) for i in sweep_info]
print("lower={l}Hz\tupper={u}Hz\tdt={t}us\tdf={d}Hz\tspeed={s}Hz/s".format(l=sweep_info[0], u=sweep_info[1], t=dt, d=sweep_info[3],s=sweep_info[4]))
