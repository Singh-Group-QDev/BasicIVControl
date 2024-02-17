from time import sleep

def isWithin(have, want, range):
    return want - range <= have <= want + range

def waitForTempBelow(triton, source, temperature):
    if (triton.get_temp_T8() > temperature):
        source.source_current = 0
        while(triton.get_temp_T8() > temperature):
            sleep(60)