# -*- coding: utf-8 -*-

import signal
import sys
import multiprocessing
sys.path.insert(1, './backend')
import config

from common import processYT, signal_handler

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
  multiprocessing.set_start_method("spawn")
  ytId = input(f"{config.interface_config['Main']['InputYT']}").strip()
  try:
      lang = input(f"{config.interface_config['Main']['InputLang']}").strip()
  except ValueError as e:
      lang = 'eng'
  processYT(ytId, lang)