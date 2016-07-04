#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  arfedora_nvidiab.py
#
#  Copyright 2016 youcef sourani <youcef.m.sourani@gmail.com>
#
#  www.arfedora.blogspot.com
#
#  www.arfedora.com
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import os
import subprocess
import platform
import sys
from talwin import talwin


home=os.getenv("HOME")
dirname=os.path.abspath(os.path.dirname(__file__))

def init_check():
	
	if os.getuid()==0:
		sys.exit("Run Script Without Root Permissions.")
		
	if platform.linux_distribution()[0]!="Fedora":
		sys.exit("Fedora Not Found.")
		
	if not sys.version.startswith("3"):
		sys.exit("Use Python 3 Try run python3 nvidia_install.py")
		
	if  platform.linux_distribution()[1]!="23" and platform.linux_distribution()[1]!="24":
		sys.exit("Fedora 23 || Fedora 24 Not Found.")
		







def check_vga_supported():
	count1=0
	count2=0
	sto1= subprocess.Popen("lspci |grep  VGA;lspci |grep 3D",stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0].decode('utf-8').strip().split()
	for word in sto1:
		if word=="VGA" or word=="3D":
			count1+=1
		if word=="Intel" or word=="NVIDIA":
			count2+=1

	if count1!=2 and count2!=2:
		sys.exit("VGA NOT SUPPORTED.")



init_check()
check_vga_supported()


def welcome():
	subprocess.call("clear")
	welcom="""
*******************************************************************
*[[[[[[[[[[[[[[[[[[[[[[[[          ~~~~~~~~~~~~~~~~~~~~~~~~~      *
*[[[[[[[[[[[[[[[[[[[[[[[[          ~~~~~~~~~~~~~~~~~~~~~~~~~      *
*{{{{{{{{{{{,{{{{{{{{{{{{          [{{{{{{{{{{{{{{{{{{{{{{{{      *
*{{{{{{{{{{,,,{{{{{{{{{{{          [[{{{{{{{{{{{{{{{{{{{{{{{      *
*{{{{{{{{{,,,,,{{{{{{{{{{          [[[{{{{{{{{{{{{{{{{{{{{{{      *
*{{{{{{{{,,,,,,,{{{{{{{{{          [[{{{{{{{{{{{{{{{{{{{{{{{      *
*{{{{{{{{{{,,,{{{{{{{{{{{          [{{{{{{{{{{{{{{{{{{{{{{{{      *
*[[[[[[[[[[[[[[[[[[[[[[[[          ,,,,,,,,,,,,,,,,,,,,,,,,,      *
*[[[[[[[[[[[[[[[[[[[[[[[[          ,,,,,,,,,,,,,,,,,,,,,,,,,      *
*                                                                 *
*Welcome to arfedora-nvidiab Copyright 2016 version 1.0           *
*youssef sourani <youssef.m.sourani@gmail.com>                    *
*www.arfedora.blogspot.com                                        *
*This is python script to install Bumblebee + Nvidia or Nouveau   *
*fedora    link:http://spins.fedoraproject.org/                   *
*favorite  link:http://www.linuxac.org/forum/forum.php            *
*******************************************************************\n\n"""              

	for i in welcom:
		if i=="*":
			talwin(i,"blue",end='')
		elif i=="["  :
			talwin(i,"red",bg="red",end='')
		elif i=="~"  :
			talwin(i,"black",bg="black",end='')
		elif i=="{"  :
			talwin(i,"white",bg="white",end='')
		elif i==",":
			talwin(i,"green",bg="green",end='')
		else :
			talwin(i,"yellow",end='')


	
	
def install_kernel_devel():
	check=subprocess.call("sudo dnf -y  --best install  kernel-devel-$(uname -r) kernel-headers-$(uname -r)",shell=True)
	if check!=0:
		return main("Error Check Your Connection.")
		

def install_rpmfusionrepos():
	check=subprocess.call("sudo dnf install  --best -y --nogpgcheck  http://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm http://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm",shell=True)
	if check!=0:
		return main("Error Check Your Connection.")
		

