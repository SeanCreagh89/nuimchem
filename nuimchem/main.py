import os
import re
import time
import jinja2
import webapp2

from google.appengine.ext import db
from datetime import datetime

template_directory = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_directory), autoescape = True)

# regular expressions and validation functions
USER_RE = re.compile(r"^[ a-zA-Z0-9_-]{8,20}$")
def valid_username(username):
	return username and USER_RE.match(username)

PASS_RE = re.compile(r"^[a-zA-Z0-9_-]{8,20}$")
def valid_password(password):
	return password and PASS_RE.match(password)

EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
def valid_email(email):
	return email and EMAIL_RE.match(email)

VALID_CAS_RE = re.compile(r"^\d{1,6}-\d{1,6}-\d{1,6}$")
def valid_cas(cas):
	return cas and VALID_CAS_RE.match(cas)

VALID_NUM_RE = re.compile(r"^[0-9]+$")
def valid_num(num):
	return num and VALID_NUM_RE.match(num)

VALID_DEC_RE = re.compile(r"^[0-9]+\.[0-9]+$")
def valid_dec(dec):
	return dec and VALID_DEC_RE.match(dec)

# gql database models
class User(db.Model):
	username = db.StringProperty(required = True)
	email = db.StringProperty(required = True)
	password = db.StringProperty(required = True)
	admin = db.StringProperty(required = False)
	created = db.DateTimeProperty(auto_now_add = True)

class Registration(db.Model):
	registration = db.BooleanProperty(required = True)

class CAS(db.Model):
	ID = db.StringProperty(required = True)
	cas_no = db.StringProperty(required = True)
	name = db.StringProperty(required = True)
	owner = db.StringProperty(required = True)
	group = db.StringProperty(required = True)
	int_quant = db.StringProperty(required = True)
	cur_quant = db.StringProperty(required = True)
	measure = db.StringProperty(required = True)
	msds = db.LinkProperty(required = True)
	classification1 = db.StringProperty(required = True)
	classification2 = db.StringProperty(required = True)
	classification3 = db.StringProperty(required = True)
	classification4 = db.StringProperty(required = True)
	classification5 = db.StringProperty(required = True)
	classification6 = db.StringProperty(required = True)
	symbol = db.StringProperty(required = False)
	container = db.StringProperty(required = True)
	location = db.StringProperty(required = True)
	sublocation = db.StringProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

class Novel(db.Model):
	ID = db.StringProperty(required = True)
	name = db.StringProperty(required = True)
	owner = db.StringProperty(required = True)
	group = db.StringProperty(required = True)
	int_quant = db.StringProperty(required = True)
	cur_quant = db.StringProperty(required = True)
	measure = db.StringProperty(required = True)
	classification1 = db.StringProperty(required = True)
	classification2 = db.StringProperty(required = True)
	classification3 = db.StringProperty(required = True)
	classification4 = db.StringProperty(required = True)
	classification5 = db.StringProperty(required = True)
	classification6 = db.StringProperty(required = True)
	symbol = db.StringProperty(required = False)
	description = db.TextProperty(required = True)
	location = db.StringProperty(required = True)
	sublocation = db.StringProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

class Waste(db.Model):
	ID = db.StringProperty(required = True)
	owner = db.StringProperty(required = True)
	group = db.StringProperty(required = False)
	measure = db.StringProperty(required = True)
	quantity = db.StringProperty(required = True)
	waste_type = db.StringProperty(required = True)
	symbol = db.StringProperty(required = False)
	description = db.TextProperty(required = False)
	location = db.StringProperty(required = True)
	sublocation = db.StringProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

class CMR(db.Model):
	ID = db.StringProperty(required = True)
	cas_no = db.StringProperty(required = True)
	name = db.StringProperty(required = True)
	classification = db.StringProperty(required = True)
	users = db.StringProperty(required = True)
	action = db.StringProperty(required = True)
	created  = db.DateTimeProperty(auto_now_add = True)

# default application handler
class AppHandler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_temp(self, template, **params):
		temp = jinja_env.get_template(template)
		return temp.render(params)

	def render(self, template, **kw):
		self.write(self.render_temp(template, **kw))

# login handler
class LoginHandler(AppHandler):
	def get(self):
		error = self.request.get('login')
		params = dict(error = error)
		params['login_user_error'] = "%s" % error
		self.render('login.html', **params)

	def post(self):
		button = int(self.request.get('button'))
		error = 0

		# login
		if button == 1:
			user = self.request.get('login_user')
			password = self.request.get('login_password')
			params = dict(user = user, password = password)

			if not valid_username(user):
				if not valid_email(user):
					if user == "":
						params['login_user_error'] = "Field Empty."
					else:
						params['login_user_error'] = "Invalid Username."
					error = 1
				else:
					query = db.GqlQuery("SELECT * FROM User WHERE email =:e", e = user)
					instance = query.get()

					if not instance:
						params['login_user_error'] = "Incorrect Email."
						error = 1
					elif instance.password != password:
						params['login_password_error'] = "Incorrect Password."
						error = 1
			else:
				query = db.GqlQuery("SELECT * FROM User WHERE username =:u", u = user)
				instance = query.get()

				if not instance:
					params['login_user_error'] = "Incorrect Username."
					error = 1
				elif instance.password != password:
					params['login_password_error'] = "Incorrect Password."
					error = 1

			if not valid_password(password):
				if password == "":
					params['login_password_error'] = "Field Empty."
				else:
					params['login_password_error'] = "Invalid Password."
				error = 1

			if error == 1:
				self.render('login.html', **params)
			if error == 0:
				if valid_username(user):
					query = db.GqlQuery("SELECT * FROM User WHERE username =:u", u = user)
					instance = query.get()

					nuimce = str(instance.email)
					self.response.headers.add_header('Set-Cookie', 'nuimce = %s; Path=/' % nuimce)

					if instance.admin == "ADMIN":
						self.redirect('/unit2/admin')
					else:
						self.redirect('/unit2/search')

				if valid_email(user):
					query = db.GqlQuery("SELECT * FROM User WHERE email =:u", u = user)
					instance = query.get()

					nuimce = str(user)
					self.response.headers.add_header('Set-Cookie', 'nuimce = %s; Path=/' % nuimce)

					if instance.admin == "ADMIN":
						self.redirect('/unit2/admin')
					else:
						self.redirect('/unit2/search')

		if button == 2:
			reg = db.GqlQuery("SELECT * FROM Registration")
			instance = reg.get()

			if not instance or instance.registration:
				username = self.request.get('register_username')
				email = self.request.get('register_email')
				password = self.request.get('register_password')
				params = dict(username = username, email = email, password = password)

				if not valid_username(username):
					if username == "":
						params['register_username_error'] = "Field Empty."
					else:
						params['register_username_error'] = "Invalid Username."
					error = 1
				else:
					query = db.GqlQuery("SELECT * FROM User WHERE username =:u", u = username)
					instance = query.get()

					if instance:
						params['register_username_error'] = "Username Already In Use."
						error = 1

				if not valid_email(email):
					if email == "":
						params['register_email_error'] = "Field Empty."
					else:
						params['register_email_error'] = "Invalid Email."
					error = 1
				else:
					query = db.GqlQuery("SELECT * FROM User WHERE email =:e", e = email)
					instance = query.get()

					if instance:
						params['register_email_error'] = "Email Already In Use."
						error = 1

				if not valid_password(password):
					if password == "":
						params['register_password_error'] = "Field Empty."
					else:
						params['register_password_error'] = "Invalid Password."
					error = 1

				if error == 1:
					self.render('login.html', **params)

				if error == 0:
					user = User(username = username, email = email, password = password)
					user.put()

					params['response'] = "Successfully Registered."
					self.render('login.html', **params)
			else:
				error = ""
				params = dict(error = error)
				params['register_username_error'] = "Registeration Closed."
				self.render('login.html', **params)

