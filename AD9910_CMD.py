
from tokenize import Triple
from AD9910_Enum import *
from math import pi, modf
from typing import List, Tuple
from abc import abstractclassmethod


def cal_n_bits_max(n: int) -> int:
    return (1 << n)-1


K = 1000
M = 1000*K
G = 1000*M
m = 0.001
u = 0.001*m
nano = 0.001*u

TWO_PI = 2*pi

MAX_32_BIT = cal_n_bits_max(32)
MAX_16_BIT = cal_n_bits_max(16)
MAX_14_BIT = cal_n_bits_max(14)
FULL_FTW = MAX_32_BIT
FULL_POW = MAX_16_BIT
FULL_ASF = MAX_14_BIT
MAX_FTW = FULL_FTW >> 1

DT_4_1G = 0.000000004


def check_list(input_list: list, element_type=int) -> bool:
    if input_list is not None and isinstance(input_list, list):
        if len(input_list) == 0:
            return True
        if isinstance(input_list[0], element_type):
            return True
    return False


def get_int_low_8(data: int = 0) -> int:
    if isinstance(data, int):
        return data & 0xff
    return 0


def get_int_low_32(data: int = 0) -> int:
    if isinstance(data, int):
        return data & 0xffffffff
    return 0


def combine_binary(rawdata: int, add_data: int, index: int, size: int = 1) -> int:
    if isinstance(add_data, bool):
        add_data = int(add_data)
    elif isinstance(add_data, Enum):
        add_data = add_data.value
    data = (add_data & (2**size-1)) << index
    # print(bin(data))
    return rawdata | data


class TRANS:

    @classmethod
    def __force_into_range(cls, value: float, lower: float, upper: float) -> float:
        if value < lower:
            return lower
        elif value > upper:
            return upper
        return value

    @classmethod
    def SCALE_TO_WORD(cls, value: float, full_range: float, FULL_WORD: int, MAX_WORD: int = MAX_32_BIT, MIN_WORD: int = 0) -> int:
        tmp = int(value/full_range*FULL_WORD)
        return cls.__force_into_range(value=tmp, lower=MIN_WORD, upper=MAX_WORD)

    @classmethod
    def SCALE_FROM_WORD(cls, WORD: float, full_range: float, FULL_WORD: int, MAX_WORD: int = MAX_32_BIT, MIN_WORD: int = 0) -> float:
        WORD = cls.__force_into_range(value=WORD, lower=MIN_WORD, upper=MAX_WORD)
        return WORD/FULL_WORD*full_range

    @classmethod
    def MODIFY_BY_WORD(cls, value: float, full_range: float, FULL_WORD: int, MAX_WORD: int = MAX_32_BIT, MIN_WORD: int = 0) -> float:
        WORD = cls.SCALE_TO_WORD(value=value, full_range=full_range, FULL_WORD=FULL_WORD, MAX_WORD=MAX_WORD, MIN_WORD=MIN_WORD)
        return cls.SCALE_FROM_WORD(WORD=WORD, full_range=full_range, FULL_WORD=FULL_WORD, MAX_WORD=MAX_WORD, MIN_WORD=MIN_WORD)

    @classmethod
    def freq_2_FTW(cls, freq: float, SYSCLK: int = 1*G) -> int:
        WORD = cls.SCALE_TO_WORD(value=freq, full_range=SYSCLK, FULL_WORD=FULL_FTW, MAX_WORD=MAX_FTW, MIN_WORD=1)
        if WORD < 1:
            return 1
        return WORD

    @classmethod
    def FTW_2_freq(cls, FTW: int, SYSCLK: int = 1*G) -> float:
        return cls.SCALE_FROM_WORD(WORD=FTW, full_range=SYSCLK, FULL_WORD=FULL_FTW, MAX_WORD=MAX_FTW, MIN_WORD=1)

    @classmethod
    def freq_modify(cls, freq: float, SYSCLK: int = 1*G) -> float:
        return cls.MODIFY_BY_WORD(value=freq, full_range=SYSCLK, FULL_WORD=FULL_FTW, MAX_WORD=MAX_FTW, MIN_WORD=1)

    @classmethod
    def phase_2_POW(cls, phase_pi: float) -> int:
        phase_pi = TWO_PI*(modf(phase_pi/TWO_PI)[0])
        return cls.SCALE_TO_WORD(value=phase_pi, full_range=TWO_PI, FULL_WORD=FULL_POW, MAX_WORD=FULL_POW, MIN_WORD=0)

    @classmethod
    def phase_2_POW_degree(cls, phase_degree: float) -> int:
        phase_degree = 360*(modf(phase_degree/360)[0])
        return cls.SCALE_TO_WORD(value=phase_degree, full_range=360, FULL_WORD=FULL_POW, MAX_WORD=FULL_POW, MIN_WORD=0)

    @classmethod
    def POW_2_phase(cls, POW: int) -> float:
        return cls.SCALE_FROM_WORD(WORD=POW, full_range=TWO_PI, FULL_WORD=FULL_POW, MAX_WORD=FULL_POW, MIN_WORD=0)

    @classmethod
    def phase_modify(cls, phase_pi) -> float:
        return cls.MODIFY_BY_WORD(value=phase_pi, full_range=TWO_PI, FULL_WORD=FULL_POW, MAX_WORD=FULL_POW, MIN_WORD=0)

    @classmethod
    def amp_2_ASF(cls, amp_100: float) -> int:
        return cls.SCALE_TO_WORD(value=amp_100, full_range=100, FULL_WORD=FULL_ASF, MAX_WORD=FULL_ASF, MIN_WORD=0)

    @classmethod
    def ASF_2_amp(cls, ASF: int) -> int:
        return cls.SCALE_FROM_WORD(WORD=ASF, full_range=100, FULL_WORD=FULL_ASF, MAX_WORD=FULL_ASF, MIN_WORD=0)

    @classmethod
    def amp_modify(cls, amp_100: float) -> float:
        return cls.MODIFY_BY_WORD(value=amp_100, full_range=100, FULL_WORD=FULL_ASF, MAX_WORD=FULL_ASF, MIN_WORD=0)

    @classmethod
    def time_2_clk(cls, time: float, SYSCLK: int = 1*G, MAX_CLK: int = MAX_32_BIT) -> int:
        tmp = int(time*SYSCLK)
        return cls.__force_into_range(value=tmp, lower=0, upper=MAX_CLK)

    @classmethod
    def clk_2_time(cls, clk: int, SYSCLK: int = 1*G, MAX_CLK: int = MAX_32_BIT) -> float:
        clk = cls.__force_into_range(value=clk, lower=0, upper=MAX_CLK)
        return clk/SYSCLK

    @classmethod
    def time_modify(cls, time: float, SYSCLK: int = 1*G, MAX_CLK: int = MAX_32_BIT) -> float:
        clk = cls.time_2_clk(time=time, SYSCLK=SYSCLK, MAX_CLK=MAX_CLK)
        return cls.clk_2_time(clk=clk, SYSCLK=SYSCLK, MAX_CLK=MAX_CLK)

    # @classmethod
    # def dt_2_nclk(cls, dt, n_clk: int = 4, SYSCLK: int = 1*G) -> int:
    #     # each n clk as one NEW_CLK
    #     return int(dt*SYSCLK/n_clk)

    # @classmethod
    # def dt_2_clk(cls, dt: float, SYSCLK: int = 1*G) -> int:
    #     return cls.dt_2_nclk(dt=dt, n_clk=1, SYSCLK=SYSCLK)

    # @classmethod
    # def dt_2_4clk(cls, dt: float, SYSCLK: int = 1*G) -> int:
    #     # each 4 clk as one NEW_CLK
    #     return cls.dt_2_nclk(dt=dt, n_clk=4, SYSCLK=SYSCLK)

    # @classmethod
    # def nclk_2_dt(cls, clk: int, n_clk: int = 4, SYSCLK: int = 1*G) -> float:
    #     return clk/SYSCLK*n_clk

    # @classmethod
    # def clk_2_dt(cls, clk: int, SYSCLK: int = 1*G) -> float:
    #     return cls.nclk_2_dt(clk=clk, n_clk=1, SYSCLK=SYSCLK)

    # @classmethod
    # def four_clk_2_dt(cls, clk: int, SYSCLK: int = 1*G) -> float:
    #     return cls.nclk_2_dt(clk=clk, n_clk=4, SYSCLK=SYSCLK)

    # @classmethod
    # def dt_4_clk(cls, SYSCLK: int = 1*G) -> float:
    #     return cls.clk_2_dt(clk=4, SYSCLK=SYSCLK)

    # @classmethod
    # def dt_n_modify(cls, dt: float, n_clk: int, max_time_clk=0xffff, SYSCLK: int = 1*G) -> float:
    #     SYSCLK = int(SYSCLK/n_clk)
    #     CLK = cls.dt_2_clk(dt=dt, SYSCLK=SYSCLK)
    #     CLK = cls.__force_max(CLK, max_time_clk)
    #     return cls.clk_2_dt(clk=CLK, SYSCLK=SYSCLK)

    # @classmethod
    # def dt_4_modify(cls, dt: float, max_time_clk=0xffff, SYSCLK: int = 1*G) -> float:
    #     return cls.dt_n_modify(dt=dt, n_clk=4, max_time_clk=max_time_clk, SYSCLK=SYSCLK)


