#!/bin/bash
# -*- coding: utf-8 -*-

sudo echo 'Start uninstall EraseDropBox...'

if [[ $? != '0' ]] ; then
 
  echo "This installation script must be run as root"
  return 1
 
fi

sudo rm -R "/usr/share/EraseDropBox/"

sudo rm "/usr/share/applications/EraseDropBox.desktop"

sudo unlink "/usr/bin/erasedropbox"
sudo unlink "/usr/bin/EraseDropBox"


sudo rm "/usr/bin/EraseDropBox.py"

sudo echo "EraseDropBox successfull remove from your system !!!"