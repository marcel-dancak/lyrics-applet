import gtk

def get_option(title, option_widget):
	vbox = gtk.HBox(True, 30)
	vbox.pack_start(gtk.Label(title))
	vbox.pack_start(option_widget, True, True)
	return vbox

class OptionsDialog(gtk.Dialog):

	applet = None
	color_button = None
	font_button = None

	def __init__(self, lyrics_applet):
		gtk.Dialog.__init__(self, "Prefferences",
			flags=gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
			buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
		
		self.applet = lyrics_applet
		hbox = gtk.VBox()
		hbox.set_border_width(10)
		hbox.set_spacing(10)
		
		#print applet.get_preferences_key()
		#print applet.get_preferences_key("color")
		#print applet.gconf_get_full_key("color")
		self.color_button = gtk.ColorButton(lyrics_applet.color)
		self.color_button.set_use_alpha(True)
		hbox.pack_start(get_option("Color", self.color_button))
		
		self.font_button = gtk.FontButton(lyrics_applet.font)
		hbox.pack_start(get_option("Font", self.font_button))
		
		hbox.show_all()
		self.vbox.add(hbox)

	def save_preferences(self):
		self.applet.gconf_client.set_string("/apps/lyrics_applet/color", self.color_button.get_color().to_string())
		self.applet.gconf_client.set_string("/apps/lyrics_applet/font", self.font_button.get_font_name())


