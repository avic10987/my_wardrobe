from tkinter import *
from secrets import secret
from PIL import Image, ImageTk
import requests
import json
import os
import copy
from tkcalendar import *
import datetime

APP_HEIGHT = 810
APP_WIDTH = 1000
DEFAULT_FONT = 'Helvetica'
NAV_BUTTON_PADX, NAV_BUTTON_PADY = 25, 15

ALL_GARMENTS = []
CLOSET_LOADED = False
CURRENT_GARM = None
OOTD = []


def kelvin_to_farenheit(temp):
		return int((temp - 273.15) * 9/5 + 32)
today = datetime.date.today()


class Wardrobe_App(Tk):
	def __init__(self):
		super().__init__()
		self.current_frame = None
		self.geometry('{0}x{1}'.format(APP_WIDTH, APP_HEIGHT))

		self.swap_frames(Welcome_page)
	
	def swap_frames(self, new_frame):
		swapped_frame = new_frame(self)
		if self.current_frame != None:
			self.current_frame.destroy()
		#print(self.current_frame, 'boo1')
		self.current_frame = swapped_frame
		self.current_frame.pack(fill = BOTH, expand = True)
		#print(self.current_frame, 'boo2')


class Welcome_page(Frame):
	def __init__(self, root):
		super().__init__(root)
		self.root = root
		self.welcome_screen(self)
		self.load_closet_data()

	def get_weather(self, zipc = 20721):
		url = 'http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={API_key}'.format(zip_code = zipc, API_key = secret)
		weather_data = requests.get(url).json()
		#print(weather_data)

		city = weather_data['name'] 
		feels_like = kelvin_to_farenheit(weather_data['main']['feels_like'])
		icon = weather_data['weather'][0]['icon']
		description = weather_data['weather'][0]['main']
		img_path = 'weather_icons/{code}@2x.png'.format(code = icon)

		return (city, feels_like, description, img_path)


	def welcome_screen(self, root):
		#Welcome text
		welcome_txt = Label(self,fg = 'black', font = ('Helvetica', 20))
		welcome_txt['text'] = 'Welcome'
		welcome_txt.pack(pady = 50)
	
		#weather display        
		weather_info = self.get_weather()
		photo = PhotoImage(file = weather_info[3])
		image = Label(self, image = photo)
		image.pack()
		image.image = photo 

		weather_info_txt = Label(self, fg = 'black', font = (DEFAULT_FONT))
		weather_info_txt['text'] = 'Currently in {city}: \n {temp}°, {description}'.format(city = weather_info[0], temp = weather_info[1], description = weather_info[2])
		weather_info_txt.pack()

		#navigation widgets
		self.navigation_widgets(self.root)

	def navigation_widgets(self, root):
		#frame for nav buttons
		nav_frame = Frame(self, height = 200, width = 900)
		nav_frame.pack(side = 'top', pady = 125)

		#nav buttons
		closet_button = Button(nav_frame, text = 'My Closet', font = DEFAULT_FONT, command = lambda: root.swap_frames(Closet))
		closet_button.pack(side = 'left', padx = 10)
		
		calender_button = Button(nav_frame, text = 'My Calender', font = DEFAULT_FONT, command = lambda: root.swap_frames(My_calender))
		calender_button.pack(side = 'left', padx = 10)

		outfit_builder_button = Button(nav_frame, text = 'OOTD', font = DEFAULT_FONT, command = lambda: root.swap_frames(OOTD_Display))
		outfit_builder_button.pack(side = 'left', padx = 10)
		
		moodboard_button = Button(nav_frame, text = 'Moodboard', font  = DEFAULT_FONT, command = lambda: root.swap_frames(Moodboard))
		moodboard_button.pack(side = 'left', padx = 10)    

	def unpack_garment(self, garment_info):
		garment = Garment()
		garment.filepath = garment_info['filename']
		garment.garment_type = garment_info['garment_type']
		garment.display_name = garment_info['display_name']
		garment.dates_worn = garment_info['dates_worn'].split(',')
		return garment
	
	def load_closet_data(self):
		global CLOSET_LOADED
		if CLOSET_LOADED == False:	
			seen_files = []
			with open('clothes/wardrobe_data.json') as wardrobe_json:
				wardrobe_data = (json.load(wardrobe_json))
				for elem in wardrobe_data:
					seen_files.append(elem['filename'])
					garment = self.unpack_garment(elem)
					ALL_GARMENTS.append(garment)
			
			for filee in os.listdir('clothes/'):
				if filee.endswith('jpg') or filee.endswith('png') or filee.endswith('jpeg'):
					if filee not in seen_files:
						new_garment = Garment()
						new_garment.filepath = filee
						ALL_GARMENTS.append(new_garment)
			CLOSET_LOADED = True