# controller handler
class ControllerHandler(AppHandler):
	def get(self):
		query = db.GqlQuery("SELECT * FROM Registration")
		instance = query.get()

		if not instance:
			reg = Registration(registration = True)
			reg.put()

		success = ""
		params = dict(success = success)
		success = self.request.get('success')
		params['success'] = "%s" % success

		users = db.GqlQuery("SELECT * FROM User ORDER BY username ASC")
		chemicals = db.GqlQuery("SELECT * FROM CAS ORDER BY ID ASC")
		novel = db.GqlQuery("SELECT * FROM Novel ORDER BY ID ASC")
		waste = db.GqlQuery("SELECT * FROM Waste ORDER BY ID ASC")
		reg = db.GqlQuery("SELECT * FROM Registration")

		self.render('admin.html', users = users, chemicals = chemicals, novel = novel, waste = waste, reg = reg, **params)

	def post(self):
		button = int(self.request.get('button'))
		email = self.request.cookies.get('nuimce', '0')
		error = 0

		if email == "":
			self.redirect('/?login=Please Login.')
		else:
			# new admin
			if button == 1:
				username = self.request.get('username')
				email = self.request.get('email')
				password = self.request.get('password')
				params = dict(username = username, email = email, password = password)

				if not valid_username(username):
					if username == "":
						params['username_error'] = "Field Empty."
					else:
						params['username_error'] = "Invalid Username."
					error = 1
				else:
					query = db.GqlQuery("SELECT * FROM User WHERE username =:u", u = username)
					instance = query.get()

					if instance:
						params['username_error'] = "Username Already In Use."
						error = 1

				if not valid_email(email):
					if email == "":
						params['email_error'] = "Field Empty."
					else:
						params['email_error'] = "Invalid Email."
					error = 1

				if not valid_password(password):
					if password == "":
						params['password_error'] = "Field Empty."
					else:
						params['password_error'] = "Invalid Password."
					error = 1

				if error == 1:
					users = db.GqlQuery("SELECT * FROM User ORDER BY username ASC")
					chemicals = db.GqlQuery("SELECT * FROM CAS ORDER BY ID ASC")
					novel = db.GqlQuery("SELECT * FROM Novel ORDER BY ID ASC")
					waste = db.GqlQuery("SELECT * FROM Waste ORDER BY ID ASC")
					reg = db.GqlQuery("SELECT * FROM Registration")
					self.render('admin.html', users = users, chemicals = chemicals, novel = novel, waste = waste, reg = reg, **params)
				if error == 0:
					admin = "ADMIN"
					user = User(username = username, email = email, password = password, admin = admin)
					user.put()
					self.redirect("/unit2/admin?success=Successfully Uploaded.")

			# registration
			if button == 2:
				toggle = self.request.get('registration')

				if toggle:
					toggle = True
				else:
					toggle = False

				query = db.GqlQuery("SELECT * FROM Registration")
				instance = query.get()

				if not instance:
					reg = Registration(registration = toggle)
					reg.put()
				else:
					instance.registration = toggle
					instance.put()

				self.redirect('/unit2/admin')

			# delete user
			if button == 10:
				user = self.request.get('user')
				query = db.GqlQuery("SELECT * FROM User WHERE username =:u", u = user)
				instance = query.get()
				username = instance.username
				db.delete(instance)
				self.redirect('/unit2/admin')

			if button == 11:
				ID = self.request.get('id')
				cas = db.GqlQuery("SELECT * FROM CAS WHERE ID =:i", i = ID)
				cas_instance = cas.get()

				if cas_instance:
					db.delete(cas_instance)
				else:
					nov = db.GqlQuery("SELECT * FROM Novel WHERE ID =:i", i = ID)
					nov_instance = nov.get()

					if nov_instance:
						db.delete(nov_instance)
					else:
						waste = db.GqlQuery("SELECT * FROM Waste WHERE ID =:i", i = ID)
						waste_instance = waste.get()

						if waste_instance:
							db.delete(waste_instance)

				self.redirect('/unit2/admin')

			# logout
			if button == 66:
				self.response.headers.add_header('Set-Cookie', 'nuimce =; Path=/')
				self.redirect('/')

