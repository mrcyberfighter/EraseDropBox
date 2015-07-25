#!/bin/bash

###############################################################################
#                                                                             #
# Application:  EraseDropBox: An easy drag and drop file and folders          #
#               erasing programm using the programm wipe.                     #
#                                                                             #
# Dependencies: python-gtk2.                                                  #
# Dependencies: wipe.                                                         #
#                                                                             #
###############################################################################

sudo echo 'Start installation from the program EraseDropBox...'
if [[ $? != '0' ]]
then
echo "This installation script must be run as root"
return 1
fi

# Check if pygtk is installed on the target system.
sudo python -c "import gtk"

if [[ $? != 0 ]]
then
  sudo echo 'ERROR: the python-gtk2 is not installed on your system  !!!'
  sudo echo 'Python module python-gtk2 required !!! For EraseDropBox installation.'
  sudo echo 'Install the python-gtk2 package.'
  sudo echo 'Then retry the installation of EraseDropBox...'
  return 1
fi

# Check if wipe is installed on the target system.
sudo wipe --help 2> /dev/null

if [[ $? != 0 ]] ; then
 
  sudo echo 'ERROR: wipe program is not installed on your system  !!!'
  sudo echo 'wipe program required !!! For EraseDropBox installation.'
  sudo echo 'Install the wipe package.'
  sudo echo 'Then retry the installation of EraseDropBox...'

  return 1

fi

way_prg="$PWD/Sources/EraseDropBox.py"
way_icon="$PWD/Icon/EraseDropBox_Icon.png"
way_readme="$PWD/README/README.txt"
way_license="$PWD/License/gpl.txt"
way_config="$PWD/Config/rc_style.rc"
way_desktop="$PWD/Desktop/EraseDropBox.desktop"

if [[ ! -d /usr/share/EraseDropBox ]] ; then
 
  # EraseDropBox folders creation.
 
  sudo mkdir "/usr/share/EraseDropBox/"

  sudo mkdir "/usr/share/EraseDropBox/Sources/"
  sudo mkdir "/usr/share/EraseDropBox/Icon/"
  sudo mkdir "/usr/share/EraseDropBox/README/"
  sudo mkdir "/usr/share/EraseDropBox/License/"
  sudo mkdir "/usr/share/EraseDropBox/Config/"

fi



# EraseDropBox files copy.
sudo cp "${way_icon}" "/usr/share/EraseDropBox/Icon/"
sudo cp "${way_readme}" "/usr/share/EraseDropBox/README/"
sudo cp "${way_prg}" "/usr/share/EraseDropBox/Sources/"
sudo cp "${way_license}" "/usr/share/EraseDropBox/License/"
sudo cp "${way_config}" "/usr/share/EraseDropBox/Config/"

# Copy of the python script in a executable folder.
sudo cp "${way_prg}" "/usr/bin/"
sudo chmod a+x "/usr/bin/EraseDropBox.py"



sudo echo "Start shortcut installation..."

# Check if shortcut directory exist like i know it.
if [[ -d /usr/share/applications ]] ; then
 
  # copy of the desktop file.
  sudo cp "${way_desktop}" /usr/share/applications


  sudo echo 'shortcut installation successfull !!!'

else

  # Shortcut directory not found on target system.
  sudo echo "WARNING: cannot find shortcut directory."
  sudo echo "No shortcut installation."

fi   

# Make a symbolic link for program name.
sudo ln -fs "/usr/bin/EraseDropBox.py" "/usr/bin/erasedropbox"
sudo ln -fs "/usr/bin/EraseDropBox.py" "/usr/bin/EraseDropBox"

sudo echo "EraseDropBox installation successfull !!!"