class Garment:
	def __init__(self):
		self.filepath = ''
		self.garment_type = ''
		self.display_name = ''
		self.dates_worn = []
		
	
	def __repr__(self):
		return self.filepath
	
	def __eq__(self, other):
		return self.filepath == other
	
	def get_last_worn(self):
		most_recent_year = ''
		worn_that_year = []
		for date in self.dates_worn:
			year = date[:2]
			if year > most_recent_year:
				most_recent_year = year
				worn_that_year = []
				worn_that_year.append(date)
			elif year == most_recent_year:
				worn_that_year.append(date)
		
		if len(worn_that_year) > 0: return max(worn_that_year)
		else: return ''

class Closet(Frame):
	def __init__(self, root):
		super().__init__(root)
		self.root = root
		self.current_page = 0
		self.closet_frame = None
		self.bottom_nav_frame = None
		self.display = []

		self.top_navigation_widgets(self.root)
		self.closet_header()
		self.load_closet_display(self.root)
		self.bottom_navigation_widgets()

		
	def top_navigation_widgets(self, root):
		back_button = Button(self, width = 10, height = 1, text = '< Main')
		back_button['command'] = lambda: root.swap_frames(Welcome_page)
		back_button.pack(side = LEFT, anchor = NW, pady = NAV_BUTTON_PADY, padx = NAV_BUTTON_PADX)

		save_button = Button(self, width = 10, height = 1, text = 'Save Changes')
		save_button['command'] = self.save_closet_data
		save_button.pack(side = RIGHT, anchor = NE, pady = NAV_BUTTON_PADY, padx = NAV_BUTTON_PADX)

	def closet_header(self):
		#closet header
		closet_header = Label(self,fg = 'black', font = ('Helvetica', 20), text = 'My Wardrobe')
		closet_header.pack(pady = 30)
		#option button
		display_options = ['All', 'Tops', 'Bottoms', "Accessories", 'Shoes', 'Misc', 'Outerwear']
		self.variable = StringVar(self)
		self.variable.set(display_options[0])

		options = OptionMenu(self, self.variable, *display_options)
		options.pack()
		refresh_button = Button(self, text = 'Refresh', command = lambda: [self.refresh_current_page(), self.load_closet_display(self.root)])
		refresh_button.pack(pady =10)

	def set_current_garm(self, button):
		global CURRENT_GARM
		print('Button:', button['text'], ALL_GARMENTS.index(button['text']))

		CURRENT_GARM = button['text']
	def refresh_current_page(self):
		self.current_page = 0
		   
	def make_display(self, category):
		#returns 2d list of all files based on category
		if category == 'All':
			temp_list = [garm for garm in ALL_GARMENTS]
		else:
			temp_list = [garm for garm in ALL_GARMENTS if garm.garment_type == category]

		display_list = []
		page = []
		while len(temp_list) > 0:
			temp_garm = temp_list.pop(0)
			page.append(temp_garm)
			if len(page) == 12:
				display_list.append(page)
				page = []
		display_list.append(page)

		return display_list

	def load_closet_display(self, root):
		#closet frame
		if self.closet_frame != None:
			self.closet_frame.destroy()

		self.closet_frame = Frame(self, width = 400, height = 400)
		self.closet_frame.pack(side = 'top', pady = 25)
		
		#update display based on category
		garm_category = self.variable.get()
		self.display = self.make_display(garm_category)

		#load all garments in display to closet frame
		current_display = self.display[self.current_page]
		counter =  0
		for r in range(3):
			for c in range(4):
				if counter < len(current_display):
					path = "clothes/{ex}".format(ex = current_display[counter].filepath)
					img_file = Image.open(path)
					
					
					img_file = img_file.resize((150, 150), Image.ANTIALIAS)
					photo = ImageTk.PhotoImage(img_file)
					image = Button(self.closet_frame, image = photo, text = current_display[counter])
					image.configure(command=lambda button=image: [self.set_current_garm(button), root.swap_frames(Edit_Garment)])
					image.grid(row = r, column = c, padx = 10, pady = 10)
					image.image = photo

					counter+=1

		self.bottom_navigation_widgets()

	
	def nav_right(self):
		if self.current_page == len(self.display) -1:
			self.current_page = 0
		else:
			self.current_page += 1
		self.load_closet_display(self.root)
		
	def nav_left(self):
		if self.current_page == 0:
				self.current_page = len(self.display) - 1
		else:
			self.current_page -= 1
		self.load_closet_display(self.root)

	def bottom_navigation_widgets(self):
		#nav buttons frame
		if self.bottom_nav_frame != None:
			self.bottom_nav_frame.destroy()
		self.bottom_nav_frame = Frame(self, height = 50, width = 1000)
		self.bottom_nav_frame.pack(side = 'top', pady = 10)

		#nav buttons
		back_button = Button(self.bottom_nav_frame, width = 5, text = '<', command = self.nav_left)
		back_button.grid(row = 0, column = 0, padx = 5)

		next_button = Button(self.bottom_nav_frame, width = 5, text  = '>', command = self.nav_right)
		next_button.grid(row = 0, column = 1, padx = 5)

	def save_closet_data(self):
		global ALL_GARMENTS
		all_garments_lst = []
		for garm in ALL_GARMENTS:
			garm_dict = {}
			garm_dict['filename'] = garm.filepath
			garm_dict['garment_type'] = garm.garment_type
			garm_dict['display_name'] = garm.display_name
			dates_worn_str = ''
			for date in garm.dates_worn:
				dates_worn_str += date + ','
			garm_dict['dates_worn'] = dates_worn_str
			all_garments_lst.append(garm_dict)
		
		print(all_garments_lst)
		with open('clothes/wardrobe_data.json', 'w') as wardrobe_data_file:
			wardrobe_data_file.write(json.dumps(all_garments_lst))