# search handler
class SearchHandler(AppHandler):
	def get(self):
		self.render('search.html')

	def post(self):
		button = int(self.request.get('button'))
		error = 0

		# search for chemical
		if button == 1:
			query_type = self.request.get('query')
			search = self.request.get('search')
			dropdown = self.request.get('dropdown')
			params = dict(search = search, dropdown = dropdown)

			if dropdown == "filter":
				params['filter_error'] = "No Filter Selected."
				error = 1

			if query_type == "select search type":
				params['query_error'] = "Please Select Query Type."
				error = 1

			# search by cas
			if query_type == "Search by CAS":
				if dropdown == "All":
					if search != "":
						params['search_error'] = "No Input Required."
					else:
						query = db.GqlQuery("SELECT * FROM CAS")
						instance = query.get()

						if not instance:
							params['filter_error'] = "No Chemicals Exist."
							error = 1

				if dropdown == "Name":
					if search == "":
						params['search_error'] = "Field Empty."
						error = 1
					else:
						query = db.GqlQuery("SELECT * FROM CAS WHERE name =:n", n = search)
						instance = query.get()

						if not instance:
							params['search_error'] = "Chemical/s Not Found."
							error = 1

				if dropdown == "Owner":
					if search == "":
						params['search_error'] = "Field Empty."
						error = 1
					else:
						query = db.GqlQuery("SELECT * FROM CAS WHERE owner =:o", o = search)
						instance = query.get()

						if not instance:
							params['search_error'] = "Chemical/s Not Found."
							error = 1

				if dropdown == "Group":
					if search == "":
						params['search_error'] = "Field Empty."
						error = 1
					else:
						query = db.GqlQuery("SELECT * FROM CAS WHERE group =:g", g = search)
						instance = query.get()

						if not instance:
							params['search_error'] = "Chemical/s Not Found."
							error = 1

				if dropdown == "Classification":
					if search == "":
						params['search_error'] = "Field Empty."
						error = 1
					else:
						query = db.GqlQuery("SELECT * FROM CAS WHERE classification1 =:c", c = search)
						instance = query.get()

						if not instance:
							query = db.GqlQuery("SELECT * FROM CAS WHERE classification2 =:c", c = search)
							instance = query.get()

							if not instance:
								query = db.GqlQuery("SELECT * FROM CAS WHERE classification3 =:c", c = search)
								instance = query.get()

								if not instance:
									query = db.GqlQuery("SELECT * FROM CAS WHERE classification4 =:c", c = search)
									instance = query.get()

									if not instance:
										query = db.GqlQuery("SELECT * FROM CAS WHERE classification5 =:c", c = search)
										instance = query.get()

										if not instance:
											query = db.GqlQuery("SELECT * FROM CAS WHERE classification6 =:c", c = search)
											instance = query.get()

											if not instance:
												params['search_error'] = "Chemical/s Not Found."
												error = 1

				if dropdown == "Location":
					if search == "":
						params['search_error'] = "Field Empty."
						error = 1
					else:
						query = db.GqlQuery("SELECT * FROM CAS WHERE location =:l", l = search)
						instance = query.get()

						if not instance:
							params['search_error'] = "Chemical/s Not Found."
							error = 1

				if dropdown == "Sub Location":
					if search == "":
						params['search_error'] = "Field Empty."
						error = 1
					else:
						query = db.GqlQuery("SELECT * FROM CAS WHERE sublocation =:s", s = search)
						instance = query.get()

						if not instance:
							params['search_error'] = "Chemical/s Not Found."
							error = 1

			# search by novel
			if query_type == "Search by Novel Compound":
				if dropdown == "All":
					if search != "":
						params['search_error'] = "No Input Required."
					else:
						query = db.GqlQuery("SELECT * FROM Novel")
						instance = query.get()

						if not instance:
							params['filter_error'] = "No Chemicals Exist."
							error = 1

				if dropdown == "Name":
					if search == "":
						params['search_error'] = "Field Empty."
						error = 1
					else:
						query = db.GqlQuery("SELECT * FROM Novel WHERE name =:n", n = search)
						instance = query.get()

						if not instance:
							params['search_error'] = "Chemical/s Not Found."
							error = 1

				if dropdown == "Owner":
					if search == "":
						params['search_error'] = "Field Empty."
						error = 1
					else:
						query = db.GqlQuery("SELECT * FROM Novel WHERE owner =:o", o = search)
						instance = query.get()

						if not instance:
							params['search_error'] = "Chemical/s Not Found."
							error = 1

				if dropdown == "Group":
					if search == "":
						params['search_error'] = "Field Empty."
						error = 1
					else:
						query = db.GqlQuery("SELECT * FROM Novel WHERE group =:g", g = search)
						instance = query.get()

						if not instance:
							params['search_error'] = "Chemical/s Not Found."
							error = 1

				if dropdown == "Classification":
					if search == "":
						params['search_error'] = "Field Empty."
						error = 1
					else:
						query = db.GqlQuery("SELECT * FROM Novel WHERE classification1 =:c", c = search)
						instance = query.get()

						if not instance:
							query = db.GqlQuery("SELECT * FROM Novel WHERE classification2 =:c", c = search)
							instance = query.get()

							if not instance:
								query = db.GqlQuery("SELECT * FROM Novel WHERE classification3 =:c", c = search)
								instance = query.get()

								if not instance:
									query = db.GqlQuery("SELECT * FROM Novel WHERE classification4 =:c", c = search)
									instance = query.get()

									if not instance:
										query = db.GqlQuery("SELECT * FROM Novel WHERE classification5 =:c", c = search)
										instance = query.get()

										if not instance:
											query = db.GqlQuery("SELECT * FROM Novel WHERE classification6 =:c", c = search)
											instance = query.get()

											if not instance:
												params['search_error'] = "Chemical/s Not Found."
												error = 1

				if dropdown == "Location":
					if search == "":
						params['search_error'] = "Field Empty."
						error = 1
					else:
						query = db.GqlQuery("SELECT * FROM Novel WHERE location =:l", l = search)
						instance = query.get()

						if not instance:
							params['search_error'] = "Chemical/s Not Found."
							error = 1

				if dropdown == "Sub Location":
					if search == "":
						params['search_error'] = "Field Empty."
						error = 1
					else:
						query = db.GqlQuery("SELECT * FROM Novel WHERE sublocation =:s", s = search)
						instance = query.get()

						if not instance:
							params['search_error'] = "Chemical/s Not Found."
							error = 1

			email = self.request.cookies.get('nuimce', '0')

			if email == "":
				error = 2

			if error == 1:
				self.render('search.html', **params)

			if error == 2:
				self.redirect('/?login=Please Login.')

			if error == 0:
				if query_type == "Search by CAS":
					if dropdown == "All":
						query = db.GqlQuery("SELECT * FROM CAS ORDER BY name ASC")
						self.render('cas-results.html', query = query, **params)

					if dropdown == "Name":
						query = db.GqlQuery("SELECT * FROM CAS WHERE name =:n ORDER BY created ASC", n = search)
						self.render('cas-results.html', query = query)

					if dropdown == "Owner":
						query = db.GqlQuery("SELECT * FROM CAS WHERE owner =:o ORDER BY created ASC", o = search)
						self.render('cas-results.html', query = query)

					if dropdown == "Group":
						query = db.GqlQuery("SELECT * FROM CAS WHERE group =:g ORDER BY created ASC", g = search)
						self.render('cas-results.html', query = query)

					if dropdown == "Classification":
						query1 = db.GqlQuery("SELECT * FROM CAS WHERE classification1 =:c ORDER BY created ASC", c = search)
						query2 = db.GqlQuery("SELECT * FROM CAS WHERE classification2 =:c ORDER BY created ASC", c = search)
						query3 = db.GqlQuery("SELECT * FROM CAS WHERE classification3 =:c ORDER BY created ASC", c = search)
						query4 = db.GqlQuery("SELECT * FROM CAS WHERE classification4 =:c ORDER BY created ASC", c = search)
						query5 = db.GqlQuery("SELECT * FROM CAS WHERE classification5 =:c ORDER BY created ASC", c = search)
						query6 = db.GqlQuery("SELECT * FROM CAS WHERE classification6 =:c ORDER BY created ASC", c = search)
						self.render('cas-class-results.html', query1 = query1, query2 = query2, query3 = query3, query4 = query4, query5 = query5, query6 = query6)

					if dropdown == "Location":
						query = db.GqlQuery("SELECT * FROM CAS WHERE location =:l ORDER BY created ASC", l = search)
						self.render('cas-results.html', query = query)

					if dropdown == "Sub Location":
						query = db.GqlQuery("SELECT * FROM CAS WHERE sublocation =:s ORDER BY created ASC", s = search)
						self.render('cas-results.html', query = query)

				if query_type == "Search by Novel Compound":
					if dropdown == "All":
						query = db.GqlQuery("SELECT * FROM Novel ORDER BY name ASC")
						self.render('novel-results.html', query = query, **params)

					if dropdown == "Name":
						query = db.GqlQuery("SELECT * FROM Novel WHERE name =:n ORDER BY created ASC", n = search)
						self.render('novel-results.html', query = query)

					if dropdown == "Owner":
						query = db.GqlQuery("SELECT * FROM Novel WHERE owner =:o ORDER BY created ASC", o = search)
						self.render('novel-results.html', query = query)

					if dropdown == "Group":
						query = db.GqlQuery("SELECT * FROM Novel WHERE group =:g ORDER BY created ASC", g = search)
						self.render('novel-results.html', query = query)

					if dropdown == "Classification":
						query1 = db.GqlQuery("SELECT * FROM Novel WHERE classification1 =:c ORDER BY created ASC", c = search)
						query2 = db.GqlQuery("SELECT * FROM Novel WHERE classification2 =:c ORDER BY created ASC", c = search)
						query3 = db.GqlQuery("SELECT * FROM Novel WHERE classification3 =:c ORDER BY created ASC", c = search)
						query4 = db.GqlQuery("SELECT * FROM Novel WHERE classification4 =:c ORDER BY created ASC", c = search)
						query5 = db.GqlQuery("SELECT * FROM Novel WHERE classification5 =:c ORDER BY created ASC", c = search)
						query6 = db.GqlQuery("SELECT * FROM Novel WHERE classification6 =:c ORDER BY created ASC", c = search)
						self.render('nov-class-results.html', query1 = query1, query2 = query2, query3 = query3, query4 = query4, query5 = query5, query6 = query6)

					if dropdown == "Location":
						query = db.GqlQuery("SELECT * FROM Novel WHERE location =:l ORDER BY created ASC", l = search)
						self.render('novel-results.html', query = query)

					if dropdown == "Sub Location":
						query = db.GqlQuery("SELECT * FROM Novel WHERE sublocation =:s ORDER BY created ASC", s = search)
						self.render('novel-results.html', query = query)

		# delete chemical
		if button == 2:
			chemical = self.request.get('id')
			email = self.request.cookies.get('nuimce', '')
			params = dict(chemical = chemical, email = email)

			query_user = db.GqlQuery("SELECT * FROM User WHERE email =:e", e = email)
			user = query_user.get()
			owner = user.username

			success = 0

			query_cas = db.GqlQuery("SELECT * FROM CAS WHERE ID =:c", c = chemical)
			cas = query_cas.get()

			if cas:
				if cas.owner == owner:
					success = 1

			query_nov = db.GqlQuery("SELECT * FROM Novel WHERE ID =:c", c = chemical)
			nov = query_nov.get()

			if nov:
				if nov.owner == owner:
					success = 2

			if success == 1:
				query = db.GqlQuery("SELECT * FROM CAS WHERE ID =:c", c = chemical)
				instance = query.get()
				db.delete(instance)

				params['success'] = "Chemical Deleted."
				self.render('search.html', **params)

			if success == 2:
				query = db.GqlQuery("SELECT * FROM Novel WHERE ID =:c", c = chemical)
				instance = query.get()
				db.delete(instance)

				params['success'] = "Chemical Deleted"
				self.render('search.html', **params)

			if success == 0:
				params['filter_error'] = "Permission Denied."
				self.render('search.html', **params)

		# update chemical in cas
		if button == 11:
			chemical = self.request.get('id')
			name = self.request.get('name')
			group = self.request.get('group')
			quantity = self.request.get('cur_quant')
			measure = self.request.get('measure')
			location = self.request.get('mainloc')
			sublocation = self.request.get('subloc')
			msds = self.request.get('msds')
			image1 = self.request.get('image1')
			image2 = self.request.get('image2')
			image3 = self.request.get('image3')
			image4 = self.request.get('image4')
			image5 = self.request.get('image5')
			image6 = self.request.get('image6')
			image7 = self.request.get('image7')
			image8 = self.request.get('image8')
			image9 = self.request.get('image9')
			container = self.request.get('container')

			params = dict(
				name = name,
				group = group,
				quantity = quantity,
				measure = measure,
				location = location,
				sublocation = sublocation,
				msds = msds,
				container = container
			)

			q = db.GqlQuery("SELECT * FROM CAS WHERE ID =:i", i = chemical)
			i = q.get()

			if group == "please select group":
				group = i.group

			if not valid_num(quantity):
				if not valid_dec(quantity):
					quantity = i.cur_quant

			if measure == "please select measurement":
				measure = i.measure

			if location == "please select primary location":
				location = i.location

			if sublocation == "please choose from above":
				sublocation = i.sublocation

			if sublocation == "please select sub location":
				sublocation = i.sublocation

			if sublocation =="no sub locations exist":
				sublocation = "None"

			if msds == "":
				msds = i.msds

			if container == "please select container type":
				container = i.container

			symbol = ""

			if image1:
				symbol += "%s " % image1

			if image2:
				symbol += "%s " % image2

			if image3:
				symbol += "%s " % image3

			if image4:
				symbol += "%s " % image4

			if image5:
				symbol += "%s " % image5

			if image6:
				symbol += "%s " % image6

			if image7:
				symbol += "%s " % image7

			if image8:
				symbol += "%s " % image8
				
			if image9:
				symbol += "%s" % image9

			query = db.GqlQuery("SELECT * FROM CAS WHERE ID =:i", i = chemical)
			instance = query.get()
			cas = instance.cas_no
			classification = instance.classification1

			if "(Category 1A)" or "(Category 1B)" in classification:
				email = self.request.cookies.get('nuimce', '')

				qu = db.GqlQuery("SELECT * FROM User WHERE email =:e", e = email)
				iu = qu.get()
				user = iu.username

				if instance.cur_quant != quantity:
					action = "Quantity Updated."

					cmr = CMR(ID = chemical, cas_no = cas, name = name, classification = classification, users = user, action = action)
					cmr.put()
				elif instance.location != location:
					action = "Location Updated."

					cmr = CMR(ID = chemical, cas_no = cas, name = name, classification = classification, users = user, action = action)
					cmr.put()
				elif instance.sublocation != sublocation:
					action = "Sub Location Updated."

					cmr = CMR(ID = chemical, cas_no = cas, name = name, classification = classification, users = user, action = action)
					cmr.put()

			instance.name = name
			instance.group = group
			instance.cur_quant = quantity
			instance.measure = measure
			instance.location = location
			instance.sublocation = sublocation
			instance.msds = msds
			instance.symbol = symbol
			instance.container = container
			instance.put()

			params['success'] = "Chemical Updated."
			self.render('search.html', **params)

		# update chemical in novel
		if button == 12:
			chemical = self.request.get('id')
			name = self.request.get('name')
			group = self.request.get('group')
			quantity = self.request.get('cur_quant')
			measure = self.request.get('measure')
			location = self.request.get('mainloc')
			sublocation = self.request.get('subloc')
			image1 = self.request.get('image1')
			image2 = self.request.get('image2')
			image3 = self.request.get('image3')
			image4 = self.request.get('image4')
			image5 = self.request.get('image5')
			image6 = self.request.get('image6')
			image7 = self.request.get('image7')
			image8 = self.request.get('image8')
			image9 = self.request.get('image9')
			description = self.request.get('description')
			countdown = int(self.request.get('countdown'))

			params = dict(
				name = name,
				group = group,
				quantity = quantity,
				measure = measure,
				location = location,
				sublocation = sublocation,
				description = description,
				countdown = countdown
			)

			q = db.GqlQuery("SELECT * FROM Novel WHERE ID =:i", i = chemical)
			i = q.get()

			if name == "":
				name = i.name

			if group == "please select group":
				group = i.group

			if not valid_num(quantity):
				if not valid_dec(quantity):
					quantity = i.cur_quant

			if measure == "please select measurement":
				measure = i.measure

			if location == "please select primary location":
				location = i.location

			if sublocation == "please choose from above":
				sublocation = i.sublocation

			if sublocation == "please select sub location":
				sublocation = i.sublocation

			if sublocation =="no sub locations exist":
				sublocation = "None"

			if countdown == 500:
				description = i.description
			elif countdown < 0:
				error = 1

			symbol = ""

			if image1:
				symbol += "%s " % image1

			if image2:
				symbol += "%s " % image2

			if image3:
				symbol += "%s " % image3

			if image4:
				symbol += "%s " % image4

			if image5:
				symbol += "%s " % image5

			if image6:
				symbol += "%s " % image6

			if image7:
				symbol += "%s " % image7

			if image8:
				symbol += "%s " % image8
				
			if image9:
				symbol += "%s" % image9

			query = db.GqlQuery("SELECT * FROM Novel WHERE ID =:i", i = chemical)
			instance = query.get()

			instance.name = name
			instance.group = group
			instance.cur_quant = quantity
			instance.measure = measure
			instance.location = location
			instance.sublocation = sublocation
			instance.symbol = symbol
			instance.description = description
			instance.put()

			params['success'] = "Chemical Updated."
			self.render('search.html', **params)

		# logout
		if button == 66:
			self.response.headers.add_header('Set-Cookie', 'nuimce =; Path=/')
			self.redirect('/')

