import storage
import usb_cdc

usb_cdc.enable(console=True, data=True)
storage.remount('/', readonly=False)