class _cmd:
    def __init__(self, instr: INSTR, bits: int, data: int = 0) -> None:
        self.__instr = instr
        # if not check_list(data, int):
        #     data: List[int] = []
        self.data = data
        if bits < 0:
            bits = 0
        self.__bits: int = bits
        self.MSB: bool = True

    @property
    def instr(self) -> INSTR:
        return self.__instr

    @property
    def instr_value(self) -> INSTR:
        return self.instr.value

    @property
    def bits_size(self) -> int:
        return self.__bits

    @property
    def bytes_size(self) -> int:
        return int(self.bits_size/8)

    def __data_to_8bit_list(self, MSB: bool = None) -> List[int]:
        data_list: List[int] = []
        for i in range(self.bytes_size):
            tmp = (self.data >> (i*8)) & 0xff
            data_list.append(tmp)
        if MSB is None:
            MSB = self.MSB
        if MSB:
            return list(reversed(data_list))
        else:
            return data_list

    def generate(self, MSB: bool = None) -> List[int]:
        self.build_data()
        # print(hex(self.data))
        data = self.__data_to_8bit_list(MSB=MSB)
        cmd: List[int] = [self.instr_value]+data
        # if MSB is None:
        #     MSB = self.MSB
        # if MSB:
        #     cmd: List[int] = [self.instr_value]+data
        # else:
        #     cmd: List[int] = [self.instr_value]+list(reversed(data))
        # print([self.instr.name]+[bin(i) for i in cmd])
        print("INSTR:\t", self.instr.name+",", "\t\tDATA:\t", [hex(i) for i in cmd])
        return cmd

    @abstractclassmethod
    def build_data(self) -> None:
        pass

    # def send_CMD(self) -> None:
    #     data = self.generate()
    #     self.send_data(data)


