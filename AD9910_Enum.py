from enum import Enum, unique


@unique
class INSTR(Enum):
    CFR1 = 0x00
    CFR2 = 0x01
    CFR3 = 0x02
    AuxDAC = 0x03
    IOUpdate = 0x04
    FTW = 0x07
    POW = 0x08
    ASF = 0x09
    MultiSync = 0x0A
    DigitalRampLimit = 0x0B
    DigitalRampStepSize = 0x0C
    DigitalRampRate = 0x0D
    Profile0 = 0x0E
    Profile1 = 0x0F
    Profile2 = 0x10
    Profile3 = 0x11
    Profile4 = 0x12
    Profile5 = 0x13
    Profile6 = 0x14
    Profile7 = 0x15
    RAM = 0x16

    @property
    def read(self) -> int:
        return 0x80 | self.value

    @property
    def write(self) -> int:
        return self.value


@unique
class RPD(Enum):
    # RAM_Playback_Destination
    Frequency = 0b00
    Phase = 0b01
    Amplitude = 0b10
    Polar = 0b11


@unique
class RIPCM(Enum):
    # RAM Internal Profile Control Modes
    # 0b0000    Internal    profile control disabled.
    # 0b0001    Burst       Execute Profile 0, then Profile 1, then halt.
    # 0b0010    Burst       Execute Profile 0 to Profile 2, then halt.
    # 0b0011    Burst       Execute Profile 0 to Profile 3, then halt.
    # 0b0100    Burst       Execute Profile 0 to Profile 4, then halt.
    # 0b0101    Burst       Execute Profile 0 to Profile 5, then halt.
    # 0b0110    Burst       Execute Profile 0 to Profile 6, then halt.
    # 0b0111    Burst       Execute Profile 0 to Profile 7, then halt.
    # 0b1000    Continuous  Execute Profile 0 to Profile 1, continuously.
    # 0b1001    Continuous  Execute Profile 0 to Profile 2, continuously.
    # 0b1010    Continuous  Execute Profile 0 to Profile 3, continuously.
    # 0b1011    Continuous  Execute Profile 0 to Profile 4, continuously.
    # 0b1100    Continuous  Execute Profile 0 to Profile 5, continuously.
    # 0b1101    Continuous  Execute Profile 0 to Profile 6, continuously.
    # 0b1110    Continuous  Execute Profile 0 to Profile 7, continuously.
    # 0b1111    Invalid.
    disable = 0b0000
    Burst_0_to_1_halt = 0b0001
    Burst_0_to_2_halt = 0b0010
    Burst_0_to_3_halt = 0b0011
    Burst_0_to_4_halt = 0b0100
    Burst_0_to_5_halt = 0b0101
    Burst_0_to_6_halt = 0b0110
    Burst_0_to_7_halt = 0b0111
    Conti_0_to_1_cont = 0b1000
    Conti_0_to_2_cont = 0b1001
    Conti_0_to_3_cont = 0b1010
    Conti_0_to_4_cont = 0b1011
    Conti_0_to_5_cont = 0b1100
    Conti_0_to_6_cont = 0b1101
    Conti_0_to_7_cont = 0b1110
    Invalid = 0b1111


@unique
class DRD(Enum):
    # Digital_Ramp_Destination_Bits(CFR2[21:20])    DDS_SignalControl_Parameter   Bits_Assigned_to_DDSParameter
    #               0b00                                    Frequency                   31:0
    #               0b01                                    Phase                       31:16
    #               0b1x                                    Amplitude                   31:18
    Frequency = 0b00
    Phase = 0b01
    Amplitude = 0b10


@unique
class IOURC(Enum):
    # 00 = divide-by-1 (default).
    # 01 = divide-by-2.
    # 10 = divide-by-4.
    # 11 = divide-by-8.
    # f_IO_update=f_sysCLK(2^(A+2)B)
    # A is the value of the 2-bit word comprising the I/O update rate control bits.
    # B is the value of the 32-bit word stored in the I/O update rate register.
    one = 0b00
    two = 0b01
    four = 0b10
    eight = 0b11


@unique
class DRV0(Enum):
    # DRV0 Bits (CFR3[29:28])     REFCLK_OUT Buffer
    #     0b00                    Disabled (tristate)
    #     0b01                    Low output current
    #     0b10                    Medium output current
    #     0b11                    High output current
    disable = 0b00
    low = 0b01
    medium = 0b10
    high = 0b11


@unique
class VCO(Enum):
    # VCO_SEL_Bits_(CFR3[26:24])          VCO_Range     frequency
    #     0b000                            VCO0          400-460
    #     0b001                            VCO1          455-530
    #     0b010                            VCO2          530-615
    #     0b011                            VCO3          650-790
    #     0b100                            VCO4          760-875
    #     0b101                            VCO5          920-1030
    #     0b110                         PLL_bypassed
    #     0b111                         PLL_bypassed
    # zero = 0b000
    _400_460_MHZ = 0b000
    # one = 0b001
    _455_530_MHZ = 0b001
    # two = 0b010
    _530_615_MHZ = 0b010
    # three = 0b011
    _650_790_MHZ = 0b011
    # four = 0b100
    _760_875_MHZ = 0b100
    # five = 0b0101
    _920_1030_MHZ = 0b0101
    PLL_bypassed = 0b111


@unique
class PLL_CPC(Enum):
    # PLL Charge Pump Current
    # ICP_Bits_(CFR3[21:19]) Charge_Pump_Current,I_cp(μA)
    #         0b000               212
    #         0b001               237
    #         0b010               262
    #         0b011               287
    #         0b100               312
    #         0b101               337
    #         0b110               363
    #         0b111               387
    _212_uA = 0b000
    _237_uA = 0b001
    _262_uA = 0b010
    _287_uA = 0b011
    _312_uA = 0b100
    _337_uA = 0b101
    _363_uA = 0b110
    _387_uA = 0b111


@unique
class Icp(Enum):
    _212_uA = 0b000
    _237_uA = 0b001
    _262_uA = 0b010
    _287_uA = 0b011
    _312_uA = 0b100
    _337_uA = 0b101
    _363_uA = 0b110
    _387_uA = 0b111

@unique
class OSK_SS(Enum):
    # OSK Amplitude Step Size
    one = 0b00
    two = 0b01
    four = 0b10
    eight = 0b11
    
    
@unique
class RAM_MC(Enum):
    # RAM_Profile_Mode_Control_Bits         RAM_Operating_Mode
    #     0b000, 101, 110, 111                 Direct switch
    #     0b001                                Ramp-up
    #     0b010                               Bidirectional ramp
    #     0b011                             Continuous bidirectional ramp
    #     0b100                                Continuous recirculate
    DirectSwitch = 0b000
    RampUp = 0b001
    BidirectionalRamp = 0b010
    ContinuousBidirectionalRamp = 0b011
    ContinuousRecirculate = 0b100