import tkinter as tk
import logging

logger = logging.getLogger()

logger.setLevel(logging.DEBUG)

stream_handler=logging.StreamHandler()
file_handler = logging.FileHandler('info.log')

formatter = logging.Formatter('%(asctime)s %(levelname)s :: %(message)s')
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

logger.debug("This is a debugging message")
logger.info("This is a debugging info")
logger.warning("This is a debugging warning")
logger.error("This is a debugging error")


if __name__=='__main__':
    root = tk.Tk()
    root.mainloop()