# cas handler
class CASHandler(AppHandler):
	def get(self):
		nuimce = self.request.cookies.get('nuimce', '')
		query = db.GqlQuery("SELECT * FROM User WHERE email =:e", e = nuimce)
		instance = query.get()

		if instance is None:
			self.render('cas.html')
		else:
			success = ""
			params = dict(success = success)
			success = self.request.get('success')
			params['success'] = "%s" % success
			users = db.GqlQuery("SELECT * FROM User ORDER BY username ASC")
			self.render('cas.html', users = users, **params)

	def post(self):
		button = int(self.request.get('button'))
		error = 0

		# enter new chemical into CAS
		if button == 1:
			cas = self.request.get('cas')
			name = self.request.get('name')
			owner = self.request.get('owner')
			group = self.request.get('group')
			quantity = self.request.get('quantity')
			measure = self.request.get('measure')
			location = self.request.get('mainloc')
			sublocation = self.request.get('subloc')
			msds = self.request.get('msds')
			classification1 = self.request.get('classification1')
			classification2 = self.request.get('classification2')
			classification3 = self.request.get('classification3')
			classification4 = self.request.get('classification4')
			classification5 = self.request.get('classification5')
			classification6 = self.request.get('classification6')
			image1 = self.request.get('image1')
			image2 = self.request.get('image2')
			image3 = self.request.get('image3')
			image4 = self.request.get('image4')
			image5 = self.request.get('image5')
			image6 = self.request.get('image6')
			image7 = self.request.get('image7')
			image8 = self.request.get('image8')
			image9 = self.request.get('image9')
			number = self.request.get('number')
			container = self.request.get('container')

			params = dict(
				cas = cas,
				name = name,
				owner = owner,
				group = group,
				quantity = quantity,
				measure = measure,
				location = location,
				sublocation = sublocation,
				msds = msds,
				classification1 = classification1,
				number = number,
				container = container
			)

			if not valid_cas(cas):
				if cas == "":
					params['cas_error'] = "Field Empty."
				else:
					params['cas_error'] = "Invalid CAS No."
				error = 1

			if name == "":
				params['name_error'] = "Field Empty."
				error = 1

			if owner == "please select owner":
				params['owner_error'] = "Please Select Owner."
				error = 1

			if group == "please select group":
				params['group_error'] = "Please Select Group."
				error = 1

			if not valid_num(quantity):
				if not valid_dec(quantity):
					if quantity == "":
						params['quantity_error'] = "Field Empty."
					else:
						params['quantity_error'] = "Invalid Quantity."
					error = 1

			if measure == "please select measurement":
				params['measure_error'] = "Please Select Measurement."
				error = 1

			if location == "please select primary location":
				params['mainloc_error'] = "Please Select Location."
				error = 1

			if sublocation == "please select sub location":
				params['subloc_error'] = "Please Select Sub Location."
				error = 1

			if sublocation =="no sub locations exist":
				sublocation = "None"

			if msds == "":
				params['msds_error'] = "Field Empty."
				error = 1

			if classification1 == "please select classification":
				classification1 = "None"
				classification2 = "Null"
				classification3 = "Null"
				classification4 = "Null"
				classification5 = "Null"
				classification6 = "Null"

			if classification2 == "please select a second classification":
				classification2 = "Null"
				classification3 = "Null"
				classification4 = "Null"
				classification5 = "Null"
				classification6 = "Null"

			if classification3 == "please select a third classification":
				classification3 = "Null"
				classification4 = "Null"
				classification5 = "Null"
				classification6 = "Null"

			if classification4 == "please select a fourth classification":
				classification4 = "Null"
				classification5 = "Null"
				classification6 = "Null"

			if classification5 == "please select a fifth classification":
				classification5 = "Null"
				classification6 = "Null"

			if classification6 == "please select a sixth classification":
				classification6 = "Null"


			if not valid_num(number):
				if number == "":
					number = 1
				else:
					params['number_error'] = "Invalid Number."
					error = 1

			if container == "please select container type":
				params['container_error'] = "Please Select Container Type."
				error = 1

			symbol = ""

			if image1:
				symbol += "%s " % image1

			if image2:
				symbol += "%s " % image2

			if image3:
				symbol += "%s " % image3

			if image4:
				symbol += "%s " % image4

			if image5:
				symbol += "%s " % image5

			if image6:
				symbol += "%s " % image6

			if image7:
				symbol += "%s " % image7

			if image8:
				symbol += "%s " % image8
				
			if image9:
				symbol += "%s" % image9

			email = self.request.cookies.get('nuimce', '0')

			if email == "":
				error = 2

			if error == 1:
				users = db.GqlQuery("SELECT * FROM User ORDER BY username ASC")
				self.render('cas.html', users = users, **params)

			if error == 2:
				self.redirect('/?login=Please Login.')

			if error == 0:
				for x in xrange(int(number)):
					now = time.strftime("%c")
					ID = "{user} {date} {num}".format(user = owner, date = now, num = x)

					new_cas = CAS(ID = ID, cas_no = cas, name = name, owner = owner, group = group, int_quant = quantity, cur_quant = quantity, measure = measure, msds = msds, classification1 = classification1, classification2 = classification2, classification3 = classification3, classification4 = classification4, classification5 = classification5, classification6 = classification6, symbol = symbol, container = container, location = location, sublocation = sublocation)
					new_cas.put()

				self.redirect("/unit2/enter/cas?success=Successfully Uploaded.")

		# logout
		if button == 66:
			self.response.headers.add_header('Set-Cookie', 'nuimce =; Path=/')
			self.redirect('/')

