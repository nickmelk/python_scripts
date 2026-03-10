## SOME FUNCTION FOR DECIMAL-BINARY CONVERSIONS ##
from fractions import Fraction

class FloatingPointFormat:
    def __init__(self, bias, exponent, fraction):
        self.bias = bias
        self.exponent = exponent
        self.fraction = fraction

float16 = FloatingPointError(15, 5, 10)             # Half-precision
float32 = FloatingPointFormat(127, 8, 23)           # Single-precision
float64 = FloatingPointFormat(1023, 11, 52)         # Double-precision
float128 = FloatingPointFormat(16383, 15, 112)      # Quadruple-precision
float256 = FloatingPointFormat(262143, 19, 236)     # Octuple-precision
x86 = FloatingPointFormat(16383, 15, 64)            # x86 extended-precision

def dec_int_to_bin(number_dec: int) -> str:
    number_bin = ""
    if number_dec == 0:
        number_bin = "0"
    while number_dec > 0:
        number_bin = str(number_dec%2) + number_bin
        number_dec //= 2
    return number_bin

def bin_to_dec_int(number_bin: str) -> int:
    number_dec = 0
    for index, bit in enumerate(number_bin[::-1]):
        number_dec += int(bit) * 2**index
    return number_dec

def bin_ieee_754_to_dec(number_bin: str, format: FloatingPointFormat = float32) -> float:
    sign = int(number_bin[0])
    exponent = number_bin[1:format.exponent+1]
    fraction = number_bin[format.exponent+1:]
    
    if exponent == '1'*format.exponent:
        if fraction == '0'*format.fraction:
            return (-1)**sign * float("inf")
        else:
            return float("nan")

    exponent_dec = bin_to_dec_int(exponent) - format.bias
    fraction_dec = Fraction(0)
    for index, bit in enumerate(fraction):
        fraction_dec += Fraction(bit) * Fraction(1, 2**(index+1))

    if exponent == '0'*format.exponent:
        if fraction == '0'*format.fraction:
            return (-1)**sign * 0.0
        else:
            return (-1)**sign * 2**(1-format.bias) * fraction_dec
    
    number_dec = (-1)**sign * Fraction(2)**(exponent_dec) * (1+fraction_dec)
    
    return number_dec

# this function needs some refactoring
def dec_to_bin_ieee_754(number: str, format: FloatingPointFormat = float32) -> str:
    sign = '0' if not '-' in number else '1'
    
    if '-' in number:
        number = number.replace('-', '')

    if number == "0.0":
        number_bin = sign + '0'*format.exponent + '0'*format.fraction
        return number_bin
    elif number == "inf":
        number_bin = sign + '1'*format.exponent + '0'*format.fraction
        return number_bin
    elif number == "nan":
        number_bin = sign + '1'*format.exponent + '1' + '0'*(format.fraction-1)
        return number_bin

    number = Fraction(number)
    integer_part = number.numerator // number.denominator
    integer_bin = dec_int_to_bin(integer_part)

    fractional_part = number - integer_part
    fractional_bin = ''
    for _ in range(format.fraction+3):
        fractional_part *= 2
        bit = int(fractional_part)
        fractional_bin += str(bit)
        fractional_part -= bit

    binary_number = integer_bin + '.' + fractional_bin

    one_app, was_seen = 0, False
    point_app = 1
    for index, bit in enumerate(binary_number):
        if bit == '1' and not was_seen:
            one_app = index
            was_seen = True
        if bit == '.':
            point_app = index

    exponent = point_app - one_app - 1
    exponent += format.bias
    exponent_bin = dec_int_to_bin(exponent)

    binary_number = binary_number.replace('.', '')
    if exponent-format.bias >= 0:
        binary_number = binary_number[one_app+1:]
    else:
        binary_number = binary_number[one_app:]         # When point is removed indeces get shifted and one_app becomes index which is +1 from first 1 bit
    while len(binary_number) < format.fraction+3:
        fractional_part *= 2
        bit = int(fractional_part)
        binary_number += str(bit)
        fractional_part -= bit
    if len(binary_number) > format.fraction:
        # If grs > 100 round up
        # If grs < 100 truncate
        # If grs = 100 take LSB if it is 1 round up, otherwise truncate (i.e. round ties to even) 
        grs = binary_number[format.fraction:format.fraction+3]
        binary_number = binary_number[:format.fraction]
        if int(grs) > 100 or (int(grs) == 100 and binary_number[-1] == '1'):
            binary_number = int(binary_number, base=2) + 1
            binary_number = dec_int_to_bin(binary_number)

    exponent_bin = '0'*(format.exponent-len(exponent_bin)) + exponent_bin
    binary_number = binary_number + '0'*(format.fraction-len(binary_number))

    number_bin = sign + exponent_bin + binary_number

    return number_bin

number = "123456789.0"
bin = dec_to_bin_ieee_754(number, float32)
print(bin)
print(len(bin))
import sys
sys.set_int_max_str_digits(10000)
dec = bin_ieee_754_to_dec("0"+"000000000000001"+"0"*64, x86)
print(f"{dec:e}")

# Test this thing with numpy floating points
import numpy as np
val_32 = np.float32(number)
print(val_32)
