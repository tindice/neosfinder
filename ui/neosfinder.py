#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk
import nfClass
import os


Ui = nfClass.Gui()

Gtk.main()
for f in framelist:
    os.remove(tmpfolder+f)

#~ print Ui.fitlist
 