class Edit_Garment(Frame):
	global CURRENT_GARM
	def __init__(self, root):
		super().__init__(root)
		self.root = root
		self.filepath = CURRENT_GARM
		self.curr_index = ALL_GARMENTS.index(CURRENT_GARM)
		self.current_garm = ALL_GARMENTS[self.curr_index]

		self.top_navigation_widgets(self.root)
		self.garm_display(self.root)
		self.bottom_widgets()
	
	def top_navigation_widgets(self, root):
		back_button = Button(self, width = 10, height = 1, text = '< Closet')
		back_button['command'] = lambda: root.swap_frames(Closet)
		back_button.pack(side = LEFT, anchor = NW, pady = NAV_BUTTON_PADY, padx = NAV_BUTTON_PADX)

		save_button = Button(self, width = 10, height = 1, text = 'View OOTD')
		save_button['command'] = lambda: root.swap_frames(OOTD_Display)
		save_button.pack(side = RIGHT, anchor = NE, pady = NAV_BUTTON_PADY, padx = NAV_BUTTON_PADX)

	def garm_display(self, root):	
		#garment image & caption
		path = "clothes/{ex}".format(ex = self.current_garm.filepath)
		img_file = Image.open(path)
		img_file = img_file.resize((375, 400), Image.ANTIALIAS)
		photo = ImageTk.PhotoImage(img_file)
		image = Label(self, image = photo)
		image.pack( anchor = CENTER, pady = 40)
		image.image = photo

		page_header_txt = Label(self,fg = 'black', font = ('Helvetica', 12))
		if self.current_garm.display_name != '':
			page_header_txt['text'] = self.current_garm.display_name
		else:
			page_header_txt['text'] = self.current_garm.filepath
		
		page_header_txt.pack(pady = 5, anchor = CENTER)
	
	def update_attribute(self, update, attribute):
		print(update)
		if attribute == 'display name':
			self.current_garm.display_name = update
		if attribute == 'type':
			self.current_garm.garment_type = update

		self.root.swap_frames(Edit_Garment)	
	
	def update_OOTD(self, update):
		global OOTD
		if update == 'add':
			OOTD.append(self.current_garm)
		elif update == 'remove':
			OOTD.remove(self.current_garm)
		print('OOTD:', OOTD)
		self.root.swap_frames(Edit_Garment)	


	def bottom_widgets(self):
		global OOTD
		#frame
		self.widgets_frame = Frame(self, width = APP_WIDTH, height = APP_HEIGHT /2)
		self.widgets_frame.pack(pady = 40)

		#edits: display name, type,
		display_name_label = Label(self.widgets_frame, text = 'Display Name:', font = (DEFAULT_FONT, 10))
		display_name_label.grid(row = 0, column = 0)
		display_name_txt = StringVar()
		display_name_entry = Entry(self.widgets_frame, textvariable = display_name_txt)
		display_name_entry.grid(row = 0, column = 1)
		display_name_update = Button(self.widgets_frame, text = 'Update')
		display_name_update.configure(command = lambda button = display_name_update: [self.update_attribute(display_name_txt.get(), 'display name')])
		display_name_update.grid(row = 0, column = 2)

		garm_type_label = Label(self.widgets_frame, text = 'Category:', font = (DEFAULT_FONT, 10))
		garm_type_label.grid(row = 1, column = 0, pady = 20) 
		garm_type_options = ['Tops', 'Bottoms', "Accessories", 'Shoes', 'Misc']
		self.garm_type_txt = StringVar(self)
		self.garm_type_txt.set(self.current_garm.garment_type)
		garm_type_menu = OptionMenu(self.widgets_frame, self.garm_type_txt, *garm_type_options)
		garm_type_menu.grid(row = 1, column = 1)
		garm_type_update = Button(self.widgets_frame, text = 'Update')
		garm_type_update.configure(command = lambda button = display_name_update: [self.update_attribute(self.garm_type_txt.get(), 'type')])
		garm_type_update.grid(row = 1, column = 2)

		#
		last_worn_label = Label(self.widgets_frame, font = (DEFAULT_FONT, 10) )
		last_worn_label.configure(text = 'Last Worn: {x}'.format(x = self.current_garm.get_last_worn()))
		last_worn_label.grid(row = 2, column = 0, pady =10) 

		if self.current_garm not in OOTD:
			add_to_ootd_button = Button(self.widgets_frame, text = 'Add to OOTD')
			add_to_ootd_button.configure(command = lambda button = add_to_ootd_button: [self.update_OOTD('add')])
			add_to_ootd_button.grid(row = 3, column = 1, pady = 20) 
		else:
			remove_from_ootd_button = Button(self.widgets_frame, text = 'Remove from OOTD')
			remove_from_ootd_button.configure(command = lambda button = remove_from_ootd_button: [self.update_OOTD('remove')])
			remove_from_ootd_button.grid(row = 3, column = 1, pady = 15) 