def get_all_extensions():
	result=[]
	if os.path.isdir("%s/.local/share/gnome-shell/extensions"%home):
		for filee in os.listdir("%s/.local/share/gnome-shell/extensions"%home):
			if filee not in result:
				result.append(filee)

	if os.path.isdir("/usr/local/share/gnome-shell/extensions"):
		for filee in os.listdir("/usr/local/share/gnome-shell/extensions"):
			if filee not in result:
				result.append(filee)

	for filee in os.listdir("/usr/share/gnome-shell/extensions"):
		if filee not in result:
			result.append(filee)

	return result


def gnome_extensions():
	if os.getenv("XDG_CURRENT_DESKTOP")=="GNOME" :
		old_extension=get_all_extensions()
		os.makedirs("%s/.local/share/gnome-shell/extensions"%home,exist_ok=True)
		for f in os.listdir("%s/extensions"%dirname):
			if f not in old_extension:
				subprocess.call("cp -r %s/extensions/%s %s/.local/share/gnome-shell/extensions"%(dirname,f,home),shell=True)
				subprocess.call("gnome-shell-extension-tool -e  %s"%f,shell=True)
			
		check=subprocess.call("sudo dnf install  --best -y lm_sensors hddtemp",shell=True)
		if check!=0:
			return main("Error Check Your Connection.")
		subprocess.call("sudo sensors-detect --auto",shell=True)
	
		subprocess.call("dconf reset -f /org/gnome/shell/extensions/freon/",shell=True)
		subprocess.call("dconf write /org/gnome/shell/extensions/freon/gpu-utility \"\'bumblebee-nvidia-smi\'\"",shell=True)
	else:
		return main("Gnome Shell Desktop Not Found.")

	

def nouveau():
	install_kernel_devel()
	install_rpmfusionrepos()
	fedora_version=platform.linux_distribution()[1]
	arch=os.uname().machine
	remove_nvidia()
	
	check=subprocess.call("sudo dnf -y  --best install http://install.linux.ncsu.edu/pub/yum/itecs/public/bumblebee/fedora%s/noarch/bumblebee-release-1.2-1.noarch.rpm"%fedora_version,shell=True)
	if check!=0:
		return main("Error Check Your Connection.")
		
	if arch!="x86_64":	
		check=subprocess.call("sudo dnf -y  --best install  bumblebee-nouveau bbswitch-dkms  VirtualGL",shell=True)
		if check!=0:
			return main("Error Check Your Connection.")
	else:
		check=subprocess.call("sudo dnf -y  --best install  bumblebee-nouveau bbswitch-dkms VirtualGL VirtualGL.i686",shell=True)
		if check!=0:
			return main("Error Check Your Connection.")
			
	subprocess.call("sudo systemctl enable bumblebeed.service",shell=True)
	subprocess.call("sudo systemctl start bumblebeed.service",shell=True)
	
	subprocess.call("sudo usermod -a -G bumblebee $USER",shell=True)


def nvidia():
	install_kernel_devel()
	install_rpmfusionrepos()
	fedora_version=platform.linux_distribution()[1]
	arch=os.uname().machine
	remove_nouveau()
	
	check=subprocess.call("sudo dnf  -y  --best install http://install.linux.ncsu.edu/pub/yum/itecs/public/bumblebee-nonfree/fedora%s/noarch/bumblebee-nonfree-release-1.2-1.noarch.rpm"%fedora_version,shell=True)
	if check!=0:
		return main("Error Check Your Connection.")
	if arch!="x86_64":
		check=subprocess.call("sudo dnf -y  --best install bumblebee-nvidia bbswitch-dkms primus",shell=True)
		if check!=0:
			return main("Error Check Your Connection.")
	else:
		check=subprocess.call("sudo dnf -y  --best install bumblebee-nvidia bbswitch-dkms VirtualGL.x86_64 VirtualGL.i686 primus.x86_64 primus.i686",shell=True)
		if check!=0:
			return main("Error Check Your Connection.")

	subprocess.call("sudo touch /etc/sysconfig/nvidia/compile-nvidia-driver",shell=True)
	
	subprocess.call("sudo systemctl enable bumblebeed.service",shell=True)
	subprocess.call("sudo systemctl start bumblebeed.service",shell=True)

	subprocess.call("sudo usermod -a -G bumblebee $USER",shell=True)
	
	