class _cmd_clk(_cmd):
    def __init__(self, instr: INSTR, bits: int, SYSCLK: int = 1*G) -> None:
        super().__init__(instr=instr, bits=bits)
        self.__SYSCLK: int = 0
        self.SYSCLK = SYSCLK

    @property
    def SYSCLK(self) -> int:
        return self.__SYSCLK

    @SYSCLK.setter
    def SYSCLK(self, clk: int) -> None:
        if not isinstance(clk, int) or clk <= 0:
            clk = 1*G
        self.__SYSCLK = clk


class _cmd_4_clk(_cmd):
    def __init__(self, instr: INSTR, bits: int, SYSCLK: int = 1*G) -> None:
        super().__init__(instr=instr, bits=bits)
        self.__SYSCLK: int = 0
        self.SYSCLK = SYSCLK

    @property
    def SYSCLK_MODIFY(self) -> int:
        return self.__SYSCLK

    @property
    def SYSCLK(self) -> int:
        return self.__SYSCLK << 2

    @SYSCLK.setter
    def SYSCLK(self, SYSCLK: int) -> None:
        self.__SYSCLK = SYSCLK >> 2


class CRF1(_cmd):
    def __init__(self) -> None:
        super().__init__(instr=INSTR.CFR1, bits=32)
        self.RAM_enable: bool = False
        # 0 = disables RAM functionality (default).
        # 1 = enables RAM functionality (required for both load/retrieve and playback operation).
        self.RAM_playback_destination: RPD = RPD.Frequency
        # RAM playback destination
        self.manual_OSK_externa: bool = False
        # Ineffective unless CFR1[9:8] = 10b.
        # 0 = OSK pin inoperative (default).
        # 1 = OSK pin enabled for manual OSK control (see Output Shift Keying (OSK) section for details).
        self.inverse_sinc_filter: bool = False
        # 0 = inverse sinc filter bypassed (default).
        # 1 = inverse sinc filter active.
        self.internal_profile_control: RIPCM = RIPCM.disable
        # Ineffective unless CFR1[31] = 1.
        # These bits are effective without the need for an I/O update. Default is 0000b.
        self.select_DDS_sine_output: bool = False
        # 0 = cosine output of the DDS is selected (default).
        # 1 = sine output of the DDS is selected.
        self.load_LRR_IO_update: bool = False
        # Ineffective unless CFR2[19] = 1.
        # 0 = normal operation of the digital ramp timer (default).
        # 1 = digital ramp timer loaded any time I/O_UPDATE is asserted or a PROFILE[2:0] change occurs.
        self.load_ARR_IO_update: bool = False
        # Ineffective unless CFR1[9:8] = 11b.
        # 0 = normal operation of the OSK amplitude ramp rate timer (default).
        # 1 = OSK amplitude ramp rate timer reloaded anytime I/O_UPDATE is asserted or a PROFILE[2:0] change occurs.
        self.autoclear_digital_ramp_accumulator: bool = False
        # 0 = normal operation of the DRG accumulator (default).
        # 1 = the ramp accumulator is reset for one cycle of the DDS clock after
        # which the accumula-tor automatically resumes normal operation.
        # As long as this bit remains set, the ramp accumulator is momentarily reset
        # each time an I/O_UPDATE is asserted or a PROFILE[2:0] change occurs.
        # This bit is synchronized with either an I/O _UPDATE or a PROFILE[2:0] change
        # and the next rising edge of SYNC_CLK.
        self.autoclear_phase_accumulator: bool = False
        # 0 = normal operation of the DDS phase accumulator (default).
        # 1 = synchronously resets the DDS phase accumulator anytime I/O_UPDATE is asserted or a profile change occurs.
        self.clear_digital_ramp_accumulator: bool = False
        # 0 = normal operation of the DRG accumulator (default).
        # 1 = asynchronous, static reset of the DRG accumulator.
        # The ramp accumulator remains reset as long as this bit remains set.
        # This bit is synchronized with either an I/O_UPDATE or a PROFILE[2:0] change and the next rising edge of SYNC_CLK.
        self.clear_phase_accumulator: bool = False
        # 0 = normal operation of the DDS phase accumulator (default).
        # 1 = asynchronous, static reset of the DDS phase accumulator.
        self.OSK_enable: bool = False
        self.select_auto_OSK: bool = False
        # Ineffective unless CFR1[9] = 1.
        # 0 = manual OSK enabled (default).
        # 1 = automatic OSK enabled.
        self.digital_power_down: bool = False
        # This bit is effective without the need for an I/O update.
        # 0 = clock signals to the digital core are active (default).
        # 1 = clock signals to the digital core are disabled.
        self.DAC_power_down: bool = False
        # 0 = DAC clock signals and bias circuits are active (default).
        # 1 = DAC clock signals and bias circuits are disabled.
        self.REFCLK_input_power_down: bool = False
        # This bit is effective without the need for an I/O update.
        # 0 = REFCLK input circuits and PLL are active (default).
        # 1 = REFCLK input circuits and PLL are disabled.\
        self.auxiliary_DAC_power_down: bool = False
        # 0 = auxiliary DAC clock signals and bias circuits are active (default).
        # 1 = auxiliary DAC clock signals and bias circuits are disabled.
        self.external_power_down_control: bool = False
        # 0 = assertion of the EXT_PWR_DWN pin affects full power-down (default).
        # 1 = assertion of the EXT_PWR_DWN pin affects fast recovery power-down.
        self.SDIO_input_only: bool = False
        # 0 = configures the SDIO pin for bidirectional operation; 2-wire serial programming mode (default).
        # 1 = configures the serial data I/O pin (SDIO) as an input only pin; 3-wire serial programming mode.
        self.LSB_first: bool = False
        # 0 = configures the serial I/O port for MSB-first format (default).
        # 1 = configures the serial I/O port for LSB-first format.

    def build_data(self) -> None:
        data: int = 0
        data = combine_binary(rawdata=data, add_data=self.LSB_first, index=0, size=1)
        data = combine_binary(rawdata=data, add_data=self.SDIO_input_only, index=1, size=1)
        data = combine_binary(rawdata=data, add_data=self.external_power_down_control, index=3, size=1)
        data = combine_binary(rawdata=data, add_data=self.auxiliary_DAC_power_down, index=4, size=1)
        data = combine_binary(rawdata=data, add_data=self.REFCLK_input_power_down, index=5, size=1)
        data = combine_binary(rawdata=data, add_data=self.DAC_power_down, index=6, size=1)
        data = combine_binary(rawdata=data, add_data=self.digital_power_down, index=7, size=1)
        data = combine_binary(rawdata=data, add_data=self.select_auto_OSK, index=8, size=1)
        data = combine_binary(rawdata=data, add_data=self.OSK_enable, index=9, size=1)
        data = combine_binary(rawdata=data, add_data=self.load_ARR_IO_update, index=10, size=1)
        data = combine_binary(rawdata=data, add_data=self.clear_phase_accumulator, index=11, size=1)
        data = combine_binary(rawdata=data, add_data=self.clear_digital_ramp_accumulator, index=12, size=1)
        data = combine_binary(rawdata=data, add_data=self.autoclear_phase_accumulator, index=13, size=1)
        data = combine_binary(rawdata=data, add_data=self.autoclear_digital_ramp_accumulator, index=14, size=1)
        data = combine_binary(rawdata=data, add_data=self.load_LRR_IO_update, index=15, size=1)
        data = combine_binary(rawdata=data, add_data=self.select_DDS_sine_output, index=16, size=1)
        data = combine_binary(rawdata=data, add_data=self.internal_profile_control, index=17, size=4)
        data = combine_binary(rawdata=data, add_data=self.inverse_sinc_filter, index=22, size=1)
        data = combine_binary(rawdata=data, add_data=self.manual_OSK_externa, index=23, size=1)
        data = combine_binary(rawdata=data, add_data=self.RAM_playback_destination, index=29, size=2)
        data = combine_binary(rawdata=data, add_data=self.RAM_enable, index=31, size=1)
        self.data = data


