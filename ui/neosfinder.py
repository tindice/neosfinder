#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk
import nfClass
import os, tempfile

_,tmpfolder = tempfile.mkstemp()

Ui = nfClass.Gui()

Gtk.main()

 