class My_calender(Frame):
	def __init__(self, root):
		global OOTD
		super().__init__(root)
		self.root = root
		self.ootd_frame = None

		self.top_navigation_widgets(self.root)
		self.display_cal()
	
	def top_navigation_widgets(self, root):
		nav_frame = Frame(self, width = APP_WIDTH, height = 2)
		nav_frame.pack(fill= BOTH)
		back_button = Button(nav_frame, width = 10, height = 1, text = '< Main')
		back_button['command'] = lambda: root.swap_frames(Welcome_page)
		back_button.pack(side = LEFT, anchor = NW, pady = NAV_BUTTON_PADY, padx = NAV_BUTTON_PADX)

	def display_cal(self):
		cal_frame = Frame(self, height = 500, width = APP_WIDTH)
		cal_frame.pack(fill = BOTH, pady = 50)

		self.cal_label = Label(cal_frame, text = '', font = (DEFAULT_FONT, 14))
		self.cal_label.pack(pady = 20)
		self.cal = Calendar(cal_frame, selectmode = 'day', year=today.year, month=today.month, day=today.day)
		self.cal.pack(fill = BOTH, padx = 200, pady = 20)
		self.cal_label.configure(text = self.cal.get_date())

		view_OOTD = Button(cal_frame, text = 'View OOTD')
		view_OOTD.configure(command = lambda: [self.display_OOTD()])
		view_OOTD.pack()

	def display_OOTD(self):
		if self.ootd_frame != None: self.ootd_frame.destroy()
		curr_date = self.cal.get_date()
		self.cal_label.configure(text = curr_date)

		ootd = [garm for garm in ALL_GARMENTS if curr_date in garm.dates_worn]
		print(curr_date, ootd)
		
		self.ootd_frame = Frame(self, height = 350, width = APP_WIDTH)
		self.ootd_frame.pack(fill = BOTH, padx = 250,)

		counter = 0
		for r in range(2):
			for c in range(4):
				if counter < len(ootd):
					path = "clothes/{x}".format(x = ootd[counter])
					print(path)
					img_file = Image.open(path)
					
					img_file = img_file.resize((100, 100), Image.ANTIALIAS)
					photo = ImageTk.PhotoImage(img_file)
					image = Label(self.ootd_frame, image = photo)
					image.grid(row = r, column = c, padx = 10, pady = 10)
					image.image = photo

					counter+=1

	