class CRF2(_cmd):
    def __init__(self) -> None:
        super().__init__(instr=INSTR.CFR2, bits=32)
        self.enable_amplitude_scale_from_single_tone_profiles: bool = False
        # Ineffective if CFR2[19 ] = 1 or CFR1[31] = 1 or CFR1[9] = 1.
        # 0 = the amplitude scaler is bypassed and shut down for power conservation (default).
        # 1 = the amplitude is scaled by the ASF from the active profile.
        self.internal_IO_update_active: bool = False
        # This bit is effective without the need for an I/O update.
        # 0 = serial I/O programming is synchronized with the external assertion of the I/O_UPDATE pin, which is configured as an input pin (default).
        # 1 = serial I/O programming is synchronized with an internally generated I/O update signal
        # (the internally generated signal appears at the I/O_UPDATE pin, which is configured as an output pin).
        self.SYNC_CLK_enable: bool = True
        # 0 = the SYNC_CLK pin is disabled; static Logic 0 output.
        # 1 = the SYNC_CLK pin generates a clock signal at ¼ fSYSCLK; used for synchronization of the serial I/O port (default).
        self.digital_ramp_destination: DRD = DRD.Frequency
        self.digital_ramp_enable: bool = False
        # 0 = disables digital ramp generator functionality (default).
        # 1 = enables digital ramp generator functionality.
        self.digital_ramp_no_dwell_high: bool = False
        # See the Digital Ramp Generator (DRG) section for details.
        # 0 = disables no-dwell high functionality (default).
        # 1 = enables no-dwell high functionality
        self.digital_ramp_no_dwell_low: bool = False
        # See the Digital Ramp Generator (DRG) section for details.
        # 0 = disables no-dwell low functionality (default).
        # 1 = enables no-dwell low functionality
        self.read_effective_FTW: bool = False
        # 0 = a serial I/O port read operation of the FTW register reports the contents of the FTW register (default).
        # 1 = a serial I/O port read operation of the FTW register reports the actual 32-bit word appearing at the input to the DDS phase accumulator.
        self.IO_update_rate_control: IOURC = IOURC.one
        # Ineffective unless CFR2[23] = 1. Sets the prescale ratio of the divider that clocks the auto I/O
        self.PDCLK_enable: bool = True
        # 0 = the PDCLK pin is disabled and forced to a static Logic 0 state; the internal clock signal continues to operate and provide timing to the data assembler.
        # 1 = the internal PDCLK signal appears at the PDCLK pin (default).
        self.PDCLK_invert: bool = False
        # 0 = normal PDCLK polarity; Q-data associated with Logic 1, I-data with Logic 0 (default).
        # 1 = inverted PDCLK polarity.
        self.TxEnable_invert: bool = False
        # 0 = no inversion.
        # 1 = inversion.
        self.matched_latency_enable: bool = False
        # 0 = simultaneous application of amplitude, phase, and frequency changes to the DDS arrive at the output in the order listed (default).
        # 1 = simultaneous application of amplitude, phase, and frequency changes to the DDS arrive at the output simultaneously.
        self.data_assembler_hold_last_value: bool = False
        # Ineffective unless CFR2[4] = 1.
        # 0 = the data assembler of the parallel data port internally forces zeros on the data path and ignores the signals on the D[15:0] and F[1:0] pins while the TxENABLE pin is Logic 0 (default). This implies that the destination of the data at the parallel data port is amplitude when TxENABLE is Logic 0.
        # 1 = the data assembler of the parallel data port internally forces the last value received on the D[15:0] and F[1:0] pins while the TxENABLE pin is Logic 1.
        self.sync_timing_validation_disable: bool = True
        # 0 = enables the SYNC_SMP_ERR pin to indicate (active high) detection of a synchronization pulse sampling error.
        # 1 = the SYNC_SMP_ERR pin is forced to a static Logic 0 condition (default).
        self.parallel_data_port_enable: bool = False
        # See the Parallel Data Port Modulation Mode section for more details.
        # 0 = disables parallel data port modulation functionality (default).
        # 1 = enables parallel data port modulation functionality.
        self.FM_gain: int = 0b00
        # The FM gain word allows the user to apply a weighting factor to the 16-bit data-word.
        # In the default state (0), the 16-bit data-word and the 32-bit word in the FTW register are LSB aligned.
        # Each increment in the value of the FM gain word shifts the 16-bit data-word to the left relative to the 32-bit word in the FTW register,
        # increasing the influence of the 16-bit data-word on the frequency defined by the FTW register by a factor of two.
        # The FM gain word effectively controls the frequency range spanned by the data-word.

    def build_data(self) -> None:
        data: int = 0
        if self.FM_gain > 0b1111:
            self.FM_gain = 0b1111
        data = combine_binary(rawdata=data, add_data=self.FM_gain, index=0, size=4)
        data = combine_binary(rawdata=data, add_data=self.parallel_data_port_enable, index=4, size=1)
        data = combine_binary(rawdata=data, add_data=self.sync_timing_validation_disable, index=5, size=1)
        data = combine_binary(rawdata=data, add_data=self.data_assembler_hold_last_value, index=6, size=1)
        data = combine_binary(rawdata=data, add_data=self.matched_latency_enable, index=7, size=1)
        data = combine_binary(rawdata=data, add_data=self.TxEnable_invert, index=9, size=1)
        data = combine_binary(rawdata=data, add_data=self.PDCLK_invert, index=10, size=1)
        data = combine_binary(rawdata=data, add_data=self.PDCLK_enable, index=11, size=1)
        data = combine_binary(rawdata=data, add_data=self.IO_update_rate_control, index=14, size=2)
        data = combine_binary(rawdata=data, add_data=self.read_effective_FTW, index=16, size=1)
        data = combine_binary(rawdata=data, add_data=self.digital_ramp_no_dwell_low, index=17, size=1)
        data = combine_binary(rawdata=data, add_data=self.digital_ramp_no_dwell_high, index=18, size=1)
        data = combine_binary(rawdata=data, add_data=self.digital_ramp_enable, index=19, size=1)
        data = combine_binary(rawdata=data, add_data=self.digital_ramp_destination, index=20, size=2)
        data = combine_binary(rawdata=data, add_data=self.SYNC_CLK_enable, index=22, size=1)
        data = combine_binary(rawdata=data, add_data=self.internal_IO_update_active, index=23, size=1)
        data = combine_binary(rawdata=data, add_data=self.enable_amplitude_scale_from_single_tone_profiles, index=24, size=1)
        self.data = data


