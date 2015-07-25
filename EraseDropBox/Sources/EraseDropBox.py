#!/usr/bin/python
# -*- coding: utf-8 -*-

#############################################################################
# EraseDropBox an easy drag and drop file and folders erasing programm      #
# using the program wipe.                                                   #       
# Copyright (C) 2014 Bruggemann Eddie                                       #
#                                                                           #
# This file is part of EraseDropBox.                                        #
# EraseDropBox is free software: you can redistribute it and/or modify      #
# it under the terms of the GNU General Public License as published by      #
# the Free Software Foundation, either version 3 of the License, or         #
# (at your option) any later version.                                       #
#                                                                           #                   
# EraseDropBox is distributed in the hope that it will be useful,           #
# but WITHOUT ANY WARRANTY; without even the implied warranty of            #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              #
# GNU General Public License for more details.                              #
#                                                                           #
# You should have received a copy of the GNU General Public License         #
# along with EraseDropBox. If not, see <http://www.gnu.org/licenses/>       #
#############################################################################

from os import stat,listdir
from os.path import isdir, isfile, basename, expanduser, abspath

from stat import S_IMODE
from time import ctime

from urllib import unquote

from subprocess import Popen,PIPE

import pygtk
pygtk.require('2.0')
import gtk

class Eraser :


  def delete_event(self, widget, event, data=None):
    # close the window and quit
    gtk.main_quit()
    return False

  def clear_selected(self, button):
    ''' Remove the selected item from to erase list. '''
  
    if not self.is_navigating :
      # The user is at the root from the items list and not navigating into a folder.
    
      selection = self.treeview.get_selection() # Get user selection row.
    
      model, iter = selection.get_selected()    # Get the selection iterator.
    
      if iter:
        path = model.get_value(iter,5)          # Get the path from theitem to remove.
        model.remove(iter)
        self.content.remove("file://"+path)     # Remove the item from the items to erase list.
        if isdir(path) :
          self.cmp_content.remove(path)         # Remove the item from the navigating usage compare list.
    
      return
  
  def clear_all(self,button) :
    ''' Clear the content of the treeview and the list of items and folders to erase. '''
    if not self.is_navigating :
      # The user is at the root from the items list and not navigating into a folder.
    
      self.content=[]                      # Clear the items to erase list.
      self.cmp_content=[]                  # Clear the navigating usage compare list.
      liststore=self.treeview.get_model()  # Get the liststore.
      gtk.ListStore.clear(liststore)       # Clear the liststore.


  def __init__(self):
      # Create a new window
    
      path="/usr/share/EraseDropBox/Config/rc_style.rc"
      gtk.rc_parse(path)
    
      self.content=[]
      self.cmp_content=[]
      self.is_navigating=False
    
      # Main window.
      self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
      self.window.set_title("EraseDropBox")
      self.window.set_border_width(2)
      self.window.set_size_request(864, 600)

      self.window.connect("delete_event", self.delete_event) # Close the main window event catching.
    
      # Drag and drop Treeview main Frame.
      self.frame_scrolled_window=gtk.Frame()
    
      # Drag and drop Treeview main ScrolledWindow.
      self.scrolledwindow = gtk.ScrolledWindow()
      self.scrolledwindow.set_border_width(4)
    
      self.vbox = gtk.VBox()
    
      self.hbox = gtk.HBox()
      self.hbox.set_homogeneous(False)
      self.hbox.set_spacing(2)
    
      # Buttons Frame.
      self.frame_buttons=gtk.Frame()
      self.frame_buttons.set_shadow_type(gtk.SHADOW_ETCHED_IN)
      #self.frame_buttons.set_border_width(4)
    
      # Perform erasing task button.
      self.button_erase = gtk.Button()
      self.button_erase_label=gtk.Label()
      self.button_erase_label.set_markup("<tt> Erase</tt>")
      self.button_erase_label.show()
      self.button_erase_space=gtk.Label("  ")
      self.button_erase_space.show()
      self.button_erase_image=gtk.image_new_from_stock(gtk.STOCK_EXECUTE,4)
      self.button_erase_image.show()
      self.button_erase_hbox=gtk.HBox()
      self.button_erase_hbox.pack_start(self.button_erase_space,False,False,0)
      self.button_erase_hbox.pack_start(self.button_erase_image,False,False,0)
      self.button_erase_hbox.pack_start(self.button_erase_label,False,False,0)
      self.button_erase_hbox.show()
      self.button_erase.add(self.button_erase_hbox)
      self.button_erase.set_border_width(2)
      self.button_erase.connect("clicked",self.process_erasing)
      self.button_erase.set_tooltip_text("Execute the erasing of listed items and directories.")
    
      self.separator_1=gtk.VSeparator()
    
      # Item adding button.
      self.button_adding = gtk.Button()
      self.button_adding_label=gtk.Label()
      self.button_adding_label.set_markup("<tt> Add</tt>")
      self.button_adding_label.show()
      self.button_adding_space=gtk.Label("  ")
      self.button_adding_space.show()
      self.button_adding_image=gtk.image_new_from_stock(gtk.STOCK_ADD,4)
      self.button_adding_image.show()
      self.button_adding_hbox=gtk.HBox()
      self.button_adding_hbox.pack_start(self.button_adding_space,False,False,0)
      self.button_adding_hbox.pack_start(self.button_adding_image,False,False,0)
      self.button_adding_hbox.pack_start(self.button_adding_label,False,False,0)
      self.button_adding_hbox.show()
      self.button_adding.add(self.button_adding_hbox)
      self.button_adding.set_tooltip_text("Open an file selector to add items to delete.")
      self.button_adding.set_border_width(2)
      self.button_adding.connect("clicked",self.select_an_item)
    
      # Item removing button.
      self.button_remove = gtk.Button()
      self.button_remove_label=gtk.Label()
      self.button_remove_label.set_markup("<tt> Remove</tt>")
      self.button_remove_label.show()
      self.button_remove_space=gtk.Label("  ")
      self.button_remove_space.show()
      self.button_remove_image=gtk.image_new_from_stock(gtk.STOCK_REMOVE,4)
      self.button_remove_image.show()
      self.button_remove_hbox=gtk.HBox()
      self.button_remove_hbox.pack_start(self.button_remove_space,False,False,0)
      self.button_remove_hbox.pack_start(self.button_remove_image,False,False,0)
      self.button_remove_hbox.pack_start(self.button_remove_label,False,False,0)
      self.button_remove_hbox.show()
      self.button_remove.add(self.button_remove_hbox)
      self.button_remove.set_tooltip_text("Remove the selected item from the erasing task list.")
      self.button_remove.set_border_width(2)
      self.button_remove.connect('clicked', self.clear_selected)
    
      # Items clearing button.
      self.button_clear = gtk.Button()
      self.button_clear_label=gtk.Label()
      self.button_clear_label.set_markup("<tt> Clear</tt>")
      self.button_clear_label.show()
      self.button_clear_space=gtk.Label("  ")
      self.button_clear_space.show()
      self.button_clear_image=gtk.image_new_from_stock(gtk.STOCK_CLEAR,4)
      self.button_clear_image.show()
      self.button_clear_hbox=gtk.HBox()
      self.button_clear_hbox.pack_start(self.button_clear_space,False,False,0)
      self.button_clear_hbox.pack_start(self.button_clear_image,False,False,0)
      self.button_clear_hbox.pack_start(self.button_clear_label,False,False,0)
      self.button_clear_hbox.show()
      self.button_clear.add(self.button_clear_hbox)
      self.button_clear.set_tooltip_text("Remove all items from the erasing task list.")
      self.button_clear.set_border_width(2)
      self.button_clear.connect('clicked',self.clear_all)
    
      self.separator_2=gtk.VSeparator()
    
      # Iteration settings spinner.
      self.label_iterations=gtk.Label()
      self.label_iterations.set_markup("<tt>ITERATIONS:</tt>")
      self.adjustment_iterations=gtk.Adjustment(value=4, lower=1, upper=99, step_incr=1, page_incr=0, page_size=0)
      self.button_iterations = gtk.SpinButton(adjustment=self.adjustment_iterations, climb_rate=0, digits=0)
      self.button_iterations.set_tooltip_text("Set the number of overwriting iterations.")
      self.button_iterations.set_alignment(0.5)
    
      self.separator_3=gtk.VSeparator()
    
      # About button.
      self.button_about = gtk.Button()
      self.button_about_label=gtk.Label()
      self.button_about_label.set_markup("<tt> About</tt>")
      self.button_about_label.show()
      self.button_about_space=gtk.Label("  ")
      self.button_about_space.show()
      self.button_about_image=gtk.image_new_from_stock(gtk.STOCK_ABOUT,4)
      self.button_about_image.show()
      self.button_about_hbox=gtk.HBox()
      self.button_about_hbox.pack_start(self.button_about_space,False,False,0)
      self.button_about_hbox.pack_start(self.button_about_image,False,False,0)
      self.button_about_hbox.pack_start(self.button_about_label,False,False,0)
      self.button_about_hbox.show()
      self.button_about.add(self.button_about_hbox)
      self.button_about.set_tooltip_text("Display an about informations window.")
      self.button_about.set_border_width(2)
      self.button_about.connect("clicked",self.display_about)
    
      self.hbox.pack_start(self.button_erase,True,True,0)
      self.hbox.pack_start(self.separator_1,False,False,2)
      self.hbox.pack_start(self.button_adding,True,True,0)
      self.hbox.pack_start(self.button_remove,True,True,0)
      self.hbox.pack_start(self.button_clear,True,True,0)
      self.hbox.pack_start(self.separator_2,False,False,2)
      self.hbox.pack_start(self.label_iterations,True,True,0)
      self.hbox.pack_start(self.button_iterations,True,True,0)
      self.hbox.pack_start(self.separator_3,False,False,2)
      self.hbox.pack_start(self.button_about,True,True,0)
    
      self.frame_buttons.add(self.hbox)
      self.frame_scrolled_window.add(self.scrolledwindow)
      self.vbox.pack_start(self.frame_buttons,False,False,8)
      self.vbox.pack_start(self.frame_scrolled_window, True,True,4)
    

    
    
    
    
    
    
    
      # create a liststore with TreeView visible and not visible, for sorting usage, columns.
      self.liststore = gtk.ListStore(str,str,str,str,str,str,int,int,int,int)    

      # create the TreeView using liststore.
      self.treeview = gtk.TreeView(self.liststore)
      self.treeview.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH | gtk.TREE_VIEW_GRID_LINES_HORIZONTAL)
      self.treeview.set_rules_hint(True)
   
      # create the CellRenderer to render the data
    
      # Icon cell.
      self.cell_icon = gtk.CellRendererPixbuf()
      self.cell_icon.set_property('cell-background', '#d9d9d9')
    
      # Item name cell.
      self.cell_name = gtk.CellRendererText()
      self.cell_name.set_fixed_size(256+128, 16)
      self.cell_name.set_property('cell-background', '#d9d9d9')
    
      # Items size cell.
      self.cell_size = gtk.CellRendererText()
      self.cell_size.set_property('cell-background', '#d9d9d9')
    
      # Item mode cell.
      self.cell_mode = gtk.CellRendererText()
      self.cell_mode.set_fixed_size(16, 16)
      self.cell_mode.set_property('cell-background', '#d9d9d9')
    
      # Last modification timestamp cell.
      self.cell_date = gtk.CellRendererText()
      self.cell_date.set_property('cell-background', '#d9d9d9')
    
      # Not visible, for sorting usage, cells.
      self.cell_path = gtk.CellRendererText()
      self.cell_byte = gtk.CellRendererText()
      self.cell_time = gtk.CellRendererText()
    
    
    
    
      # create the TreeViewColumns to display the data
    
      self.tvcolumn_icon = gtk.TreeViewColumn("Type", self.cell_icon, stock_id=0)
    
      self.tvcolumn_name = gtk.TreeViewColumn("Name", self.cell_name, text=1)
    
      self.tvcolumn_size = gtk.TreeViewColumn("Size", self.cell_size, text=2)
    
      self.tvcolumn_mode = gtk.TreeViewColumn("Mode", self.cell_mode, text=3)
    
      self.tvcolumn_date = gtk.TreeViewColumn("Last modification", self.cell_date, text=4)
    
      self.tvcolumn_path = gtk.TreeViewColumn("", self.cell_path, text=5)
      self.tvcolumn_path.set_visible(False)
    
      self.tvcolumn_byte = gtk.TreeViewColumn("", self.cell_byte, text=6)
      self.tvcolumn_byte.set_visible(False)
    
      self.tvcolumn_time = gtk.TreeViewColumn("", self.cell_time, text=7)
      self.tvcolumn_time.set_visible(False)
    
      self.tvcolumn_icon.set_min_width(1)
      self.tvcolumn_icon.set_sort_column_id(9)
    
      self.tvcolumn_name.set_min_width(256+64)
      self.tvcolumn_name.set_sort_column_id(2)
      self.tvcolumn_name.set_sort_indicator(True)
    
      self.tvcolumn_size.set_min_width(96)
      self.tvcolumn_size.set_sort_column_id(6)
      self.tvcolumn_size.set_sort_indicator(True)
    
      self.tvcolumn_mode.set_min_width(5)
      self.tvcolumn_mode.set_max_width(72)
      self.tvcolumn_mode.set_sort_column_id(8)
      self.tvcolumn_mode.set_sort_indicator(True)
    
      self.tvcolumn_date.set_min_width(600-300-128)
      self.tvcolumn_date.set_sort_column_id(7)
      self.tvcolumn_date.set_sort_indicator(True)
    
      self.treeview.append_column(self.tvcolumn_icon)
      self.treeview.append_column(self.tvcolumn_name)
      self.treeview.append_column(self.tvcolumn_size)
      self.treeview.append_column(self.tvcolumn_mode)
      self.treeview.append_column(self.tvcolumn_date)
      self.treeview.append_column(self.tvcolumn_path)
      self.treeview.append_column(self.tvcolumn_byte)
    
    
      # Allow enable drag and drop of rows including row move
      self.treeview.enable_model_drag_source( gtk.gdk.BUTTON1_MASK,[('text/plain', 0, 0)],gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
      self.treeview.enable_model_drag_dest([('text/plain', 0, 0)],gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)

      # Drag and drop settings.
      self.treeview.connect("drag_data_received",
                            self.drag_data_received_data)
    
      # Naviagting in a folder settings.
      self.treeview.connect('row-activated',self.row_clicked)
    
    
      self.scrolledwindow.add(self.treeview)
      self.window.add(self.vbox)
      self.window.show_all()
  


  def drag_data_received_data(self, treeview, context, x, y, selection,info, etime):
    ''' Drag and drop Treeview receive data function. '''
  
    model = treeview.get_model()
  
    data = selection.get_text() # Get the dropped item path urlencoded with scheme file://.
  
    datas=unquote(data)         # Decode the item filepath given from the drag and dtop mechanism as an URI.
  
    datas=data.split('\n')
    datas.pop(-1)               # Remove the last '\n' character.
  
    datas=[ unquote(v) for v in datas ]
  
    for y in datas :
      # We loop in case the user drag more than one item.
    
      # Normalise the filepath.
      name_string=str()
      for v in y :
        name_string += chr(ord(v)) # Converting in filepath in a string.
    
      if isdir(name_string[7::]) :
      
        self.content.append(name_string)           # Adding the path to the items to erase list.
        self.cmp_content.append(name_string[7::])  # Adding the path (scheme splitted) to the folder navigation usage compare list.
      
        stats=stat(name_string[7::])               # Getting metadatas about the item.
      
        # Computing size column content.
        if stats.st_size < 1000 :
          size=str(stats.st_size)
        elif stats.st_size < 1000000 and stats.st_size >= 1000 :
          size=str(round(stats.st_size/1000.,1))+" Ko"
        elif stats.st_size < 1000000000 and stats.st_size >= 1000000 :
          size=str(round(stats.st_size/1000000.,1))+" Mo"
        elif stats.st_size > 1000000000 :
          size=str(round(stats.st_size/1000000000.,1))+" Go"
      
        # Append the item to the Treeview Liststore.
        model.append([gtk.STOCK_DIRECTORY,basename(name_string[7::]),size,oct(S_IMODE(stats.st_mode)),ctime(stats.st_mtime),name_string[7::],stats.st_size,stats.st_mtime,int(oct(S_IMODE(stats.st_mode)),8),1])
      
      elif isfile(name_string[7::]) :
      
        self.content.append(name_string)           # Adding the path to the items to erase list.
      
        stats=stat(name_string[7::])               # Getting metadatas about the item.
      
        # Computing size column content.
        if stats.st_size < 1000 :
          size=str(stats.st_size)
        elif stats.st_size < 1000000 and stats.st_size >= 1000 :
          size=str(round(stats.st_size/1000.,1))+" Ko"
        elif stats.st_size < 1000000000 and stats.st_size >= 1000000 :
          size=str(round(stats.st_size/1000000.,1))+" Mo"
        elif stats.st_size > 1000000000 :
          size=str(round(stats.st_size/1000000000.,1))+" Go"
      
        # Append the item to the Treeview Liststore.
        model.append([gtk.STOCK_FILE,basename(name_string[7:256]),size,oct(S_IMODE(stats.st_mode)),ctime(stats.st_mtime),name_string[7::],stats.st_size,stats.st_mtime,int(oct(S_IMODE(stats.st_mode)),8),0])
      
    return
  
  def process_erasing(self,widget) :
    ''' Functionto process to the erasing task. '''
  
    iterations=int(self.adjustment_iterations.get_value()) # Getting user iterations numbers settings.
  
    model = self.treeview.get_model()
  
    for v in self.content :
    
      if isfile(v[7::]) :
        # For items we use the programm wipe to erase items.
        cmdline="wipe -r -c -f -q -Q {0} \'{1}\'".format(iterations,v[7::]) # Construct the subprocess string to execute.
    
      elif isdir(v[7::]) :
        # For folders we use the programm wipe to erase folders recursively.
        cmdline="wipe -r -c -f -q -Q {0} \'{1}\'".format(iterations,v[7::]) # Construct the subprocess string to execute.
    
      action=Popen(cmdline,shell="/bin/bash",stdout=PIPE,stdin=PIPE)        # Process the item erasing task.
    
      action.wait()                                                         # Wait for subprocess to terminate.
    
      iter=model.get_iter((0,))                                           
      model.remove(iter)                                                    # Remove item from the Treeview.
 
    # Reset the settings after erasing task complete.
    self.content=[]
    self.cmp_content=[]
    self.is_navigating=False
      
  
  

  def add_selected_item_to_treeview(self,filepath) :
    ''' Function to add an item to the erasing list from the file selector. '''
  
    model = self.treeview.get_model()
  
    if isdir(filepath) :
    
      self.content.append("file://"+filepath)  # Adding the path to the items to erase list.
      self.cmp_content.append(filepath)        # Adding the path to the folder navigation usage compare list.
    
      stats=stat(filepath)                     # Getting metadatas about the item.
    
      # Computing size column content.
      if stats.st_size < 1000 :
        size=str(stats.st_size)
      elif stats.st_size < 1000000 and stats.st_size >= 1000 :
        size=str(round(stats.st_size/1000.,1))+" Ko"
      elif stats.st_size < 1000000000 and stats.st_size >= 1000000 :
        size=str(round(stats.st_size/1000000.,1))+" Mo"
      elif stats.st_size > 1000000000 :
        size=str(round(stats.st_size/1000000000.,1))+" Go"
     
      # Append the item to the Treeview Liststore.
      model.append([gtk.STOCK_DIRECTORY,basename(filepath),size,oct(S_IMODE(stats.st_mode)),ctime(stats.st_mtime),filepath,stats.st_size,stats.st_mtime,int(oct(S_IMODE(stats.st_mode)),8),1])
    
    elif isfile(filepath) :
    
      self.content.append("file://"+filepath) # Adding the path to the items to erase list.
    
      stats=stat(filepath)                    # Getting metadatas about the item.
    
      # Computing size column content.
      if stats.st_size < 1000 :
        size=str(stats.st_size)
      elif stats.st_size < 1000000 and stats.st_size >= 1000 :
        size=str(round(stats.st_size/1000.,1))+" Ko"
      elif stats.st_size < 1000000000 and stats.st_size >= 1000000 :
        size=str(round(stats.st_size/1000000.,1))+" Mo"
      elif stats.st_size > 1000000000 :
        size=str(round(stats.st_size/1000000000.,1))+" Go"
    
      # Append the item to the Treeview Liststore.
      model.append([gtk.STOCK_FILE,basename(filepath),size,oct(S_IMODE(stats.st_mode)),ctime(stats.st_mtime),filepath,stats.st_size,stats.st_mtime,int(oct(S_IMODE(stats.st_mode)),8),0])
    
    return


  def navigate_folder(self, folder=None):  
    ''' Function returning an folder content list.
        Used for user folder navigating.
    '''
  
    self.is_navigating=True
  
    # Items list contructing.
    items = [f for f in listdir(folder) if f[0] <> '.']
    items.sort()
    items = ['..'] + items
  
    model = gtk.ListStore(str,str,str,str,str,str,int,int,int,int)
  
    for f in items:

      if isdir(folder+"/"+f) :
      
        stats=stat(folder+"/"+f) # Getting metadatas about the item.
      
        # Computing size column content.
        if stats.st_size < 1000 :
          size=str(stats.st_size)
        elif stats.st_size < 1000000 and stats.st_size >= 1000 :
          size=str(round(stats.st_size/1000.,1))+" Ko"
        elif stats.st_size < 1000000000 and stats.st_size >= 1000000 :
          size=str(round(stats.st_size/1000000.,1))+" Mo"
        elif stats.st_size > 1000000000 :
          size=str(round(stats.st_size/1000000000.,1))+" Go"
      
        icon=gtk.STOCK_DIRECTORY
        is_directory=1
      
      elif isfile(folder+"/"+f) :
      
        stats=stat(folder+"/"+f) # Getting metadatas about the item.
      
        # Computing size column content.
        if stats.st_size < 1000 :
          size=str(stats.st_size)
        elif stats.st_size < 1000000 and stats.st_size >= 1000 :
          size=str(round(stats.st_size/1000.,1))+" Ko"
        elif stats.st_size < 1000000000 and stats.st_size >= 1000000 :
          size=str(round(stats.st_size/1000000.,1))+" Mo"
        elif stats.st_size > 1000000000 :
          size=str(round(stats.st_size/1000000000.,1))+" Go"
      
        icon=gtk.STOCK_FILE
        is_directory=0
    
      # Append the item to the Treeview Liststore.
      model.append([icon,f,size,oct(S_IMODE(stats.st_mode)),ctime(stats.st_mtime),folder+"/"+f,stats.st_size,stats.st_mtime,int(oct(S_IMODE(stats.st_mode)),8),is_directory])
  
    return model

  def row_clicked(self,treeview,path,column) :
    ''' Function to navigating into a selected folder by clicking on it. '''
  
    field=treeview.get_column(5) # Not visible path column content.
  
    if isdir(field.get_cell_renderers()[0].get_property("text")) :
    
      to_cmp=field.get_cell_renderers()[0].get_property("text") # Not visible path cell content.
    
      if to_cmp[0:-3] in self.cmp_content and self.is_navigating :
      
        model=self.restore_current_names()  # Restore parent folder content.
        self.treeview.set_model(model)
        self.is_navigating=False
      
      else :
      
        if to_cmp.endswith('/..') :
          to_cmp=abspath(to_cmp)
        
        model=self.navigate_folder(to_cmp)
        self.treeview.set_model(model)

  def restore_current_names(self) :
    ''' Function to list parent folder ("../") content by navigating. '''
  
    model = gtk.ListStore(str,str,str,str,str,str,int,int,int,int)
  
    for v in self.content:
    
      if isdir(v[7::]) :
      
        stats=stat(v[7::])     # Getting metadatas about the item.
      
        # Computing size column content.
        if stats.st_size < 1000 :
          size=str(stats.st_size)
        elif stats.st_size < 1000000 and stats.st_size >= 1000 :
          size=str(round(stats.st_size/1000.,1))+" Ko"
        elif stats.st_size < 1000000000 and stats.st_size >= 1000000 :
          size=str(round(stats.st_size/1000000.,1))+" Mo"
        elif stats.st_size > 1000000000 :
          size=str(round(stats.st_size/1000000000.,1))+" Go"
        
        model.append([gtk.STOCK_DIRECTORY,basename(v[7::]),size,oct(S_IMODE(stats.st_mode)),ctime(stats.st_mtime),v[7::],stats.st_size,stats.st_mtime,int(oct(S_IMODE(stats.st_mode)),8),1])
      
      elif isfile(v[7::]) :
      
        stats=stat(v[7::])     # Getting metadatas about the item.
     
        # Computing size column content.
        if stats.st_size < 1000 :
          size=str(stats.st_size)
        elif stats.st_size < 1000000 and stats.st_size >= 1000 :
          size=str(round(stats.st_size/1000.,1))+" Ko"
        elif stats.st_size < 1000000000 and stats.st_size >= 1000000 :
          size=str(round(stats.st_size/1000000.,1))+" Mo"
        elif stats.st_size > 1000000000 :
          size=str(round(stats.st_size/1000000000.,1))+" Go"
      
        model.append([gtk.STOCK_FILE,basename(v[7:256]),size,oct(S_IMODE(stats.st_mode)),ctime(stats.st_mtime),v[7::],stats.st_size,stats.st_mtime,int(oct(S_IMODE(stats.st_mode)),8),0])
      
      
      
    return model

  def destroy_about_window(self,widget,response) :
    ''' Destroy about Dialog window. '''
    self.about_dialog_main_window.destroy()

  def display_about(self,widget) :
    ''' Display About window. '''
  
    self.about_dialog_main_window=gtk.AboutDialog()
  
    self.about_dialog_main_window.set_program_name("EraseDropBox")
  
    self.about_dialog_main_window.set_version("1.0.0")
  
    self.about_dialog_main_window.set_copyright("GPLv3")
  
    license_file_object=file("/usr/share/EraseDropBox/License/gpl.txt",'r')
    self.about_dialog_main_window.set_license(license_file_object.read())
    license_file_object.close()
  
    self.about_dialog_main_window.set_wrap_license(True)
  
    self.about_dialog_main_window.set_authors(["Bruggemann Eddie\nContact: mrcyberfighter@gmailcom\nGPLv3 © 2014 "])
  
    self.about_dialog_main_window.set_artists(["Bruggemann Eddie\nContact: mrcyberfighter@gmailcom\nGPLv3 © 2014 "])
  
    self.about_dialog_main_window.set_documenters(["Bruggemann Eddie\nContact: mrcyberfighter@gmailcom\nGPLv3 © 2014 "])
  
    about_dialog_icon = gtk.gdk.pixbuf_new_from_file("/usr/share/EraseDropBox/Icon/EraseDropBox_Icon.png")
    self.about_dialog_main_window.set_logo(about_dialog_icon)
  
    self.about_dialog_main_window.set_comments("Thank's to my mother and to the doctors.\nStay away from drugs:\ndrugs destroy your brain\nand your life !!!")
  
    self.about_dialog_main_window.connect("response",self.destroy_about_window)
  
    self.about_dialog_main_window.run()

  def select_an_item(self,widget) :
    ''' Construct an file selector toplevel. '''
  
    self.select_file_toplevel=gtk.Window(type=gtk.WINDOW_TOPLEVEL)
    self.select_file_toplevel.set_title("Select an directory or an file to secure delete:")
    self.select_file_toplevel.set_size_request(768+128,256+256+64)
    self.select_file_toplevel.set_resizable(False)
    
    self.select_file_file_chooser=gtk.FileChooserWidget(action=gtk.FILE_CHOOSER_ACTION_OPEN, backend=None)
    self.select_file_file_chooser.connect("selection-changed",self.select_file_operation_update_selection)

    self.select_file_file_ok_button=gtk.Button(label=None, stock=gtk.STOCK_OK, use_underline=True)
    self.select_file_file_ok_button.connect("clicked",self.select_file_operation_toplevel_ok)
    self.select_file_file_ok_button.set_size_request(128+40,32)
    self.select_file_file_ok_button.show()
  
    self.select_file_file_cancel_button=gtk.Button(label=None, stock=gtk.STOCK_CANCEL, use_underline=True)
    self.select_file_file_cancel_button.connect("clicked",self.select_file_operation_toplevel_cancel)
    self.select_file_file_cancel_button.set_size_request(128+40,32)
    self.select_file_file_cancel_button.show()
   
  
  
    self.select_file_file_entry=gtk.Entry(0)
    self.select_file_file_entry.set_can_focus(False)
    self.select_file_file_entry.set_width_chars(66)
    self.select_file_file_entry.set_text("")
    self.select_file_file_entry.set_alignment(0.0)
    self.select_file_file_entry.show()
  
  
  
    self.select_file_file_hbox=gtk.HBox(False,2)
    self.select_file_file_hbox.pack_start(self.select_file_file_cancel_button,True,True,2)
    self.select_file_file_hbox.pack_start(self.select_file_file_entry,True,True,2)
    self.select_file_file_hbox.pack_start(self.select_file_file_ok_button,True,True,2)
    self.select_file_file_hbox.show()
  
    self.select_file_file_chooser.set_extra_widget(self.select_file_file_hbox)
  
    self.select_file_file_chooser.set_property("show-hidden",True)
  
    self.select_file_file_chooser.set_show_hidden(True)
    self.select_file_file_chooser.set_current_folder(expanduser("~"))
    self.select_file_file_chooser.set_preview_widget_active(True)
    self.select_file_file_chooser.set_use_preview_label(True)
    self.select_file_file_chooser.show()
  
    self.select_file_toplevel.add(self.select_file_file_chooser)
  
  
    self.select_file_toplevel.show()


  def select_file_operation_toplevel_ok(self,widget) :
    ''' File selector file selected callback. '''   
    self.add_selected_item_to_treeview(self.select_file_file_chooser.get_filename())
  
    self.select_file_toplevel.destroy()
  
  def select_file_operation_toplevel_cancel(self,widget) :
    ''' File selector cancel callback. ''' 
    self.select_file_toplevel.destroy()
  
  def select_file_operation_update_selection(self,widget) :
    ''' File selector update slection Entry widget. ''' 
  
    if not widget.get_filename() :
      return
  
    if isfile(widget.get_filename()) or isdir(widget.get_filename()) :
      self.select_file_file_entry.set_text(basename(widget.get_filename()))
  
    else :
      self.select_file_file_entry.set_text("")

def main():
    gtk.main()

if __name__ == "__main__":
    eraser = Eraser()
    main()