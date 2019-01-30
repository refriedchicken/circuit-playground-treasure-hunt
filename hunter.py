import time
import board
import pulseio
import adafruit_irremote
import neopixel

# Configure treasure information
#                  ID       PIXEL    COLOR
TREASURE_INFO = { (1,)*4 : (  0  , 0xC0392B) , #redish
                  (2,)*4 : (  1  , 0x9B59B6) , #purple
                  (3,)*4 : (  2  , 0x2980B9) , #blue
                  (4,)*4 : (  3  , 0x1ABC9C) , #seagreen
                  (5,)*4 : (  4  , 0xF1C40F) , #orange
                  (6,)*4 : (  5  , 0xECF0F1) , #white
                  (7,)*4 : (  6  , 0x196F3D) , #dark green
                  (8,)*4 : (  7  , 0xAED6F1) , #light blue
                  (9,)*4 : (  8  , 0xE59866) , #orange-brown
                  (10,)*4 : (  9  , 0xFF00FF)} #fuscia
treasures_found = dict.fromkeys(TREASURE_INFO.keys(), False) 

# Create NeoPixel object to indicate status
pixels = neopixel.NeoPixel(board.NEOPIXEL, 10)

# Sanity check setup
if len(TREASURE_INFO) > pixels.n:
    raise ValueError("More treasures than pixels.")

# Create a 'pulseio' input, to listen to infrared signals on the IR receiver
pulsein = pulseio.PulseIn(board.IR_RX, maxlen=120, idle_state=True)

# Create a decoder that will take pulses and turn them into numbers
decoder = adafruit_irremote.GenericDecode()

while True:
    # Listen for incoming IR pulses
    pulses = decoder.read_pulses(pulsein)

    # Try and decode them
    try:
        # Attempt to convert received pulses into numbers
        received_code = tuple(decoder.decode_bits(pulses, debug=False))
    except adafruit_irremote.IRNECRepeatException:
        # We got an unusual short code, probably a 'repeat' signal
        # print("NEC repeat!")
        continue
    except adafruit_irremote.IRDecodeException as e:
        # Something got distorted or maybe its not an NEC-type remote?
        # print("Failed to decode: ", e.args)
        continue

    # See if received code matches any of the treasures
    if received_code in TREASURE_INFO.keys():
        treasures_found[received_code] = True
        p, c = TREASURE_INFO[received_code] 
        pixels[p] = c
        
    # Check to see if all treasures have been found
    if False not in treasures_found.values():
        pixels.auto_write = False
        while True:
            # Round and round we go
            pixels.buf = pixels.buf[-3:] + pixels.buf[:-3]
            pixels.show()
            time.sleep(0.1)