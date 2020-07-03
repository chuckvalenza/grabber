#!/usr/bin/env python3

# ---------------------------------------------------------------------------- #
#                                  autodl.py                                   #
#                                                                              #
# Lists signal files in remote directory, downloads the targets, then destroys #
# the signal file                                                              #
# ---------------------------------------------------------------------------- #

import sys
from os import system, getpid, path, unlink
from paramiko import SSHClient, AutoAddPolicy, RSAKey, SSHConfig
from paramiko.auth_handler import AuthenticationException, SSHException
from loguru import logger
from os.path import expanduser

# ---------------------------------------------------------------------------- #
#                              global variables                                #
# ---------------------------------------------------------------------------- #

DL_DIR = "./download/"
SSH_CONFIG = expanduser("~/") + ".ssh/config"
SSH_KEY = expanduser("~/") + ".ssh/id_rsa"
L_HOSTNAME = "localhost"
GRABBERS = [L_HOSTNAME]

# ---------------------------------------------------------------------------- #
#                                  logging                                     #
# ---------------------------------------------------------------------------- #

logger.add(sys.stderr,
           format="{time} {level} {message}",
           filter="client",
           level="ERROR")

# ---------------------------------------------------------------------------- #
#                                RemoteClient                                  #
# ---------------------------------------------------------------------------- #

class RemoteClient:
	def __init__(self, host, ssh_config, ssh_key_filepath):
		ssh_config = SSHConfig.from_path(ssh_config)
		ssh_tgt = ssh_config.lookup(host)
		self.host = ssh_tgt.get("hostname")
		self.user = ssh_tgt.get("user")
		self.ssh_key_filepath = ssh_key_filepath
		self.client = None

	def __get_ssh_key(self):
		try:
			self.ssh_key = RSAKey.from_private_key_file(self.ssh_key_filepath)
		except SSHException as error:
			logger.error(error)
		return self.ssh_key

	def __connect(self):
		try:
			self.client = SSHClient()
			self.client.load_system_host_keys()
			self.client.set_missing_host_key_policy(AutoAddPolicy())
			self.client.connect(self.host,
								username=self.user,
								key_filename=self.ssh_key_filepath,
								look_for_keys=True,
								timeout=5000)
			self.sftp = self.client.open_sftp()
		except AuthenticationException as error:
			logger.error(error)
			raise error
		finally:
			return self.client

	def __annotate_grab(self, sig_file):
		if self.client is None:
			self.client = self.__connect()
		self.client.exec_command("echo " + L_HOSTNAME + " >> " + sig_file)

	def __check_grab(self, sig_file):
		if self.client is None:
			self.client = self.__connect()
		stdin, stdout, stderr = self.client.exec_command("cat " + sig_file)
		stdout.channel.recv_exit_status()
		return stdout.readlines()

	def disconnect(self):
		self.client.close()

	def grab(self, category, sig_path, tgt_path):
		if self.client is None:
			self.client = self.__connect()
		for i in self.sftp.listdir(sig_path):
			if i is not "\n":
				data_file = tgt_path + i
				lstatout = str(self.sftp.lstat(data_file)).split()[0]
				cmd = ""

				data_file = data_file.replace(" ", "\ ")
				data_file = data_file.replace("'", "\\'")
				data_file = data_file.replace('"', '\\\\\\"')

				sig_file = sig_path + i
				sig_file = sig_file.replace(" ", "\ ")
				sig_file = sig_file.replace("'", "\\'")
				sig_file = sig_file.replace("(", "\(")
				sig_file = sig_file.replace(")", "\)")
				sig_file = sig_file.replace("[", "\[")
				sig_file = sig_file.replace("]", "\]")
				sig_file = sig_file.replace("&", "\&")

				# decide whether to use mirror or pget
				if "d" in lstatout:
					cmd = 'lftp -e "open ' + self.host + \
						'; mirror -c --use-pget-n=10 ' + data_file + '; exit"'
				else:
					cmd = 'lftp -e "open ' + self.host + \
						'; pget -n 10 ' + data_file + '; exit"'

				contents_holder = []
				sig_contents = self.__check_grab(sig_file)
				for s in sig_contents:
					contents_holder.append(s.replace("\n", ""))
				sig_contents = contents_holder

				if not any(L_HOSTNAME in x for x in sig_contents):
					print(cmd)
					if system(cmd) == 0:
						self.__annotate_grab(sig_file)
						sig_contents.append(L_HOSTNAME)
				else:
					print("File already grabbed from this client...")

				if all(g in sig_contents for g in GRABBERS):
					print("All grabbers have fetched, removing.")
					self.client.exec_command("rm -r " + sig_file)
				else:
					print("Other grabbers still need to fetch.")

	def execute_commands(self, commands):
		if self.client is None:
			self.client = self.__connect()
		for cmd in commands:
			stdin, stdout, stderr = self.client.exec_command(cmd)
			stdout.channel.recv_exit_status()
			print(stdout.readlines())

# ---------------------------------------------------------------------------- #
#                                  execution                                   #
# ---------------------------------------------------------------------------- #

def grab(remote_host, categories):
	for category in categories:
		target_dir = signal_dir = DL_DIR
		target_dir += "data/" + category + "/"
		signal_dir += "finished/" + category + "/"
		remote_cxn = RemoteClient(remote_host, SSH_CONFIG, SSH_KEY)
		remote_cxn.grab(category, signal_dir, target_dir)
	remote_cxn.disconnect()

def main():
	remote_host = sys.argv[1]
	categories = sys.argv[2:]

	pid = str(getpid())
	pidfile = "/tmp/grabber.pid"

	if path.isfile(pidfile):
		print("grabber is already running, exiting")
		sys.exit()
	open(pidfile, 'w').write(pid)
	try:
		grab(remote_host, categories)
	finally:
		unlink(pidfile)

main()

