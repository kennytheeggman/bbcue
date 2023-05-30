import re 
from mimetypes import guess_type

from .component import component, class_file, file, rid
from flask import Response

class RegexComponent:

	def __init__(self, regex, match_props=r'\$"(.*?)"', match_params=r'\&"(.*?)"', repl_props=r'{props[\1]}', repl_params=r'{params[\1]}'):
		
		# string to be regex matched
		self.regex = regex

		# regex pattern for matching props and params
		self.match_props = match_props
		self.match_params = match_params

		# regex pattern for replacing props and params
		self.repl_props = repl_props
		self.repl_params = repl_params

		# ensure number of groups in regex sequence are correct
		if re.compile(self.match_props).groups < 1:
			raise GroupException("No groups found in match_props")
		elif re.compile(self.match_props).groups > 1:
			raise GroupException("Too many groups found in match_props")
		elif re.compile(self.match_params).groups < 1:
			raise GroupException("No groups found in match_params")
		elif re.compile(self.match_params).groups > 1:
			raise GroupException("Too many groups found in match_params")
		
		# identify all properties and parameters
		self.props = re.findall(self.match_props, self.regex)
		self.params = re.findall(self.match_params, self.regex)
		
	@classmethod
	def from_file(cls, file_path):

		# open file and create object from file contents
		f = open(file_path)
		return RegexComponent(f.read())
	
	@classmethod
	def from_folder(cls, path, props, exclude=[]):

		# imports for acquiring file names
		from os import listdir
		from os.path import isfile, join

		# get files
		files = [f for f in listdir(path) if isfile(join(path, f)) and f not in exclude]
		files.sort()

		# identify candidates for primary files
		main_candidates = [valid for valid in files if valid.startswith("index") or valid.startswith("main")]

		# get first main candidate if main candidate exists, else get first alphabetical file
		main = main_candidates[0] if len(main_candidates) > 0 else files[0]

		# get identified props
		pr = {}

		# if any prop is not added, replace it with a random 8 letter sequence
		for f in files:

			rc = RegexComponent.from_file(f"{path}/{f}")

			for prop in rc.props:

				pr |= {prop: rid()}

		# remove main from the files to be added to routing
		files.remove(main)

		# get component from the main file using correct props
		component = RegexComponent.from_file(f"{path}/{main}").get_component(pr | props)

		# for each non-main file
		for name in files:
			
			# create a classfile with correct contents
			@class_file(component, f"/{path}/{name}")
			def f(props):

				unformatted = str(RegexComponent.from_file(join(path, name)))
			
				return str(RegexComponent.from_file(join(path, name))).format(props = pr | props)
			
			# infer mimetype by file extension
			@file(f"/{path}/{name}")
			def f_ext(content):

				resp = Response(content)

				if guess_type(join(path, name))[0]:

					resp.headers["Content-Type"] = guess_type(join(path, name))[0]
				
				return lambda: resp
		
		return component
	
	def __str__(self):

		# replace single curly braces with doubles for string formatting consistency
		escaped = re.sub(r'}', r'}}', re.sub(r'{', r'{{', self.regex))

		# substitute the pattern
		p1 = re.sub(self.match_props, self.repl_props, escaped)
		p2 = re.sub(self.match_params, self.repl_params, p1)

		return p2
	
	def get_component(self, params):

		# create a component with parameters
		@component(params)
		def comp(params, props):

			return str(self).format(props=props, params=params)
		
		return comp


class GroupException(Exception):

	pass