# novel handler
class NovelHandler(AppHandler):
	def get(self):
		nuimce = self.request.cookies.get('nuimce', '')
		query = db.GqlQuery("SELECT * FROM User WHERE email =:e", e = nuimce)
		instance = query.get()

		if instance is None:
			self.render('novel.html')
		else:
			success = ""
			params = dict(success = success)
			success = self.request.get('success')
			params['success'] = "%s" % success
			users = db.GqlQuery("SELECT * FROM User ORDER BY username ASC")
			self.render('novel.html', users = users, **params)

	def post(self):
		button = int(self.request.get('button'))
		error = 0

		# enter new chemical into Novel
		if button == 1:
			name = self.request.get('name')
			owner = self.request.get('owner')
			group = self.request.get('group')
			quantity = self.request.get('quantity')
			measure = self.request.get('measure')
			location = self.request.get('mainloc')
			sublocation = self.request.get('subloc')
			classification1 = self.request.get('classification1')
			classification2 = self.request.get('classification2')
			classification3 = self.request.get('classification3')
			classification4 = self.request.get('classification4')
			classification5 = self.request.get('classification5')
			classification6 = self.request.get('classification6')
			image1 = self.request.get('image1')
			image2 = self.request.get('image2')
			image3 = self.request.get('image3')
			image4 = self.request.get('image4')
			image5 = self.request.get('image5')
			image6 = self.request.get('image6')
			image7 = self.request.get('image7')
			image8 = self.request.get('image8')
			image9 = self.request.get('image9')
			description = self.request.get('description')
			countdown = int(self.request.get('countdown'))

			params = dict(
				name = name,
				owner = owner,
				group = group,
				quantity = quantity,
				measure = measure,
				location = location,
				sublocation = sublocation,
				classification1 = classification1,
				description = description,
				countdown = countdown
			)

			if name == "":
				params['name_error'] = "Field Empty."
				error = 1

			if owner == "please select owner":
				params['owner_error'] = "Please Select Owner."
				error = 1

			if group == "please select group":
				params['group_error'] = "Please Select Group."
				error = 1

			if not valid_num(quantity):
				if not valid_dec(quantity):
					if quantity == "":
						params['quantity_error'] = "Field Empty."
					else:
						params['quantity_error'] = "Invalid Quantity."
					error = 1

			if measure == "please select measurement":
				params['measure_error'] = "Please Select Measurement."
				error = 1

			if location == "please select primary location":
				params['mainloc_error'] = "Please Select Location."
				error = 1

			if sublocation == "please select sub location":
				params['subloc_error'] = "Please Select Sub Location."
				error = 1

			if sublocation =="no sub locations exist":
				sublocation = "None"

			if classification1 == "please select classification":
				classification1 = "None"
				classification2 = "Null"
				classification3 = "Null"
				classification4 = "Null"
				classification5 = "Null"
				classification6 = "Null"

			if classification2 == "please select a second classification":
				classification2 = "Null"
				classification3 = "Null"
				classification4 = "Null"
				classification5 = "Null"
				classification6 = "Null"

			if classification3 == "please select a third classification":
				classification3 = "Null"
				classification4 = "Null"
				classification5 = "Null"
				classification6 = "Null"

			if classification4 == "please select a fourth classification":
				classification4 = "Null"
				classification5 = "Null"
				classification6 = "Null"

			if classification5 == "please select a fifth classification":
				classification5 = "Null"
				classification6 = "Null"

			if classification6 == "please select a sixth classification":
				classification6 = "Null"

			if countdown == 500:
				params['desc_error'] = "Field Empty."
				error = 1
			elif countdown < 0:
				params['desc_error'] = "Too Many Characters."
				error = 1

			symbol = ""

			if image1:
				symbol += "%s " % image1

			if image2:
				symbol += "%s " % image2

			if image3:
				symbol += "%s " % image3

			if image4:
				symbol += "%s " % image4

			if image5:
				symbol += "%s " % image5

			if image6:
				symbol += "%s " % image6

			if image7:
				symbol += "%s " % image7

			if image8:
				symbol += "%s " % image8
				
			if image9:
				symbol += "%s" % image9

			email = self.request.cookies.get('nuimce', '0')

			if email == "":
				error = 2

			if error == 1:
				users = db.GqlQuery("SELECT * FROM User ORDER BY username ASC")
				self.render('novel.html', users = users, **params)

			if error == 2:
				self.redirect('/?login=Please Login.')

			if error == 0:
				now = time.strftime("%c")
				ID = "{user} {date}".format(user = owner, date = now)

				new_novel = Novel(ID = ID, name = name, owner = owner, group = group, int_quant = quantity, cur_quant = quantity, measure = measure, classification1 = classification1, classification2 = classification2, classification3 = classification3, classification4 = classification4, classification5 = classification5, classification6 = classification6, symbol = symbol, description = description, location = location, sublocation = sublocation)
				new_novel.put()

				self.redirect("/unit2/enter/novel?success=Successfully Uploaded.")

		# logout
		if button == 66:
			self.response.headers.add_header('Set-Cookie', 'nuimce =; Path=/')
			self.redirect('/')