class OOTD_Display(Frame):
	def __init__(self, root):
		global OOTD
		super().__init__(root)
		self.root = root

		if OOTD == []:
			self.redirect_to_closet(self.root)
		else:
			self.top_navigation_widgets(self.root)
			self.display_fit(self.root)
			self.date_widgets()
		
	def redirect_to_closet(self, root):
		Frame(self, height = 250).pack(fill = Y) #padding

		redirect_txt = Label(self, font = (DEFAULT_FONT, 15))
		redirect_txt['text'] = 'Oops! Nothing to see here.\nGo to your closet to add to your outfit of the day.'
		redirect_txt.pack(side = TOP)

		redirect_button = Button(self, text = 'My Closet')
		redirect_button['command'] = lambda: root.swap_frames(Closet)
		redirect_button.pack(pady = 30)
	
	def top_navigation_widgets(self, root):
		back_button = Button(self, width = 10, height = 1, text = '< Main')
		back_button['command'] = lambda: root.swap_frames(Welcome_page)
		back_button.pack(side = LEFT, anchor = NW, pady = NAV_BUTTON_PADY, padx = NAV_BUTTON_PADX)

		save_button = Button(self, width = 10, height = 1, text = 'Closet >')
		save_button['command'] = lambda: root.swap_frames(Closet)
		save_button.pack(side = RIGHT, anchor = NE, pady = NAV_BUTTON_PADY, padx = NAV_BUTTON_PADX)


	def assign_date(self):
		global OOTD
		#check for valid entry
		day, month, year = None, None, None
		if int(self.month_spin.get()) in range(1,13):
			month = self.month_spin.get()
		if int(self.day_spin.get()) in range(1,31):
			day = self.day_spin.get()
		if int(self.year_spin.get()) in range(0,99):
			if int(self.year_spin.get()) in range(0,10):
				year = "0" + self.year_spin.get() 
			else: year = self.year_spin.get()

		if day!= None and month !=  None and year != None:
			date = "{m}/{d}/{y}".format(m =month , d = day, y = year)
			for garm in OOTD:
				garm.dates_worn.append(date)
			print(date)

	def display_fit(self, root):
		global OOTD
		Frame(self, height =150,).pack(fill =Y, side =TOP) #padding	
		#outfit frame	
		fit_frame = Frame(self) 
		fit_frame.pack(fill = BOTH)
		#display
		num_pieces = len(OOTD)
		num_rows = num_pieces // 2 +1
		num_cols = num_pieces // 2 +1

		counter = 0
		for r in range(num_rows):
			for c in range(num_cols):
				if counter < num_pieces:
					path = "clothes/{ex}".format(ex = OOTD[counter].filepath)
					img_file = Image.open(path)

					img_file = img_file.resize((200, 200), Image.ANTIALIAS)
					photo = ImageTk.PhotoImage(img_file)
					image = Label(fit_frame, image = photo)
					image.grid(row = r, column = c, padx = 10, pady = 10)
					image.image = photo

					counter+=1
		
	def date_widgets(self):
		date_widgets_frame = Frame(self, width = APP_WIDTH, height = 150)
		date_widgets_frame.pack(fill = BOTH, padx = 150, pady = 20)

		#month, day, year drop down menus
		month_label = Label(date_widgets_frame, text = 'Month:')
		month_label.grid(row = 0 , column = 0, padx = 5)
		self.month_var = IntVar(date_widgets_frame)
		self.month_var.set(today.month)
		self.month_spin = Spinbox(date_widgets_frame, from_ = 0, to = 12, font  = (DEFAULT_FONT, 12), width = 5, textvariable= self.month_var)
		self.month_spin.grid(row = 0 , column = 1, padx = 5)

		day_label = Label(date_widgets_frame, text = 'Day:')
		day_label.grid(row = 0 , column = 2, padx = 5)
		self.day_var = IntVar(date_widgets_frame)
		self.day_var.set(today.day)
		self.day_spin = Spinbox(date_widgets_frame, from_ = 1, to = 30, font  = (DEFAULT_FONT, 12), width = 5, textvariable= self.day_var)
		self.day_spin.grid(row = 0 , column = 3, padx = 5)

		year_label = Label(date_widgets_frame, text = 'Year (20_x_x_):')
		year_label.grid(row = 0 , column = 4, padx = 5)
		self.year_var = IntVar(date_widgets_frame)
		self.year_var.set(today.year%100)
		self.year_spin = Spinbox(date_widgets_frame, from_ = 0, to = 99, font  = (DEFAULT_FONT, 12), width = 5, textvariable= self.year_var)
		self.year_spin.grid(row = 0 , column = 5, padx = 5)


		#assign to date! button
		refresh_button = Button(self, text = 'Assign to Date', command = lambda: [self.assign_date()])
		refresh_button.pack(pady =10)

