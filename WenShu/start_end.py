# -*- coding: utf-8 -*-
__author__ = "nixinxin"

import os
import sys
from scrapy.cmdline import execute

execute(['scrapy', 'crawl', 'wenshu', '-s JOBDIR=/status/001'])