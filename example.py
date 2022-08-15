#!/usr/bin/python
from AD9910 import *


OSK = 24
PWR = 5
RST = 6
PF0 = 17
PF1 = 27
PF2 = 22
IOP = 18
DRC = 20
DRH = 21
DRO = 16

io = AD9910_IO(PWR=PWR, RST=RST, PF0=PF0, PF1=PF1, PF2=PF2, OSK=OSK, IOP=IOP)
io.DRG_config(DRC=DRC, DRH=DRH, DRO=DRO)

spi = AD9910_COM()

ad9910 = AD9910(IO=io, COM=spi)
ad9910.crf_init()
phase = pi*1.5
f0 = 255
# fpa = ad9910.output_single_tone(freq=f0, amp=100, phase=phase)

# fpa = [round(i, 3) for i in fpa]
# print("freq={f}Hz\tphase={p}pi\tamplitude={a}%".format(f=fpa[0], p=round(fpa[1]/pi, 4), a=fpa[2]))


dt = 4*nano*80000
df = 0.2

# sleep(5)
# asf=ASF(amp_100=100,dt=0)
# ad9910.send_data(asf.generate())
# ad9910.send_data([INSTR.AuxDAC.value,0x00, 0x00, 0x00, 0x7F])

# ===============TEST_SWEEP_FREQ=======================
# lower = 0
# upper = 4*K
# ad9910.output_single_tone(freq=lower, amp=100, phase=phase)
# ad9910.DRG_dwell(dwell_high=False, dwell_low=False, update=False)
# # sweep_info = ad9910.output_sweep_freq(lower=lower, upper=upper, dt=dt, df=df)
# sweep_info = ad9910.output_sweep_ctl_freq(lower=lower, upper=upper, dt=dt, df=df)
# dt = round(sweep_info[2]/u, 3)
# sweep_info = [round(i, 3) for i in sweep_info]
# print("lower={l}Hz\tupper={u}Hz\tdt={t}us\tdf={d}Hz\tspeed={s}Hz/s\ttime={time}s"
#       .format(l=sweep_info[0], u=sweep_info[1], t=dt, d=sweep_info[3], s=sweep_info[4], time=sweep_info[5]))
# ad9910.DRG_wait_finish()

# ===============TEST_SWEEP_AMP=======================

# ad9910.set_frequency(100)
# ad9910.DRG_dwell(dwell_high=False, dwell_low=False, update=False)
# sweep_info = ad9910.output_sweep_ctl_amp(lower=0, upper=100, dt=dt, da=0)
# dt = round(sweep_info[2]/u, 3)
# sweep_info = [round(i, 3) for i in sweep_info]
# print("lower={l}%\tupper={u}%\tdt={t}us\td_amp={d}%\tspeed={s}%/s\ttime={time}s"
#       .format(l=sweep_info[0], u=sweep_info[1], t=dt, d=sweep_info[3], s=sweep_info[4], time=sweep_info[5]))
# ad9910.DRG_wait_finish


# ==============TEST_pulse_trapezoid================================
# pulse = PULSE(init_freq=100, step_freq=0, end_freq=3*K, init_amp=50, end_amp=100, dt=dt, step_amp=0)
# print(pulse)
# pulse_new = ad9910.pulse_trapezoid(pulse=pulse)
# print(pulse_new)


# ==============OSK_TEST================================
# dt = 4*nano*60000
# fpa = ad9910.output_single_tone(freq=10, amp=0, phase=phase)
# fpa = [round(i, 3) for i in fpa]
# print("freq={f}Hz\tphase={p}pi\tamplitude={a}%".format(f=fpa[0], p=round(fpa[1]/pi, 4), a=fpa[2]))
# sweep_info = ad9910.output_sweep_amp_osk(max=100, dt=dt)
# dt = round(sweep_info[2]/u, 3)
# time = round(sweep_info[5]/1, 3)
# sweep_info = [round(i, 3) for i in sweep_info]
# print("lower={l}%\tupper={u}%\tdt={t}us\td_amp={d}%\tspeed={s}%/s\ttime={time}s"
#       .format(l=sweep_info[0], u=sweep_info[1], t=dt, d=sweep_info[3], s=sweep_info[4], time=time))
# sleep(time)
# ad9910.IO.OSK(False)

# ==============OSK_Pulse================================
# f0=1*K
# f1=3*K
# dt = 4*nano*60000
# fpa = ad9910.output_single_tone(freq=f0, amp=0, phase=phase)
# fpa = [round(i, 3) for i in fpa]
# print("freq={f}Hz\tphase={p}pi\tamplitude={a}%".format(f=fpa[0], p=round(fpa[1]/pi, 4), a=fpa[2]))
# sweep_info = ad9910.output_sweep_amp_osk(max=100, dt=dt)
# dt = round(sweep_info[2]/u, 3)
# time = round(sweep_info[5]/1, 3)
# sweep_info = [round(i, 3) for i in sweep_info]
# print("lower={l}%\tupper={u}%\tdt={t}us\td_amp={d}%\tspeed={s}%/s\ttime={time}s"
#       .format(l=sweep_info[0], u=sweep_info[1], t=dt, d=sweep_info[3], s=sweep_info[4], time=time))
# sleep(time+0.5)

# ad9910.DRG_dwell(dwell_high=False, dwell_low=False, update=False)

# sweep_info = ad9910.output_sweep_ctl_freq(lower=f0, upper=f1, dt=dt, df=df)
# dt = round(sweep_info[2]/u, 3)
# sweep_info = [round(i, 3) for i in sweep_info]
# print("lower={l}Hz\tupper={u}Hz\tdt={t}us\tdf={d}Hz\tspeed={s}Hz/s\ttime={time}s"
#       .format(l=sweep_info[0], u=sweep_info[1], t=dt, d=sweep_info[3], s=sweep_info[4], time=sweep_info[5]))
# ad9910.DRG_wait_finish()

# ad9910.IO.OSK(False)


# ==============pulse_trapezoid================================
f0 = 1*K
f1 = 3*K
dt_freq = 4*nano*60000
dt_amp = 4*nano*10000

pulse = PULSE(init_freq=f0, step_freq=0, dt_freq=dt_freq, end_freq=f1, end_amp=100,  dt_amp=dt_amp, step_amp=OSK_SS.four)
ad9910.output_single_tone(freq=pulse.init_freq, amp=0, phase=pulse.phase)
sleep(1)
# output the sigel tone whcih amp is zero and hold 1 second, this is just for the display
ad9910.pulse_trapezoid(pulse=pulse)
print(pulse)