# waste handler
class WasteHandler(AppHandler):
	def get(self):
		nuimce = self.request.cookies.get('nuimce', '')
		query = db.GqlQuery("SELECT * FROM User WHERE email =:e", e = nuimce)
		instance = query.get()

		if instance is None:
			self.render('waste.html')
		else:
			success = ""
			params = dict(success = success)
			success = self.request.get('success')
			params['success'] = "%s" % success
			users = db.GqlQuery("SELECT * FROM User ORDER BY username ASC")
			self.render('waste.html', users = users, **params)

	def post(self):
		button = int(self.request.get('button'))
		error = 0

		# enter new waste into Waste
		if button == 1:
			owner = self.request.get('owner')
			group = self.request.get('group')
			quantity = self.request.get('quantity')
			measure = self.request.get('measure')
			location = self.request.get('mainloc')
			sublocation = self.request.get('subloc')
			waste_type = self.request.get('type')
			image1 = self.request.get('image1')
			image2 = self.request.get('image2')
			image3 = self.request.get('image3')
			image4 = self.request.get('image4')
			image5 = self.request.get('image5')
			image6 = self.request.get('image6')
			image7 = self.request.get('image7')
			image8 = self.request.get('image8')
			image9 = self.request.get('image9')
			description = self.request.get('description')
			countdown = int(self.request.get('countdown'))

			params = dict(
				owner = owner,
				quantity = quantity,
				measure = measure,
				location = location,
				sublocation = sublocation,
				waste_type = waste_type,
				description = description,
				countdown = countdown
			)

			if owner == "please select owner":
				params['owner_error'] = "Please Select Owner."
				error = 1

			if group == "please select group":
				group = ""

			if not valid_num(quantity):
				if not valid_dec(quantity):
					if quantity == "":
						params['quantity_error'] = "Field Empty."
					else:
						params['quantity_error'] = "Invalid Quantity."
					error = 1

			if measure == "please select measurement":
				params['measure_error'] = "Please Select Measurement."
				error = 1

			if location == "please select primary location":
				params['mainloc_error'] = "Please Select Location."
				error = 1

			if sublocation == "please select sub location":
				params['subloc_error'] = "Please Select Sub Location."
				error = 1

			if sublocation =="no sub locations exist":
				sublocation = "None"

			if waste_type == "please select type":
				params['type_error'] = "Please Select Type."
				error = 1

			if description != "":
				if countdown < 0:
					params['desc_error'] = "Too Many Characters."
					error = 1

			symbol = ""

			if image1:
				symbol += "%s " % image1

			if image2:
				symbol += "%s " % image2

			if image3:
				symbol += "%s " % image3

			if image4:
				symbol += "%s " % image4

			if image5:
				symbol += "%s " % image5

			if image6:
				symbol += "%s " % image6

			if image7:
				symbol += "%s " % image7

			if image8:
				symbol += "%s " % image8
				
			if image9:
				symbol += "%s" % image9

			email = self.request.cookies.get('nuimce', '0')

			if email == "":
				error = 2

			if error == 1:
				users = db.GqlQuery("SELECT * FROM User ORDER BY username ASC")
				self.render('waste.html', users = users, **params)

			if error == 2:
				self.redirect('/?login=Please Login.')

			if error == 0:
				now = time.strftime("%c")
				ID = "{user} {date}".format(user = owner, date = now)

				new_waste = Waste(ID = ID, owner = owner, group = group, quantity = quantity, measure = measure, waste_type = waste_type, symbol = symbol, description = description, location = location, sublocation = sublocation)
				new_waste.put()

				self.redirect("/unit2/enter/waste?success=Successfully Uploaded.")

		# logout
		if button == 66:
			self.response.headers.add_header('Set-Cookie', 'nuimce =; Path=/')
			self.redirect('/')

