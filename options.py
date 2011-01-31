import gtk

class Option(object):
	pass

class ColorOption(Option):
	pass


def get_option(title, option_widget):
	vbox = gtk.HBox(True, 30)
	vbox.pack_start(gtk.Label(title))
	vbox.pack_start(option_widget, True, True)
	return vbox

class OptionsDialog(gtk.Dialog):

	applet = None
	color = None
	font = None

	def __init__(self, applet):
		gtk.Dialog.__init__(self, "Prefferences",
			flags=gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
			buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
		
		self.applet = applet
		hbox = gtk.VBox()
		hbox.set_border_width(10)
		hbox.set_spacing(10)
		
		#print applet.get_preferences_key()
		#print applet.get_preferences_key("color")
		#print applet.gconf_get_full_key("color")
		self.color = gtk.ColorButton()
		self.color.set_use_alpha(True)
		hbox.pack_start(get_option("Color", self.color))
		
		self.font = gtk.FontButton()
		hbox.pack_start(get_option("Font", self.font))
		
		hbox.show_all()
		self.vbox.add(hbox)