class CRF3(_cmd):
    def __init__(self) -> None:
        super().__init__(instr=INSTR.CFR3, bits=32)
        self.DRV0: DRV0 = DRV0.low
        # Controls the REFCLK_OUT pin; default is 01b.
        self.VCO_SEL = VCO.PLL_bypassed
        # Selects the frequency band of the REFCLK PLL VCO); default is 111b.
        self.I_cp: PLL_CPC = PLL_CPC._387_uA
        # Selects the charge pump current in the REFCLK PLL; default is 111b.
        self.REFCLK_input_divider_bypass: bool = False
        # 0 = input divider is selected (default).
        # 1 = input divider is bypassed.
        self.REFCLK_input_divider_ResetB: bool = True
        # 0 = input divider is reset.
        # 1 = input divider operates normally (default).
        self.PFD_reset: bool = False
        # 0 = normal operation (default).
        # 1 = phase detector disabled.
        self.PLL_enable: bool = False
        # 0 = REFCLK PLL bypassed (default).
        # 1 = REFCLK PLL enabled.
        self.N: int = 0
        # This 7-bit number is the divide modulus of the REFCLK PLL feedback divider; default is 0000000b.

    def build_data(self) -> None:
        data: int = 0
        if self.N > 0b1111111:
            self.N = 0b1111111
        data = combine_binary(rawdata=data, add_data=self.N, index=1, size=7)
        data = combine_binary(rawdata=data, add_data=self.PLL_enable, index=8, size=1)
        data = combine_binary(rawdata=data, add_data=self.PFD_reset, index=10, size=1)
        data = combine_binary(rawdata=data, add_data=self.REFCLK_input_divider_ResetB, index=14, size=1)
        data = combine_binary(rawdata=data, add_data=self.REFCLK_input_divider_bypass, index=15, size=1)
        data = combine_binary(rawdata=data, add_data=self.I_cp, index=19, size=3)
        data = combine_binary(rawdata=data, add_data=self.VCO_SEL, index=24, size=3)
        data = combine_binary(rawdata=data, add_data=self.DRV0, index=28, size=2)
        self.data = data


class AuxDAC(_cmd):
    def __init__(self) -> None:
        super().__init__(instr=INSTR.AuxDAC, bits=32)
        self.FSC: int = 127
        # I-out=(86.4/R_set)(1+CODE/96)

    def cal_I_out(self, R_set: float = 1000) -> float:
        if R_set <= 0:
            R_set = 1000
        return (1+self.FSC/96)*86.4/R_set

    def set_FSC_by_current(self, I_out: float, R_set: float) -> float:
        code = (((I_out*R_set)/86.4)-1)*96
        self.FSC = int(code)
        return self.cal_I_out(R_set=R_set)

    def build_data(self) -> None:
        data: int = 0
        data = combine_binary(rawdata=data, add_data=self.FSC, index=0, size=8)
        self.data = data