def remove_nvidia():
	check=subprocess.call("sudo dnf -y remove bumblebee-nvidia bbswitch-dkms  bumblebee primus --setopt clean_requirements_on_remove=false",shell=True)
	if check!=0:
		return main("Remove Error.")
		
def remove_nouveau():
	check=subprocess.call("sudo dnf -y remove bumblebee-nouveau bbswitch-dkms bumblebee  --setopt clean_requirements_on_remove=false",shell=True)
	if check!=0:
		return main("Remove Error.")
		
def troubleshoot_nvidia_1():
	install_kernel_devel()
	install_rpmfusionrepos()
	fedora_version=platform.linux_distribution()[1]
	arch=os.uname().machine
	remove_nouveau()
	
	check=subprocess.call("sudo dnf  -y  --best reinstall http://install.linux.ncsu.edu/pub/yum/itecs/public/bumblebee-nonfree/fedora%s/noarch/bumblebee-nonfree-release-1.2-1.noarch.rpm"%fedora_version,shell=True)
	if check!=0:
		return main("Error Check Your Connection.")
	if arch!="x86_64":
		check=subprocess.call("sudo rm -r  /etc/sysconfig/nvidia/* ",shell=True)
		check=subprocess.call("sudo rm -r  /etc/sysconfig/nvidia/* ",shell=True)
		check=subprocess.call("sudo dnf -y  --best reinstall bumblebee-nvidia bbswitch-dkms VirtualGL primus",shell=True)
		
		if check!=0:
			return main("Error Check Your Connection.")
	else:
		check=subprocess.call("sudo dnf -y  --best reinstall bumblebee-nvidia bbswitch-dkms VirtualGL VirtualGL.i686 primus primus.i686",shell=True)
		if check!=0:
			return main("Error Check Your Connection.")
			
	
	subprocess.call("sudo systemctl enable bumblebeed.service",shell=True)
	subprocess.call("sudo systemctl start bumblebeed.service",shell=True)
	subprocess.call("sudo systemctl enable dkms.service",shell=True)
	subprocess.call("sudo touch /etc/sysconfig/nvidia/compile-nvidia-driver",shell=True)
	subprocess.call("sudo usermod -a -G bumblebee $USER",shell=True)
	subprocess.call("sudo bumblebee-nvidia --debug --force",shell=True)
	
	
def troubleshoot_nvidia_2():
	subprocess.call("echo \"options bbswitch load_state=-1 unload_state=1\" |sudo tee /etc/modprobe.d/50-bbswitch.conf",shell=True)
	talwin("Please do not power off or unplug your machine.\n","red")
	subprocess.call(" sudo dracut -f",shell=True)
	
def undo_troubleshoot_nvidia_2():
	if os.path.isfile("/etc/modprobe.d/50-bbswitch.conf"):
		subprocess.call("sudo rm /etc/modprobe.d/50-bbswitch.conf",shell=True)
		talwin ("Please do not power off or unplug your machine.\n","red")
		subprocess.call(" sudo dracut -f",shell=True)
	else:
		return main("Nothing To Do.")
	
def troubleshoot_nouveau():
	install_kernel_devel()
	install_rpmfusionrepos()
	fedora_version=platform.linux_distribution()[1]
	arch=os.uname().machine
	remove_nvidia()
	
	check=subprocess.call("sudo dnf -y  --best reinstall http://install.linux.ncsu.edu/pub/yum/itecs/public/bumblebee/fedora%s/noarch/bumblebee-release-1.2-1.noarch.rpm"%fedora_version,shell=True)
	if check!=0:
		return main("Error Check Your Connection.")
		
	if arch!="x86_64":	
		check=subprocess.call("sudo dnf -y  --best reinstall  bumblebee-nouveau bbswitch-dkms  VirtualGL",shell=True)
		if check!=0:
			return main("Error Check Your Connection.")
	else:
		check=subprocess.call("sudo dnf -y  --best reinstall  bumblebee-nouveau bbswitch-dkms VirtualGL VirtualGL.i686",shell=True)
		if check!=0:
			return main("Error Check Your Connection.")
			
	subprocess.call("sudo systemctl enable bumblebeed.service",shell=True)
	subprocess.call("sudo systemctl start bumblebeed.service",shell=True)
	
	subprocess.call("sudo usermod -a -G bumblebee $USER",shell=True)
	
	
