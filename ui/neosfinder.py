#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk
import nfClass, DataViewerClass
import os, tempfile

_,tmpfolder = tempfile.mkstemp()

Ui = nfClass.Gui()

Gtk.main()

 