class IO_Update(_cmd):
    def __init__(self, IO_update_rate: int = MAX_32_BIT) -> None:
        super().__init__(instr=INSTR.IOUpdate, bits=32)
        self.IO_update_rate: int = IO_update_rate

    def build_data(self) -> None:
        data: int = 0
        if self.IO_update_rate > MAX_32_BIT:
            self.IO_update_rate = MAX_32_BIT
        data = combine_binary(rawdata=data, add_data=self.IO_update_rate, index=0, size=32)
        self.data = data


class FTW(_cmd_clk):
    def __init__(self, freq: float, SYSCLK: int = 1*G) -> None:
        super().__init__(instr=INSTR.FTW, bits=32)
        self.__freq: float = 0.0
        self.SYSCLK = SYSCLK
        self.freq = freq

    @property
    def frequency(self) -> float:
        return self.__freq

    @frequency.setter
    def frequency(self, freq: float) -> float:
        self.__freq == TRANS.freq_modify(freq=freq, SYSCLK=self.SYSCLK)

    @property
    def frequency_tuning_word(self) -> int:
        return TRANS.freq_2_FTW(freq=self.frequency, SYSCLK=self.SYSCLK)

    def build_data(self) -> None:
        data: int = 0
        data = combine_binary(rawdata=data, add_data=self.frequency_tuning_word, index=0, size=32)
        self.data = data


class POW(_cmd):
    def __init__(self, phase_pi: float) -> None:
        super().__init__(instr=INSTR.POW, bits=32)
        self.__phase: float = 0
        self.phase = phase_pi

    @property
    def phase(self) -> float:
        return self.__phase

    @phase.setter
    def phase(self, phase_pi: float) -> None:
        self.__phase = TRANS.phase_modify(phase_pi=phase_pi)

    @property
    def phase_offset_word(self) -> int:
        return TRANS.phase_2_POW(self.phase)

    def build_data(self) -> None:
        data: int = 0
        data = combine_binary(rawdata=data, add_data=self.phase_offset_word, index=0, size=16)
        self.data = data


class ASF(_cmd_4_clk):
    # Amplitude Scale Factor Register
    # dt=4M/SYSCLK
    # where M is the 16-bit number stored in the amplitude ramp rate (ARR) portion of the ASF register.
    # For example, if fSYSCLK =750 MHz and M = 23218 (0x5AB2), then Δt ≈ 123.8293 μs.
    def __init__(self, amp_100: float, dt: float, step_size: OSK_SS = OSK_SS.one, SYSCLK: int = 1*G) -> None:
        super().__init__(instr=INSTR.ASF, bits=32, SYSCLK=SYSCLK)
        self.__dt: float = 0.0
        self.__amp: float = 0.0
        self.dt = dt
        self.amp = amp_100
        self.step_size: OSK_SS = step_size

    @property
    def dt(self) -> float:
        return self.__dt

    @dt.setter
    def dt(self, dt: float) -> None:
        self.__dt = TRANS.time_modify(time=dt, SYSCLK=self.SYSCLK_MODIFY, MAX_CLK=MAX_16_BIT)

    @property
    def amp(self) -> float:
        return self.__amp

    @amp.setter
    def amp(self, amp_100: float) -> None:
        self.__amp = TRANS.amp_modify(amp_100=amp_100)

    @property
    def ramp_rate(self) -> int:
        return TRANS.time_2_clk(time=self.dt, SYSCLK=self.SYSCLK_MODIFY, MAX_CLK=MAX_16_BIT)

    @property
    def scale_factor(self) -> int:
        return TRANS.amp_2_ASF(self.amp)

    def build_data(self) -> None:
        data: int = 0
        data = combine_binary(rawdata=data, add_data=self.step_size, index=0, size=2)
        data = combine_binary(rawdata=data, add_data=self.scale_factor, index=2, size=14)
        data = combine_binary(rawdata=data, add_data=self.ramp_rate, index=16, size=16)
        self.data = data


class MultiSync(_cmd):
    # Multichip Sync Register
    def __init__(self) -> None:
        super().__init__(instr=INSTR.MultiSync, bits=32)
        self.sync_validation_delay: int = 0b0000
        # This 4-bit number sets the timing skew (in ~75ps increments) between SYSCLK
        # and the delayed SYNC_INx signal for the sync validation block in the sync receiver. Default is 0000b.
        self.sync_receiver_enable: bool = False
        # 0 = synchronization clock receiver disabled (default).
        # 1 = synchronization clock receiver enabled.
        self.sync_generator_enable: bool = False
        # 0 = synchronization clock generator disabled (default).
        # 1 = synchronization clock generator enabled.
        self.sync_generator_polarity: bool = False
        # 0 = synchronization clock generator coincident with the rising edge of SYSCLK (default).
        # 1 = synchronization clock generator coincident with the falling edge of SYSCLK.
        self.sync_state_preset_value: int = 0b000000
        # This 6-bit number is the state that the internal clock generator assumes when it receives a sync pulse. Default is 000000b.
        self.output_sync_generator: int = 0b00000
        # This 5-bit number sets the output delay (in ~75 ps increments) of the sync generator. Default is 00000b.
        self.input_sync_receiver_delay: int = 0b00000
        # This 5-bit number sets the input delay (in ~75 ps increments) of the sync receiver. Default is 00000b.

    def build_data(self) -> None:
        data: int = 0
        data = combine_binary(rawdata=data, add_data=self.input_sync_receiver_delay, index=3, size=5)
        data = combine_binary(rawdata=data, add_data=self.output_sync_generator, index=11, size=5)
        data = combine_binary(rawdata=data, add_data=self.sync_state_preset_value, index=18, size=6)
        data = combine_binary(rawdata=data, add_data=self.sync_generator_polarity, index=25, size=1)
        data = combine_binary(rawdata=data, add_data=self.sync_generator_enable, index=26, size=1)
        data = combine_binary(rawdata=data, add_data=self.sync_receiver_enable, index=27, size=1)
        data = combine_binary(rawdata=data, add_data=self.sync_validation_delay, index=28, size=4)
        self.data = data