def msg(m):
	while True:
		subprocess.call("clear")
		print()
		talwin (m,"red")
		talwin("\nY To Continue || N To Back || Q To Quit : \n-","blue",end="")
		y_n=input()
		if y_n.strip()=="Y" or y_n.strip()=="y":
			break
		elif y_n.strip()=="N" or y_n.strip()=="n":
			return main()
		elif y_n.strip()=="q" or y_n.strip()=="Q":
			sys.exit("\nBye...\n")
			
def main(ms=""):
	if len(ms)!=0:
		ms="((((%s))))"%ms
	while True:
		welcome()
		talwin("Do You Want Install Open Source Driver Or Closed Source Driver?\n","blue")
		print("1-Install Nouveau Open Source Driver.\t\t\t\t\t\t 2-Install Nvidia Closed Source Driver.\n\n\n3-Level 1 Troubleshoot Nvidia Closed Source Driver\t\t\t\t 4-Level 2 Troubleshoot Nvidia Closed Source Driver\n\n\n5-Undo Level 2 Troubleshoot Nvidia Closed Source Driver.\t\t\t 6-Troubleshoot Nouveau Open Source Driver\n\n\n7-Remove Nouveau Open Source Driver.                                            8-Remove Nvidia CLosed Source Driver.\n\n\n9-Remove All Driver.                                                            10-Install Gnome Shell Extentios.")
		talwin("\n%s\n"%ms,"red")
		talwin("Choice Number || q to Exit.\n-","blue",end="")
		answer=input().strip()
		ms=""
		if answer.strip()=="1":
			msg("Remove Nvidia Closed Source Driver || Install Nouveau Open Source Driver.")
			nouveau()
			return main("Finish Reboot Your Machine.")
		elif answer=="2":
			msg("Remove Nouveau Open Source Driver || Install Nvidia Closed Source Driver.")
			nvidia()
			return main("Finish Reboot Your Machine.")
			
			
		elif answer=="3":
			msg("Remove Nouveau Open Source Driver ||Reinstall Nvidia Closed Source Driver.")
			troubleshoot_nvidia_1()
			return main("Finish Reboot Your Machine.")
		elif answer=="4":
			msg("Add Option \"options bbswitch load_state=-1 unload_state=1\" To /etc/modprobe.d/50-bbswitch.conf And Rebuild initramfs.")
			troubleshoot_nvidia_2()
			return main("Finish Reboot Your Machine.")
		elif answer=="5":
			msg("Remove File /etc/modprobe.d/50-bbswitch.conf And Rebuild initramfs.")
			undo_troubleshoot_nvidia_2()
			return main("Finish Reboot Your Machine.")
		elif answer=="6":
			msg("Remove Nvidia Closed Source Driver || Reinstall Nouveau Open Source Driver.")
			troubleshoot_nouveau()
			return main("Finish Reboot Your Machine.")
			
			
		elif answer=="7":
			msg("Remove Nouveau Open Source Driver.")
			remove_nouveau()
			return main("Finish Reboot Your Machine.")
		elif answer=="8":
			msg("Remove Nvidia Closed Source Driver.")
			remove_nvidia()
			return main("Finish Reboot Your Machine.")
		elif answer=="9":
			msg("Remove Nouveau And Nvidia Drivers.")
			remove_nouveau()
			remove_nvidia()
			return main("Finish Reboot Your Machine.")
			
		elif answer=="10":
			msg("Install Gnome Shell Extentions.")
			gnome_extensions()
			return main("Finish Reboot Your Machine.")
			
		elif answer.strip()=="q" or answer.strip()=="Q":
			sys.exit("\nBye...\n")
		
	

if __name__=="__main__":
	main()
	