class Moodboard(Frame):
	def __init__(self, root):
		super().__init__(root)
		self.root = root
		self.current_page = 0
		self.display = []
		self.moodboard_frame = None
		self.bottom_nav_frame = None

		self.top_navigation_widgets(self.root)
		self.header()
		self.load_moodboard_display(self.root)

	def top_navigation_widgets(self, root):
		nav_frame = Frame(self, width = APP_WIDTH, height = 20)
		nav_frame.pack(fill = BOTH)
		back_button = Button(nav_frame, width = 10, height = 1, text = '< Main')
		back_button['command'] = lambda: root.swap_frames(Welcome_page)
		back_button.pack(side = LEFT, anchor = NW, pady = NAV_BUTTON_PADY, padx = NAV_BUTTON_PADX)
	
	def header(self):
		Label(self, text = 'Moodboard',font = ('Helvetica', 16)).pack()
		Frame(self, height =15).pack(fill =Y, side =TOP) # extra paddin

	def refresh_current_page(self):
		self.current_page = 0
		   
	def make_display(self):
		#returns 2d list of all files based on category
		temp_list = [file for file in os.listdir('moodboard/')]

		display_list = []
		page = []
		while len(temp_list) > 0:
			temp_garm = temp_list.pop(0)
			page.append(temp_garm)
			if len(page) == 4:
				display_list.append(page)
				page = []
		display_list.append(page)

		return display_list

		
	def load_moodboard_display(self, root):
		#closet frame
		if self.moodboard_frame != None:
			self.moodboard_frame.destroy()

		self.moodboard_frame = Frame(self, width = APP_WIDTH, height = 500)
		self.moodboard_frame.pack()
		
		#organize moodboard into pages
		self.display = self.make_display()

		#load all moodboard images 
		current_display = self.display[self.current_page]
		counter =  0
		for r in range(2):
			for c in range(2):
				if counter < len(current_display):
					path = "moodboard/{x}".format(x = current_display[counter])
					img_file = Image.open(path)
					
					img_file = img_file.resize((300, 300), Image.ANTIALIAS)
					photo = ImageTk.PhotoImage(img_file)
					image = Label(self.moodboard_frame, image = photo, text = current_display[counter])
					image.grid(row = r, column = c, padx = 10, pady = 10)
					image.image = photo

					counter+=1

		self.bottom_navigation_widgets()

	
	def nav_right(self):
		if self.current_page == len(self.display) -1:
			self.current_page = 0
		else:
			self.current_page += 1
		self.load_moodboard_display(self.root)
		
	def nav_left(self):
		if self.current_page == 0:
				self.current_page = len(self.display) - 1
		else:
			self.current_page -= 1
		self.load_moodboard_display(self.root)

	def bottom_navigation_widgets(self):
		#nav buttons frame
		if self.bottom_nav_frame != None:
			self.bottom_nav_frame.destroy()
		self.bottom_nav_frame = Frame(self, height = 50, width = 1000)
		self.bottom_nav_frame.pack(side = 'top', pady = 10)

		#nav buttons
		back_button = Button(self.bottom_nav_frame, width = 5, text = '<', command = self.nav_left)
		back_button.grid(row = 0, column = 0, padx = 5)

		next_button = Button(self.bottom_nav_frame, width = 5, text  = '>', command = self.nav_right)
		next_button.grid(row = 0, column = 1, padx = 5)

if __name__ == "__main__":
	app = Wardrobe_App()
	app.mainloop()