# report handler
class ReportHandler(AppHandler):
	def get(self):
		self.render('report.html')

	def post(self):
		button = int(self.request.get('button'))
		error = 0

		# generate report
		if button == 1:
			search = self.request.get('search')
			dropdown = self.request.get('dropdown')
			params = dict(search = search, dropdown = dropdown)

			if dropdown == "filter":
				params['filter_error'] = "No Filter Selected."
				error = 1

			if dropdown == "All":
				if search != "":
					params['search_error'] = "No Input Required."
				else:
					query = db.GqlQuery("SELECT * FROM CAS")
					instance = query.get()

					if not instance:
						params['filter_error'] = "No Chemicals Exist."
						error = 1

			if dropdown == "Name":
				if search == "":
					params['search_error'] = "Field Empty."
					error = 1
				else:
					query = db.GqlQuery("SELECT * FROM CAS WHERE name =:n", n = search)
					instance = query.get()

					if not instance:
						params['search_error'] = "Chemical/s Not Found."
						error = 1

			if dropdown == "Owner":
				if search == "":
					params['search_error'] = "Field Empty."
					error = 1
				else:
					query = db.GqlQuery("SELECT * FROM CAS WHERE owner =:o", o = search)
					instance = query.get()

					if not instance:
						params['search_error'] = "Chemical/s Not Found."
						error = 1

			if dropdown == "Group":
				if search == "":
					params['search_error'] = "Field Empty."
					error = 1
				else:
					query = db.GqlQuery("SELECT * FROM CAS WHERE group =:g", g = search)
					instance = query.get()

					if not instance:
						params['search_error'] = "Chemical/s Not Found."
						error = 1

			if dropdown == "Classification":
				if search == "":
					params['search_error'] = "Field Empty."
					error = 1
				elif "(Category 1A)" in search or "(Category 1B)" in search:
					query = db.GqlQuery("SELECT * FROM CMR WHERE classification =:c", c = search)
					instance = query.get()

					if not instance:
						params['search_error'] = "Chemical/s Not Found."
						error = 1
				else:
					query = db.GqlQuery("SELECT * FROM CAS WHERE classification1 =:c", c = search)
					instance = query.get()

					if not instance:
						query = db.GqlQuery("SELECT * FROM CAS WHERE classification2 =:c", c = search)
						instance = query.get()

						if not instance:
							query = db.GqlQuery("SELECT * FROM CAS WHERE classification3 =:c", c = search)
							instance = query.get()

							if not instance:
								query = db.GqlQuery("SELECT * FROM CAS WHERE classification4 =:c", c = search)
								instance = query.get()

								if not instance:
									query = db.GqlQuery("SELECT * FROM CAS WHERE classification5 =:c", c = search)
									instance = query.get()

									if not instance:
										query = db.GqlQuery("SELECT * FROM CAS WHERE classification6 =:c", c = search)
										instance = query.get()

										if not instance:
											params['search_error'] = "Chemical/s Not Found."
											error = 1

			if dropdown == "Location":
				if search == "":
					params['search_error'] = "Field Empty."
					error = 1
				else:
					query = db.GqlQuery("SELECT * FROM CAS WHERE location =:l", l = search)
					instance = query.get()

					if not instance:
						params['search_error'] = "Chemical/s Not Found."
						error = 1

			if dropdown == "Sub Location":
				if search == "":
					params['search_error'] = "Field Empty."
					error = 1
				else:
					query = db.GqlQuery("SELECT * FROM CAS WHERE sublocation =:s", s = search)
					instance = query.get()

					if not instance:
						params['search_error'] = "Chemical/s Not Found."
						error = 1

			if dropdown == "Waste":
				if search != "":
					params['search_error'] = "No Input Required."

				query = db.GqlQuery("SELECT * FROM Waste")
				instance = query.get()

				if not instance:
					params['filter_error'] = "No Waste Exists."
					error = 1

			email = self.request.cookies.get('nuimce', '0')

			if email == "":
				error = 2

			if error == 1:
				self.render('report.html', **params)

			if error == 2:
				self.redirect('/?login=Please Login.')

			if error == 0:
				if dropdown == "All":
					query = db.GqlQuery("SELECT * FROM CAS ORDER BY name ASC")
					self.render('report-results.html', query = query, **params)

				if dropdown == "Name":
					query = db.GqlQuery("SELECT * FROM CAS WHERE name =:n ORDER BY created ASC", n = search)
					self.render('report-results.html', query = query)

				if dropdown == "Owner":
					query = db.GqlQuery("SELECT * FROM CAS WHERE owner =:o ORDER BY created ASC", o = search)
					self.render('report-results.html', query = query)

				if dropdown == "Group":
					query = db.GqlQuery("SELECT * FROM CAS WHERE group =:g ORDER BY created ASC", g = search)
					self.render('report-results.html', query = query)

				if dropdown == "Classification":
					if "(Category 1A)" in search or "(Category 1B)" in search:
						query = db.GqlQuery("SELECT * FROM CMR WHERE classification =:c ORDER BY created ASC", c = search)
						self.render('cmr-results.html', query = query)
					else:
						query1 = db.GqlQuery("SELECT * FROM CAS WHERE classification1 =:c ORDER BY created ASC", c = search)
						query2 = db.GqlQuery("SELECT * FROM CAS WHERE classification2 =:c ORDER BY created ASC", c = search)
						query3 = db.GqlQuery("SELECT * FROM CAS WHERE classification3 =:c ORDER BY created ASC", c = search)
						query4 = db.GqlQuery("SELECT * FROM CAS WHERE classification4 =:c ORDER BY created ASC", c = search)
						query5 = db.GqlQuery("SELECT * FROM CAS WHERE classification5 =:c ORDER BY created ASC", c = search)
						query6 = db.GqlQuery("SELECT * FROM CAS WHERE classification6 =:c ORDER BY created ASC", c = search)
						self.render('class-report-results.html', query1 = query1, query2 = query2, query3 = query3, query4 = query4, query5 = query5, query6 = query6)

				if dropdown == "Location":
					query = db.GqlQuery("SELECT * FROM CAS WHERE location =:l ORDER BY created ASC", l = search)
					self.render('report-results.html', query = query)

				if dropdown == "Sub Location":
					query = db.GqlQuery("SELECT * FROM CAS WHERE sublocation =:s ORDER BY created ASC", s = search)
					self.render('report-results.html', query = query)

				if dropdown == "Waste":
					query = db.GqlQuery("SELECT * FROM Waste ORDER BY created ASC")
					self.render('waste-results.html', query = query, **params)

		# logout
		if button == 66:
			self.response.headers.add_header('Set-Cookie', 'nuimce =; Path=/')
			self.redirect('/')

# application mapping
app = webapp2.WSGIApplication([
	('/', LoginHandler),
	('/unit2/admin', ControllerHandler),
	('/unit2/search', SearchHandler),
	('/unit2/enter/cas', CASHandler),
	('/unit2/enter/novel', NovelHandler),
	('/unit2/enter/waste', WasteHandler),
	('/unit2/report', ReportHandler)
	], debug=True)