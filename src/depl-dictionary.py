import os
import gi
from html.parser import HTMLParser
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gydict
from gi.repository import Pango
from gi.repository import Dazzle
from gi.repository import GLib
from gi.repository import Gio

SETTINGS_PATH = "/org/gtk/gydict/plugin/depl-dictionary-german-polish/"
DICT_ID       = "depl-dictionary-german-polish"

class DeplWin(GObject.Object, Gydict.WindowAddin):
    def do_load(self, win):
        win.get_dict_manager().insert_dict(DeplDict(identifier=DICT_ID), DICT_ID)

    def do_unload(self, win):
        win.get_dict_manager().remove_dict(DICT_ID)


class DeplPrefs(GObject.Object, Gydict.PrefsViewAddin):
    def do_load(self, prefs):
        self.id_widget = prefs.add_file_chooser("dictionaries", "paths", "org.gtk.gydict.path", "path",
                                                 SETTINGS_PATH, "DEPL Dictionary German-Polish", "Select dictionary.dat",
                                                 Gtk.FileChooserAction.OPEN, "", 0)

    def do_unload(self, prefs):
        prefs.remove_id(self.id_widget)

class Parser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.s = GLib.String()
        self.stack = []
        self.to_apply = []

    def get_parsed_string(self):
        return self.s.str

    def get_attr_list(self):
        attr_list = Pango.AttrList.new()

        for attr in self.stack:
            Gydict.TextAttribute.insert_attr_to_list (attr_list, attr)

        return attr_list

    def handle_starttag(self, tag, attrs):
        if tag == "b":
            attr = Gydict.TextAttribute.weight_new(Pango.Weight.BOLD)
            attr.set_start_index(self.s.len)
            self.stack.append(attr)
        elif tag == "i":
            attr = Gydict.TextAttribute.style_new(Pango.Style.ITALIC)
            attr.set_start_index(self.s.len)
            self.stack.append(attr)
            pass
        elif tag == "font":
            color = None
            if attrs[0][1] == "dodgerblue":
                color = "#1e90ff"
            elif attrs[0][1] == "green":
                color = "#008000"
            elif attrs[0][1] == "blue":
                color = "#0000ff"
            elif attrs[0][1] == "lightcoral":
                color = "#f08080"
            else:
                print(attrs)
            if color != None:
                attr = Gydict.TextAttribute.foreground_new_from_hex(color)
                attr.set_start_index(self.s.len)
                self.stack.append(attr)
        elif tag == "acronym":
            pass
        elif tag == "a":
            pass
        else:
            print("Unknown tag: <%s>" % tag)

    def handle_endtag(self, tag):

        if tag in ("b", "i", "font"):
            attr = self.stack[-1]
            attr.set_end_index(self.s.len)
            self.to_apply.append(attr)
            del self.stack[-1]
        elif tag == "acronym":
            pass
        elif tag == "a":
            pass
        else:
            print("Unknown tag: </%s>" % tag)

    def handle_data(self, data):
        self.s.append(data.replace("  ", "\n"))

class DeplDict(Gydict.Dict):

    def do_map(self):
        filepath = Gio.Settings.new_with_path("org.gtk.gydict.path", SETTINGS_PATH).get_string("path")

        if not os.path.isfile(filepath):
            self.set_property("is-mapped", False)
            raise GLib.Error("File path {} does not exist.".format(filepath), "DEPL", GLib.FileError.NOENT)

        self.store = Gtk.ListStore(str)
        self.lexical_units = []

        with open(filepath) as fp:
            for line in fp:
                self.lexical_units.append(line)
                self.store.append([line[0:line.find("  ")]])

        self.set_property("model", self.store)
        self.set_property("is-mapped", True)

    def do_get_lexical_unit(self, idx):
        return self.lexical_units[idx]

    def do_parse(self, text, length):
        parser = Parser()
        parser.feed(text)

        attr_list = Pango.AttrList.new()
        for attr in parser.to_apply:
            Gydict.TextAttribute.insert_attr_to_list (attr_list, attr)

        return (True, attr_list, parser.get_parsed_string())


