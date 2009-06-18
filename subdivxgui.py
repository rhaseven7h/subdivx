#!/usr/bin/env python
#
#   This file is part of SubDivX.
#
#   SubDivX is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License.
#
#   SubDivX is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with SubDivX, if not, see <http://www.gnu.org/licenses/>.
#
#   See the LICENSE file.
#

import os
import gtk
import urllib
import subdivxclient

class SubDivXGUI:
  def __init__(self):
    self.subdivxclient = subdivxclient.SubDivXClient()
    self.builder = gtk.Builder()
    self.builder.add_from_file('/var/lib/subdivx/subdivx.glade')
    self.builder.connect_signals({
      'on_button_quit_clicked'         : self.app_quit,
      'on_window_subdivx_destroy'      : self.app_quit,
      'on_button_search_clicked'       : self.on_button_search_clicked,
      'on_button_next_clicked'         : self.on_button_next_clicked,
      'on_button_clear_clicked'        : self.on_button_clear_clicked,
      'on_button_results_fetch_clicked': self.on_button_results_fetch_clicked
    })
    
    self.win = self.builder.get_object('window_subdivx')
    self.win.maximize()
    
    self.entry_search = self.builder.get_object("entry_search")

    self.treeview_results = self.builder.get_object("treeview_results")

    column = gtk.TreeViewColumn('Name', gtk.CellRendererText(), text = 1)
    column.expand = False
    self.treeview_results.append_column(column)

    column = gtk.TreeViewColumn('CDs', gtk.CellRendererText(), text = 3)
    column.expand = False
    self.treeview_results.append_column(column)

    column = gtk.TreeViewColumn('Description', gtk.CellRendererText(), text = 2)
    column.expand = False
    self.treeview_results.append_column(column)

    self.treeview_results.set_tooltip_column(2)

    self.liststore_results = self.builder.get_object("liststore_results")
    
    self.button_next = self.builder.get_object("button_next")
    self.button_next.set_sensitive(False)
    self.button_clear = self.builder.get_object("button_clear")
    self.button_clear.set_sensitive(False)
    self.button_search = self.builder.get_object("button_search")
    self.button_search.set_sensitive(True)

    self.label_results = self.builder.get_object("label_results")
    
    self.page = 1
    
  def run(self):
    self.win.show()
    gtk.main()

  def app_quit(self, widget):
    gtk.main_quit()

  def on_button_search_clicked(self, widget):
    if len(self.entry_search.get_text().strip()) > 0:
      self.entry_search.set_sensitive(False)
      self.button_search.set_sensitive(False)
      self.button_next.set_sensitive(True)
      self.button_clear.set_sensitive(True)
      self.label_results.set_text("Results Page %s" % self.page)
      self.liststore_results.clear()
      results = self.subdivxclient.search(self.entry_search.get_text().strip(), self.page).results
      for i in range(len(results)):
        result = results[i]
        iter = self.liststore_results.append()
        self.liststore_results.set_value(iter, 0, i)
        self.liststore_results.set_value(iter, 1, results[i]['title'])
        self.liststore_results.set_value(iter, 2, results[i]['description'])
        self.liststore_results.set_value(iter, 3, int(results[i]['cds']))
        self.liststore_results.set_value(iter, 4, results[i]['link'])

      if len(results) < 20:
        self.button_next.set_sensitive(False)
    else:
      dialog = gtk.MessageDialog(self.win, flags=gtk.DIALOG_DESTROY_WITH_PARENT, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE)
      dialog.set_title("Error Searching")
      dialog.set_markup("Search Was Not Performed")
      dialog.format_secondary_text("You didn't specify any search terms.\nPlease try again.")
      dialog.run()
      dialog.destroy()      

  def on_button_next_clicked(self, widget):
    self.page += 1
    self.on_button_search_clicked(widget)
  
  def on_button_clear_clicked(self, widget):
    self.page = 1
    self.liststore_results.clear()
    self.entry_search.set_sensitive(True)
    self.button_search.set_sensitive(True)
    self.button_next.set_sensitive(False)
    self.button_clear.set_sensitive(False)
    self.label_results.set_text("Results")
  
  def on_button_results_fetch_clicked(self, widget):
    sel_model, sel_iter = self.treeview_results.get_selection().get_selected()
    if sel_iter:
      os.system("gnome-open %s" % self.subdivxclient.fetch(sel_model.get_value(sel_iter, 0)))
    else:                                                                      
      dialog = gtk.MessageDialog(self.win, flags=gtk.DIALOG_DESTROY_WITH_PARENT, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE)
      dialog.set_title("Error Downloading")
      dialog.set_markup("No Result Selected")
      dialog.format_secondary_text("You have to select a result to download.\nPlease try again.")
      dialog.run()
      dialog.destroy()