class DigitalRampLimit(_cmd_clk):
    def __init__(self, freq_upper: float, freq_lower: float, SYSCLK: int = 1*G) -> None:
        super().__init__(instr=INSTR.DigitalRampLimit, bits=64)
        self.SYSCLK = SYSCLK
        self.__freq_upper: float = 0
        self.__freq_lower: float = 0
        self.freq_upper = freq_upper
        self.freq_lower = freq_lower

    @property
    def freq_upper(self) -> float:
        return self.__freq_upper

    @freq_upper.setter
    def freq_upper(self, freq: float) -> None:
        self.__freq_upper = TRANS.freq_modify(freq=freq, SYSCLK=self.SYSCLK)

    @property
    def freq_lower(self) -> float:
        return self.__freq_lower

    @freq_lower.setter
    def freq_lower(self, freq: float) -> None:
        self.__freq_lower = TRANS.freq_modify(freq=freq, SYSCLK=self.SYSCLK)

    @property
    def upper(self) -> int:
        return TRANS.freq_2_FTW(self.freq_upper, self.SYSCLK)

    @property
    def lower(self) -> int:
        return TRANS.freq_2_FTW(self.freq_lower, self.SYSCLK)

    def build_data(self) -> None:
        data: int = 0
        data = combine_binary(rawdata=data, add_data=self.lower, index=0, size=32)
        data = combine_binary(rawdata=data, add_data=self.upper, index=32, size=32)
        self.data = data


class DigitalRampStepSize(_cmd_clk):
    # Eight bytes are assigned to this register. This register is only effective if CFR2[19] = 1. See the Digital Ramp Generator (DRG) section for details.
    def __init__(self, dx_dec: float, dx_inc: float, ramp_dest: DRD = DRD.Frequency, SYSCLK: int = 1*G, out_max: float = 100.0) -> None:
        super().__init__(instr=INSTR.DigitalRampStepSize, bits=64)
        self.SYSCLK = SYSCLK
        self.out_max: float = out_max
        self.__dest: DRD = ramp_dest
        self.__dec: float = 0
        self.__inc: float = 0
        self.inc = dx_inc
        self.dec = dx_dec

    def GET_WORD(self, value: float) -> int:
        dest = self.dest
        if dest == DRD.Frequency:
            return TRANS.freq_2_FTW(freq=value, SYSCLK=self.SYSCLK)
        elif dest == DRD.Phase:
            return TRANS.phase_2_POW(phase_pi=value)
        elif dest == DRD.Amplitude:
            return TRANS.amp_2_ASF(amp_100=value)

    def SET_VALUE(self, value: float) -> float:
        dest = self.dest
        if dest == DRD.Frequency:
            return TRANS.freq_modify(freq=value, SYSCLK=self.SYSCLK)
        elif dest == DRD.Phase:
            return TRANS.phase_modify(phase_pi=value)
        elif dest == DRD.Amplitude:
            return TRANS.amp_modify(amp_100=value)

    @property
    def dest(self) -> DRD:
        return self.__dest

    @property
    def dec(self) -> float:
        return self.__dec

    @dec.setter
    def dec(self, dx: float) -> None:
        self.__dec = self.SET_VALUE(dx)

    @property
    def inc(self) -> float:
        return self.__inc

    @inc.setter
    def inc(self, dx: float) -> None:
        self.__inc = self.SET_VALUE(dx)

    @property
    def decrement(self) -> int:
        return self.GET_WORD(self.dec)

    @property
    def increment(self) -> int:
        return self.GET_WORD(self.inc)

    def build_data(self) -> None:
        data: int = 0
        data = combine_binary(rawdata=data, add_data=self.increment, index=0, size=32)
        data = combine_binary(rawdata=data, add_data=self.decrement, index=32, size=32)
        self.data = data


class DigitalRampRate(_cmd_4_clk):
    def __init__(self, dt_negative: float, dt_positive: float, SYSCLK: int = 1*G) -> None:
        super().__init__(instr=INSTR.DigitalRampRate, bits=32, SYSCLK=SYSCLK)
        self.__neg: float = 0.0
        self.__pos: float = 0.0
        self.SYSCLK = SYSCLK
        self.negative = dt_negative
        self.positive = dt_positive

    @property
    def negative(self) -> float:
        return self.__neg

    @negative.setter
    def negative(self, dt: float) -> None:
        self.__neg = TRANS.time_modify(time=dt, SYSCLK=self.SYSCLK_MODIFY, MAX_CLK=MAX_16_BIT)

    @property
    def positive(self) -> float:
        return self.__pos

    @positive.setter
    def positive(self, dt: float) -> None:
        self.__pos = TRANS.time_modify(time=dt, SYSCLK=self.SYSCLK_MODIFY, MAX_CLK=MAX_16_BIT)

    @property
    def negative_slope_rate(self) -> int:
        return TRANS.time_2_clk(time=self.negative, SYSCLK=self.SYSCLK_MODIFY, MAX_CLK=MAX_16_BIT)

    @property
    def positive_slope_rate(self) -> int:
        return TRANS.time_2_clk(time=self.positive, SYSCLK=self.SYSCLK_MODIFY, MAX_CLK=MAX_16_BIT)

    def build_data(self) -> None:
        data: int = 0
        data = combine_binary(rawdata=data, add_data=self.positive_slope_rate, index=0, size=16)
        data = combine_binary(rawdata=data, add_data=self.negative_slope_rate, index=16, size=16)
        self.data = data


