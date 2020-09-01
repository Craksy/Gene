#!/usr/bin/env python3

import logging

logger = logging.getLogger('Gene')
handler = logging.FileHandler('debug.log', 'w+')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

logger.debug('-'*40)
logger.debug('starting logging for Gene')
