import time
import pytest
import logging

import nvme as d
import PySimpleGUI as sg


def test_format(nvme0: d.Controller, nvme0n1):
    nvme0.format(0).waitdone()


def test_download_firmware(nvme0):
    layout = [[sg.Text('select the firmware binary file')],
              [sg.In(), sg.FileBrowse()],
              [sg.OK(), sg.Cancel()]]
    _, (filename,) = sg.Window('pynvme', layout).Read()
    if filename:        
        logging.info("To download firmware binary file: " + filename)
        nvme0.downfw(filename)
    

def test_powercycle_by_sleep(subsystem):
    # sleep system for 10 seconds, to make DUT power off and on
    subsystem.power_cycle()


def test_controller_identify_data(nvme0: d.Controller):
    b = d.Buffer()
    nvme0.identify(b).waitdone()
    b.dump()


def test_sanitize(nvme0, nvme0n1):
    buf = d.Buffer()

    nvme0.identify(buf).waitdone()
    if buf.data(331, 328) == 0:
        warnings.warn("sanitize operation is not supported")
        return

    logging.info("supported sanitize operation: %d" % buf.data(331, 328))
    nvme0.sanitize().waitdone()

    # sanitize status log page
    nvme0.getlogpage(0x81, buf, 20).waitdone()
    while buf.data(3, 2) & 0x7 != 1:  # sanitize is not completed
        progress = buf.data(1, 0)*100//0xffff
        sg.OneLineProgressMeter('sanitize progress', progress, 100,
                                'key', orientation='h')
        nvme0.getlogpage(0x81, buf, 20).waitdone()
        time.sleep(1)
        