class _profile(_cmd):
    def __init__(self, N: int = 0) -> None:
        if N > 8:
            N = 8
        elif N < 0:
            N = 0
        instr_value = INSTR.Profile0.value+N
        instr = INSTR(instr_value)
        super().__init__(instr=instr, bits=64)


class Profile_SingleTone(_profile, _cmd_clk):
    def __init__(self, freq: float, amp: float, phase: float = 0, N: int = 0, SYSCLK: int = 1*G) -> None:
        super().__init__(N)
        self.__freq: float = 0
        self.__amp: float = 0
        self.__phase: float = 0
        # self.__SYSCLK: int = 0
        self.SYSCLK = SYSCLK
        self.set_value(freq=freq, amp=amp, phase=phase)

    # @property
    # def SYSCLK(self) -> int:
    #     return self.__SYSCLK

    # @SYSCLK.setter
    # def SYSCLK(self, clk: int) -> None:
    #     if not isinstance(clk, int) or clk <= 0:
    #         clk = 1*G
    #     self.__SYSCLK = clk

    @property
    def fpa(self) -> Tuple[float, float, float]:
        return self.freq, self.phase, self.amp

    @property
    def freq(self) -> float:
        return self.__freq

    @freq.setter
    def freq(self, freq_value: float) -> None:
        self.__freq = TRANS.freq_modify(freq=freq_value, SYSCLK=self.SYSCLK)

    @property
    def amp(self) -> float:
        return self.__amp

    @amp.setter
    def amp(self, amp_value: float) -> None:
        self.__amp = TRANS.amp_modify(amp_100=amp_value)

    @property
    def phase(self) -> float:
        return self.__phase

    @property
    def amplitude_scale_factor(self) -> int:
        return TRANS.amp_2_ASF(self.amp)

    @property
    def phase_offset_word(self) -> int:
        return TRANS.phase_2_POW(self.phase)

    @property
    def frequency_tuning_word(self) -> int:
        return TRANS.freq_2_FTW(freq=self.freq, SYSCLK=self.SYSCLK)

    @phase.setter
    def phase(self, phase_value: float) -> None:
        self.__phase = TRANS.phase_modify(phase_pi=phase_value)

    def set_value(self, freq: float, amp: float, phase: float = 0) -> Tuple[float, float, float]:
        self.freq = freq
        self.amp = amp
        self.phase = phase
        return self.fpa

    def build_data(self) -> None:
        data: int = 0
        data = combine_binary(rawdata=data, add_data=self.frequency_tuning_word, index=0, size=32)
        data = combine_binary(rawdata=data, add_data=self.phase_offset_word, index=32, size=16)
        data = combine_binary(rawdata=data, add_data=self.amplitude_scale_factor, index=48, size=14)
        self.data = data


class Profile_RAM(_profile):
    def __init__(self, mode_control: RAM_MC.DirectSwitch, N: int = 0) -> None:
        super().__init__(N)
        self.address_step_rate: int = 0x0000
        self.waveform_end_address: int = 0x0000
        self.waveform_start_address: int = 0x0000
        self.no_dwell_high: bool = False
        # Effective only when the RAM mode is in ramp-up.
        # 0 = when the RAM state machine reaches the end address, it halts.
        # 1 = when the RAM state machines reaches the end address, it jumps to the start address and halts.
        self.zero_cross: bool = False
        # Effective only when in RAM mode, direct switch.
        # 0 = zero-crossing function disabled.
        # 1 = zero-crossing function enabled.
        self.RAM_mode_control: RAM_MC = mode_control

    def build_data(self) -> None:
        data: int = 0
        data = combine_binary(rawdata=data, add_data=self.RAM_mode_control, index=0, size=3)
        data = combine_binary(rawdata=data, add_data=self.zero_cross, index=3, size=1)
        data = combine_binary(rawdata=data, add_data=self.no_dwell_high, index=5, size=1)
        data = combine_binary(rawdata=data, add_data=self.waveform_start_address, index=14, size=10)
        data = combine_binary(rawdata=data, add_data=self.waveform_end_address, index=30, size=10)
        data = combine_binary(rawdata=data, add_data=self.address_step_rate, index=40, size=16)
        self.data = data


def copy_RAM_profile(profile: Profile_RAM, new_N: int) -> Profile_RAM:
    new_profile = Profile_RAM(new_N)
    if isinstance(profile, Profile_RAM):
        new_profile.RAM_mode_control = profile.RAM_mode_control
        new_profile.zero_cross = profile.zero_cross
        new_profile.no_dwell_high = profile.no_dwell_high
        new_profile.waveform_start_address = profile.waveform_start_address
        new_profile.waveform_end_address = profile.waveform_end_address
        new_profile.address_step_rate = profile.address_step_rate
    return new_profile


class RAM(_cmd):
    def __init__(self, data: List[int]) -> None:
        super().__init__(instr=INSTR.RAM, bits=32)
        self.data: List[int] = data

    def generate(self, MSB: bool = None) -> List[int]:
        data: List[int] = []
        for i in self.data:
            data.append(get_int_low_32(i))
        if MSB is None:
            MSB = self.MSB
        if MSB:
            cmd: List[int] = [self.instr_value]+data
        else:
            cmd: List[int] = [self.instr_value]+list(reversed(data))
        return cmd
