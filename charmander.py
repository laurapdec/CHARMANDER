import imageio,random,math,pyglet,subprocess,time
import matplotlib.pyplot as plt
import numpy as np
import cantera as ct
from tkinter import *
from tkinter import ttk,filedialog,messagebox
from PIL import ImageTk,Image
from mpl_toolkits.mplot3d import Axes3D
from os import remove
from numpy.random import random
from random import randint
from math import exp

###############################################################################
##                         CLASSE INTERFACE GRÁFICA                          ##
###############################################################################

class App:
	def __init__(self,master):

		self.master=master

		self.elements=[]
		self.saved=False

		self.style = ttk.Style(master)

		self.style.theme_use('xpnative')
		menu=Menu(master)
		menu.add_command(label="Import",command=self.import_)
		menu.add_command(label="Help",command=self.help)

		subMenu = Menu(menu, tearoff=False)
		menu.add_cascade(label='Theme', menu=subMenu) 
		subMenu.add_command(label="White",command=self.whiteTheme)
		subMenu.add_command(label="Dark",command=self.darkTheme)
		master.config(menu=menu)

		



		CTIlabel = ttk.Labelframe(master, text='Select the .CTI file')
		self.CTIvar = StringVar()
		CTIcombo = ttk.Combobox(CTIlabel,state="readonly", textvariable=self.CTIvar ,values=["GRI Mech 3.0", "SP21RE","CH4 Global","Local file"])
		
		CTIcombo.grid(pady=5, padx=10)
		CTIlabel.grid(row=0, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)       

		CTIcombo.bind('<<ComboboxSelected>>', self.checkCTI)
	


		## Mixture Model

		MODELlabel = ttk.Labelframe(master, text='Select the mixing model')
		self.MODELvar = StringVar()
		MODELcombo = ttk.Combobox(MODELlabel,state="readonly", textvariable=self.MODELvar ,values=["Curl","Curl Modificado","IEM/LMSE", "EIEM","Langevin","Langevin Estendido"])
		self.MODELvar.set("IEM/LMSE")
		MODELcombo.grid(pady=5, padx=10)
		MODELlabel.grid(row=1,column=0, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)  

		MODELcombo.bind('<<ComboboxSelected>>', self.checkMODEL)     

		## Parameters

		ParamLabel = ttk.Labelframe(master, text='Parameters')
		ParamLabel.grid(row=0,column=1,rowspan=2, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)  
		
		
		Label(master,text="\u03b1:").grid(in_=ParamLabel,row=0, sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 
		self.Alphastring=StringVar()
		self.Alphastring.set(0.5)
		self.entryAlpha=Entry(master,textvariable=self.Alphastring,state='disabled')
		self.entryAlpha.grid(in_=ParamLabel,row=0, column=1, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)
		
		Label(master,text="C\u03c9 :").grid(in_=ParamLabel,row=1, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)
		self.Cwstring=StringVar()
		self.Cwstring.set(2)
		self.entryCw=Entry(master,textvariable=self.Cwstring,state='disabled')
		self.entryCw.grid(in_=ParamLabel,row=1, column=1, sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 

		Label(master,text="d0 :").grid(in_=ParamLabel,row=2, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)
		self.D0string=StringVar()
		self.D0string.set(0.5)
		self.entryD0=Entry(master,textvariable=self.D0string,state='disabled')
		self.entryD0.grid(in_=ParamLabel,row=2, column=1, sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 

		self.Param=[self.Alphastring,self.Cwstring,self.D0string]
		## Simulation time parameters

		TimeLabel = ttk.Labelframe(master, text='Time settings')
		TimeLabel.grid(row=0,column=2,rowspan=2,sticky='W', padx=5, pady=5, ipadx=5, ipady=5)  
		
		
		Label(master,text="t_f [s] :").grid(in_=TimeLabel,row=0, sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 
		self.TFstring=StringVar()
		self.TFstring.set(0.01)
		self.entryTF=Entry(master,textvariable=self.TFstring)
		self.entryTF.grid(in_=TimeLabel,row=0, column=1, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)
		
		Label(master,text="dt [s] :").grid(in_=TimeLabel,row=1, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)
		self.DTstring=StringVar()
		self.DTstring.set(0.001)
		self.entryDT=Entry(master,textvariable=self.DTstring)
		self.entryDT.grid(in_=TimeLabel,row=1, column=1, sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 


		


		## Boundary Conditions
		
		
		Boundlabel = ttk.Labelframe(master, text='Boundary Conditions')
		Boundlabel.grid(sticky=E+W,row=2,columnspan=4,rowspan=3,padx=5, pady=5, ipadx=5, ipady=5)


		# Setting Composition


		BigFrame=Frame(Boundlabel)

		BigFrame.grid(column=3,row=0,sticky=W+N,rowspan=30)

		self.canvas = Canvas(self.master, width=200, height=500,bd=0,highlightthickness=0, relief='ridge')
		self.CompositionLabel = ttk.Labelframe(self.canvas, text='Compositions')
		sbar = Scrollbar(self.master, orient="vertical", command=self.canvas.yview)
		
		self.canvas.config(yscrollcommand=sbar.set)

		self.canvas.pack(in_=BigFrame,side="left")
		sbar.pack(in_=BigFrame,side="left", fill="y")
		self.canvas.create_window((2,2), window=self.CompositionLabel, anchor="nw",  tags="self.CompositionLabel")        
		
		self.CompositionLabel.bind("<Configure>", self.onFrameConfigure)
		

		
				
		# Select Wall

		Label(master,text="Select the wall :").grid(in_=Boundlabel,row=0,column=0 ,sticky='W', padx=5, pady=5, ipadx=5, ipady=5)
		self.Boundvar = StringVar()
		Boundcombo = ttk.Combobox(Boundlabel,state="readonly", textvariable=self.Boundvar ,values=["LEFT", "RIGHT", "FRONT", "BACK", "UP", "DOWN","fill","Half 1","Half 2"])
		Boundcombo.grid(row=0,column=1,pady=5, padx=10)

		self.Boundvar.set("LEFT")
		
		Boundcombo.bind('<<ComboboxSelected>>', self.newWall)

		#Image of wall

		self.ImgPath = StringVar()
		self.ImgPath.set( "wall/LEFT.png")
		self.WallImg = ImageTk.PhotoImage(Image.open(self.ImgPath.get()))

		self.Imglabel = Label(image=self.WallImg)
		self.Imglabel.img = self.WallImg # this line need to prevent gc
		self.Imglabel.grid(in_=Boundlabel,row=0,column=2)

		# Create particles here?
		
		
		self.createPart = IntVar()
		self.checkIn=Checkbutton(master, text="Generate particles in this Wall?",variable=self.createPart,command=self.checkenable)
		self.checkIn.grid(in_=Boundlabel,sticky=W,row=1,columnspan=3)


		# Create particles here later?
		
		
		self.createPartT = IntVar()
		self.checkInT=Checkbutton(master, text="Generate particles in this Wall every time step?",variable=self.createPartT,state='disabled')
		self.checkInT.grid(in_=Boundlabel,sticky=W,row=2,columnspan=3)

		# Setting Number of Particles
		
		Label(master,text="Number of particles generated by time step :").grid(in_=Boundlabel,row=3 ,columnspan=2,sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 
		self.Nstring=StringVar()
		self.entryN=Entry(master,textvariable=self.Nstring,state='disabled')
		self.Nstring.set(0)
		self.entryN.grid(in_=Boundlabel,row=3, column=2, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)
		
		# Setting Temperature
		
		Label(master,text="T [K] :").grid(in_=Boundlabel,row=4 ,columnspan=2,sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 
		self.Tstring=StringVar()
		self.entryT=Entry(master,textvariable=self.Tstring,state='disabled')
		self.entryT.grid(in_=Boundlabel,row=4, column=2, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)


		
		
		# Setting Velocities

		VelocityLabel = ttk.Labelframe(Boundlabel, text='Velocities')
		VelocityLabel.grid(sticky=E+W,row=5,padx=5, pady=5, ipadx=5, ipady=5,columnspan=3)
		
		
		Label(master,text="u [m/s] :").grid(in_=VelocityLabel,row=3, sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 
		self.Ustring=StringVar()
		self.Ustring.set(0)
		self.entryU=Entry(master,textvariable=self.Ustring,state='disabled')
		self.entryU.grid(in_=VelocityLabel,row=3, column=1, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)
		
		Label(master,text="v [m/s] :").grid(in_=VelocityLabel,row=4, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)
		self.Vstring=StringVar()
		self.Vstring.set(0)
		self.entryV=Entry(master,textvariable=self.Vstring,state='disabled')
		self.entryV.grid(in_=VelocityLabel,row=4, column=1, sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 

		Label(master,text="w [m/s] :").grid(in_=VelocityLabel,row=5, sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 
		self.Wstring=StringVar()
		self.Wstring.set(0)
		self.entryW=Entry(master,textvariable=self.Wstring,state='disabled')
		self.entryW.grid(in_=VelocityLabel,row=5, column=1, sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 




		# Wall Reflect or Pass
		
		self.WallReflect = IntVar()
		Checkbutton(master, text="Reflects?", variable=self.WallReflect).grid(in_=Boundlabel,row=6, sticky=W,columnspan=3)

		# Save Wall
		
		self.save=Button(Boundlabel,text="Save Wall",command=self.saveWall)
		self.save.grid(row=7, columnspan=2, sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 
	

		## Plot Configure

		## Run

		self.run=Button(master,text="Run",command=self.running)
		self.run.grid(row=1, column=5 , sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 


		## Prompt

		
		self.fontsize=11

		PromptFrame=Frame(master)
		PromptFrame.grid(row=2,column=4,sticky='W', padx=5, pady=5)
		Label( PromptFrame,text='LOG Console',bg='white',font=('freemono', 11, 'italic'),bd=1,highlightthickness=2, relief='ridge').grid(row=0,columnspan=2,sticky="ew")
		
		bar_prompt = Scrollbar(PromptFrame, orient="vertical")
		self.prompt=Canvas(PromptFrame,width=500, height=500,bg='black',bd=0,highlightthickness=2, relief='ridge',yscrollcommand=bar_prompt.set)

		bar_prompt.config(command=self.prompt.yview)

		self.prompt.config(scrollregion=self.prompt.bbox('all'))

		bar_prompt.grid(row=1,column=1,sticky="ns")
		self.prompt.grid(row=1,column=0)


		## Plot parameters


		PlotFrame=Frame(self.master,bg='')

		PlotFrame.grid(row=0,column=4,rowspan=2,sticky='W', padx=5, pady=5, ipadx=5, ipady=5)  

		self.plotcanvas = Canvas(self.master, width=300, height=125,bd=0,highlightthickness=0, relief='ridge')
		self.PlotLabel = ttk.Labelframe(self.plotcanvas, text='Plot settings')
		plot_bar = Scrollbar(self.master, orient="horizontal", command=self.plotcanvas.xview)
		
		self.plotcanvas.config(xscrollcommand=plot_bar.set)

		self.plotcanvas.pack(in_=PlotFrame,side="top")
		plot_bar.pack(in_=PlotFrame,side="top", fill="x")
		self.plotcanvas.create_window((2,2), window=self.PlotLabel, anchor="nw",  tags="self.PlotLabel")        
		
		self.PlotLabel.bind("<Configure>", self.onFrameConfigurePlot)
		


		## Burning MODEL

		Burnlabel = ttk.Labelframe(master, text='Select the reaction model')
		self.Burnvar = StringVar()
		self.Burnvar.set("Cantera")
		Burncombo = ttk.Combobox(Burnlabel,state="readonly", textvariable=self.Burnvar ,values=["Cantera","Don't burn"])
		
		Burncombo.grid(pady=5, padx=10)
		Burnlabel.grid(row=0, column=5,sticky='W', padx=5, pady=5, ipadx=5, ipady=5)       

		
		
		## Default White Theme
		self.whiteTheme()

	def promptPrint(self,message,cont=False):
		global used
		start=10
		height=(self.fontsize+10) * used + 10
		if cont:
			start+=30
			height-=5

		used+=1
		a=self.prompt.create_text((start,height),anchor="w",text=message,fill='green',font=('freemono', self.fontsize))
		x1,y1,x2,y2=self.prompt.bbox(a)


		if (x2-x1) >480:
			n=int(480*len(message)/(x2-x1))
			self.prompt.itemconfigure(a,text=message[:n])
			self.promptPrint(message[n:],True)

		bound=[self.prompt.bbox('all')[0],self.prompt.bbox('all')[1],self.prompt.bbox('all')[2],self.prompt.bbox('all')[3]+200]

		self.prompt.config(scrollregion=bound)

	def whiteTheme(self):
		self.color="white"
		self.textcolor="black"
		self.updateTheme()

	def darkTheme(self):
		self.color="#5b5b5b"
		self.textcolor='white'
		self.updateTheme()

	def updateTheme(self):
		self.master.configure(bg=self.color)
		self.style.configure('TFrame',bg=self.color)
		self.style.configure('TLabelframe', background=self.color)
		self.style.configure('TLabelframe.Label', background=self.color,foreground=self.textcolor)
		self.style.configure('TLabel', background=self.color,foreground=self.textcolor)
		for wid in self.master.winfo_children()+self.CompositionLabel.winfo_children()+self.PlotLabel.winfo_children():
			if type(wid)==Label  :
				wid.configure(bg=self.color,foreground=self.textcolor)
			elif type(wid)==Canvas or type(wid)==Checkbutton:
				wid.configure(bg=self.color)

	def newWall(self,event=None):

		if not self.saved :
			if messagebox.askokcancel("Warning", "Wish to save unsaved wall?"):
				self.saveWall()

		self.saved=False
		stri="wall/"+self.Boundvar.get()+".png"
		self.ImgPath.set(stri)
		photo=ImageTk.PhotoImage(Image.open(self.ImgPath.get()))
		self.Imglabel.configure(image= photo)
		self.Imglabel.image=photo

		self.createPart.set(0)
		self.createPartT.set(0)
		self.checkenable()
		self.Nstring.set(0)
		self.Ustring.set(0)
		self.Vstring.set(0)
		self.Wstring.set(0)
		self.WallReflect.set(0)
		for id, field in enumerate(self.elements):
			self.stringComposition[id].set(0)

	def saveWall(self):

		if self.createPart.get()==1:
			stringComposition_temp=[]

			for id,comp in enumerate(self.stringComposition):
				stringComposition_temp.append(comp.get())

			if self.Boundvar.get() == "LEFT":
				strin=1
				self.promptPrint("Wall "+self.Boundvar.get() +" saved!")
			elif self.Boundvar.get() == "RIGHT":
				strin=2
				self.promptPrint("Wall "+self.Boundvar.get() +" saved!")
			elif self.Boundvar.get() == "FRONT":
				strin=3
				self.promptPrint("Wall "+self.Boundvar.get() +" saved!")
			elif self.Boundvar.get() == "BACK":
				strin=4
				self.promptPrint("Wall "+self.Boundvar.get() +" saved!")
			elif self.Boundvar.get() == "UP":
				strin=5
				self.promptPrint("Wall "+self.Boundvar.get() +" saved!")
			elif self.Boundvar.get() == "DOWN":
				strin=6
				self.promptPrint("Wall "+self.Boundvar.get() +" saved!")
			elif self.Boundvar.get() == "fill":
				strin=7
				self.promptPrint(self.Boundvar.get() +" saved!")
			elif self.Boundvar.get() == "Half 1":
				strin=8
				self.promptPrint(self.Boundvar.get() +" saved!")
			elif self.Boundvar.get() == "Half 2":
				strin=9
				self.promptPrint(self.Boundvar.get() +" saved!")
			self.Wall[strin-1]['GenDt']=self.createPartT.get()
			self.Wall[strin-1]['Nstring']=self.Nstring.get()
			self.Wall[strin-1]['Tstring']=self.Tstring.get()
			self.Wall[strin-1]['Ustring']=self.Ustring.get()
			self.Wall[strin-1]['Vstring']=self.Vstring.get()
			self.Wall[strin-1]['Wstring']=self.Wstring.get()
			self.Wall[strin-1]['WallReflect']=self.WallReflect.get()
			self.Wall[strin-1]['stringComposition']=stringComposition_temp


		self.save.config(bg='green')
		self.saved=True
					
	def checkCTI(self,event=None):


		for id, field in enumerate(self.elements):
			self.entryComposition[id].grid_forget()
			self.labelComposition[id].grid_forget()
			self.checkComposition[id].grid_forget()
			self.labelComposition[id].grid_forget()

			
		if (self.CTIvar.get()=="SP21RE"):
			self.CTIfile="CTI Files\\sp21re.cti"
		elif (self.CTIvar.get()=="GRI Mech 3.0"):
			self.CTIfile="CTI Files\\GRI30.cti"
		elif (self.CTIvar.get()=="CH4 Global"):
			self.CTIfile="CTI Files\\methane_global.cti"
		elif (self.CTIvar.get()=="Local file"):
			self.CTIfile = filedialog.askopenfilename(title='Select file',filetypes = (("CTI files","*.cti"),("all files","*.*")))

		self.elements=ct.Solution(self.CTIfile).species_names
		self.promptPrint(self.CTIfile+ " was just imported")

		global elementos
		elementos=self.elements

		self.checkComposition=[0]*len(self.elements)
		self.PlotConfiguration=[0]*len(self.elements)
		self.stringComposition=[0]*len(self.elements)
		self.labelComposition=[0]*len(self.elements)
		self.entryComposition=[0]*len(self.elements)

		for id, field in enumerate(self.elements):
			frammim=Frame(self.PlotLabel,bg='')
			frammim.grid(row=id%4 ,column=id//4) 
			self.PlotConfiguration[id]=StringVar()
			self.PlotConfiguration[id].set(0)
			self.checkComposition[id]=Checkbutton(self.PlotLabel,variable=self.PlotConfiguration[id])
			self.checkComposition[id].grid(in_=frammim,row=0,column=0,sticky='EN') 
			self.labelComposition[id]=Label(self.PlotLabel,text=field)
			self.labelComposition[id].grid(in_=frammim,row=0,column=1,sticky='WN') 
		
		for id, field in enumerate(self.elements):
			self.labelComposition[id]=Label(self.CompositionLabel,text=field)
			self.labelComposition[id].grid(row=id ,sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 
			self.stringComposition[id]=StringVar()
			self.stringComposition[id].set(0)
			self.entryComposition[id]=Entry(self.CompositionLabel,textvariable=self.stringComposition[id],state='disabled')
			self.entryComposition[id].grid(row=id, column=1, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)
		self.checkenable()

		self.Wall=[]
		for i in range(0,9):
			self.Wall.append({'GenDt':0,'Nstring':'0','Tstring':'0','Ustring':'0','Vstring':'0','Wstring':'0','stringComposition':[0.0]*len(self.elements),'WallReflect':0})
		self.save.config(bg='red')
		self.updateTheme()

	def onFrameConfigure(self, event):
		self.canvas.configure(scrollregion=self.canvas.bbox("all"))


	def onFrameConfigurePlot(self, event):
		self.plotcanvas.configure(scrollregion=self.plotcanvas.bbox("all"))

	def checkenable(self):
		if (self.createPart.get()==0):
			self.checkInT.configure(state='disabled')
			self.entryT.configure(state='disabled')
			self.entryN.configure(state='disabled')
			self.entryU.configure(state='disabled')
			self.entryV.configure(state='disabled')
			self.entryW.configure(state='disabled')
			for id, field in enumerate(self.elements):
				self.entryComposition[id].configure(state='disabled')
				

		else:
			self.checkInT.configure(state='normal')
			self.entryT.configure(state='normal')
			self.entryN.configure(state='normal')
			self.entryU.configure(state='normal')
			self.entryV.configure(state='normal')
			self.entryW.configure(state='normal')
			for id, field in enumerate(self.elements):
				self.entryComposition[id].configure(state='normal')

	def saveInput(self):

		self.promptPrint("The conditions set are available in the file setup.txt in the folder OUTPUT")
		setup=open("OUTPUT\\setup.char",'w')
		setup.write(self.CTIfile + "\n")
		setup.write(self.MODELvar.get()+ "\n")
		setup.write(self.Param[0].get()+" "+self.Param[1].get()+" "+self.Param[2].get()+ "\n")

		for i in range(0,9):
			name="\n \n Wall " +str(i+1)+ " \n \n "
			setup.write(name)
			setup.write("\n GenDt:"+str(self.Wall[i]['GenDt']))
			setup.write("\n N:"+self.Wall[i]['Nstring'])
			setup.write("\n T:"+self.Wall[i]['Tstring'])
			setup.write("\n U:"+self.Wall[i]['Ustring'])
			setup.write("\n V:"+self.Wall[i]['Vstring'])
			setup.write("\n W:"+self.Wall[i]['Wstring'])
			setup.write("\n Wall Reflect:"+str(self.Wall[i]['WallReflect']))
			setup.write("\n Composition: \n")
			for id, element in enumerate(self.elements):
				setup.write(element+":"+str(self.Wall[i]['stringComposition'][id]) + '\n')

		setup.close()

	def run(self):
		try:
			self.running()
		except:
			self.promptPrint("Insuficient data")
			print(sys.exc_info()[0])
			self.run.config(state='normal')

	def running(self):
		self.run.config(state='disabled')
		if not self.saved :
			if messagebox.askokcancel("Warning", "Wish to save unsaved wall?"):
				self.saveWall()
			else:
				self.run.config(state='normal')
				return None


		self.Param=[self.Alphastring,self.Cwstring,self.D0string]

		self.saveInput()

		if self.MODELvar.get()=="Curl":
			Model=Simulate_Curl
		elif self.MODELvar.get()=="Curl Modificado":
			Model=Simulate_CurlM
		elif self.MODELvar.get()=="IEM/LMSE":
			Model=Simulate_IEM
		elif self.MODELvar.get()=="EIEM":
			Model=Simulate_EIEM
		elif self.MODELvar.get()=="Langevin":
			Model=Simulate_Lange
		elif self.MODELvar.get()=="Langevin Estendido":
			Model=Simulate_LangeEst


		if self.Burnvar.get()=="Cantera":
			React=BurnCantera
		elif self.Burnvar.get()=="Don't burn":
			React=DontBurn

		PlotConfigurationsent=[]
		for i in range(0,len(self.PlotConfiguration)):
			PlotConfigurationsent.append(self.PlotConfiguration[i].get())

		Simulate(self.Wall,self.Param,self.DTstring,self.TFstring,Model,React,PlotConfigurationsent)

		self.stop_loading()

		self.run.config(state='normal')

	def stop_loading(self):

		imagelist=["done\\0.png","done\\1.png","done\\2.png","done\\3.png","done\\4.png","done\\5.png","done\\6.png","done\\7.png","done\\8.png"]    
		
		self.giflist = []
		for imagefile in imagelist:
			photo = PhotoImage(file=imagefile)
			self.giflist.append(photo)
		for gif in self.giflist:
			try:
				self.prompt.delete(last)
			except:
				print()
			last=self.prompt.create_image(250, 500-gif.height()//2,	 image=gif)
			self.prompt.update()
			self.master.update()
			time.sleep(0.1) 
		time.sleep(1)
		self.promptPrint("Finished.")
		self.prompt.delete(last)

	def import_(self):
		filename = filedialog.askopenfilename(initialdir = "C:\\Users\\laura\\Desktop\\IC\\CHARMANDER\\beta\\OUTPUT",title='Select file',filetypes = (("CHARMANDER files","*.char"),("all files","*.*")))
		doc=open(filename,'r')

		self.promptPrint("The conditions set in the file " + doc.name+ " are now being used")


		self.CTIfile=doc.readline().strip('\n')
		self.checkCTI()
		if (self.CTIfile=="CTI Files\\sp21re.cti"):
			self.CTIvar.set("SP21RE")
		elif (self.CTIfile=="CTI Files\\GRI30.cti"):
			self.CTIvar.set("GRI Mech 3.0")
		elif (self.CTIfile=="CTI Files\\methane_global.cti"):
			self.CTIvar.set("CH4 Global")


		self.MODELvar.set(doc.readline().strip('\n'))


		Param=doc.readline().strip('\n').split(' ')
		self.Param[0].set(Param[0])
		self.Param[1].set(Param[1])
		self.Param[2].set(Param[2])

		for f in range(0,9):
			doc.readline()
			doc.readline()
			i=int(doc.readline()[6])
			doc.readline()
			doc.readline()
			self.Wall[i-1]['GenDt']=int(doc.readline()[7:].strip('\n'))
			self.Wall[i-1]['Nstring']=doc.readline()[3:].strip('\n')
			self.Wall[i-1]['Tstring']=doc.readline()[3:].strip('\n')
			self.Wall[i-1]['Ustring']=doc.readline()[3:].strip('\n')
			self.Wall[i-1]['Vstring']=doc.readline()[3:].strip('\n')
			self.Wall[i-1]['Wstring']=doc.readline()[3:].strip('\n')
			self.Wall[i-1]['WallReflect']=int(doc.readline()[14:].strip('\n'))
			doc.readline()
			for id, element in enumerate(self.elements):
				a=doc.readline()
				self.Wall[i-1]['stringComposition'][id]=float(a[a.find(':')+1:].strip('\n'))

		doc.close()
		self.saved=True

	def checkMODEL(self,event=None):
		self.entryCw.configure(state="disabled")
		self.entryAlpha.configure(state="disabled")
		self.entryD0.configure(state="disabled")
		if self.MODELvar.get() == "IEM/LMSE":
			self.entryCw.configure(state="normal")
		elif self.MODELvar.get() == "Curl Modificado":
			self.entryAlpha.configure(state="normal")
		elif self.MODELvar.get() == "Langevin" or self.MODELvar.get() == "Langevin Estendido" :
			self.entryD0.configure(state="normal")

	def help(self):
		subprocess.Popen(["manual.pdf"],shell=True)

###############################################################################
##                               CLASSE PARTÍCULA                            ##
###############################################################################

class part():
	def __init__(self,position,velocity,comp,T):
		global elementos
		[x,y,z]=position 
		[u,v,w]=velocity
		self.x=x
		self.y=y
		self.z=z

		self.u=u
		self.v=v
		self.w=w

		self.T=T
		self.comp=comp


		self.old_position=np.array([100,100,100])

		self.gamma=0.01
		self.gamma_old=0.01
		self.gamma_t=0.0
		self.gamma_t_old=0.0

		self.P=101325       #[Pa]
		self.rho=287/self.P*self.T      #[Kg/m³]

		self.R_r=0

		omega_te=C_omega*(self.gamma+self.gamma_t)/(delta**2)
		self.omega={}
		for id, element in enumerate(elementos):
			self.omega[elementos[id]]=omega_te

		self.gas=ct.Solution(ap.CTIfile)
		self.gas.TPX=self.T,self.P,self.comp


	def getPosition(self):
		return np.array([self.x,self.y,self.z])

	def getOlderPosition(self):
		return self.old_position

	def getVelocity(self):
		return np.array([self.u,self.v,self.w])

	def setPosition(self,pos):
		self.old_position=np.array([self.x,self.y,self.z])
		self.x=pos[0]
		self.y=pos[1]
		self.z=pos[2]

	def setVelocity(self,vel):
		self.u=vel[0]
		self.v=vel[1]
		self.w=vel[2]

	def updateGamma(self,new):
		self.gamma_old=self.gamma
		self.gamma=new

###############################################################################
##                              FUNÇÕES DO PROGRAMA                          ##
###############################################################################

def random_float(min,max):
	result=0
	while result >=max or result<=min:
		result=random()*(max-min)+min
	return result

def plot_3D(x,y,z,data,plot):
	global frame_3D,filenames_3D
	c=data[0]
	fig=plt.figure()
	ax = fig.add_subplot(1,1,1, projection='3d')
	pnt1=ax.scatter(x,y,z,c=c,cmap=plt.cm.jet, edgecolor='black')
	cbar=plt.colorbar(pnt1)
	pnt1.set_clim(0.0,1.0)
	plt.xlim(0.0,1.0)
	plt.ylim(0.0,1.0)
	ax.set_zlim3d(0.0,1.0)
	spe="% de "+plot[0]
	cbar.set_label(spe)
	ax.set_xlabel('Eixo x')
	ax.set_ylabel('Eixo y')
	ax.set_zlabel('Eixo z')
	frame_3D[0]+=1
	frame_3D[1]=t
	name='OUTPUT/frames/t_'+str(frame_3D[0])+'.png'
	filenames_3D.append(name)
	plt.savefig(name)
	plt.close('all')

def plot_comp(x,data,plot):
	global filenames_comp,frame_comp
	#plt.plot(x,h,'.b',LineWidth=0.1)
	for p in data:
		plt.plot(x,p,'.',LineWidth=0.1)
	#plt.plot(x,o,'.r',LineWidth=0.1)
	plt.axis([0,1,0,1])
	plt.xlabel('Eixo x')
	plt.ylabel('%')
	plt.legend(plot)
	frame_comp[0]+=1
	frame_comp[1]=t
	name='OUTPUT/frames/h_'+str(frame_comp[0])+'.png'
	filenames_comp.append(name)
	plt.savefig(name)
	plt.close('all')

def plot_PDF(data_t,plot): 
	global frame_PDF,filenames_PDF,frame_CDF,filenames_CDF
	p_t=[]
	pp_t=[]
	for data in data_t:
		p=np.zeros(len(data))
		k=0
		for i in range(0,len(data)):  
			for r in np.linspace(0,1,len(p)):
				if data[i] >= r and data[i] <= n_div + r:
					p[k] += 1
				k +=1
			k=0
		pp= np.array(p)*100 / npart
		p_t.append(p)
		pp_t.append(pp)
	
	x = np.linspace(0, 1 , len(p))
	for p in p_t:
		plt.plot(x, p, 'o-')
	plt.axis([-0.1,1.1,0,len(p)])
	plt.grid()
	plt.ylabel('[]')
	plt.legend(plot)
	frame_CDF[0]+=1
	frame_CDF[1]=t
	name='OUTPUT/frames/cdf_'+str(frame_CDF[0])+'.png'
	filenames_CDF.append(name)
	plt.savefig(name)
	plt.close('all')

	for pp in pp_t:
		plt.plot(x, pp, '.-')

	plt.axis([-0.1,1.1,0,100])
	plt.ylabel('Probabilidade de [] %')
	plt.xlabel('[]')
	plt.legend(plot)
	plt.grid()
	#plt.legend(["$H_2$","$H_2O$","$O_2$"])
	frame_PDF[0]+=1
	frame_PDF[1]=t
	name='OUTPUT/frames/pdf_'+str(frame_PDF[0])+'.png'
	filenames_PDF.append(name)
	plt.savefig(name)
	plt.close('all')


###############################################################################
##                               FUNÇÃO SIMULAR                              ##
###############################################################################

def Simulate(Wall,Param,DT,TF,Model,React,PlotConfiguration):

	global frame_3D,frame_CDF,frame_comp,frame_PDF,filenames_3D,filenames_comp,filenames_CDF,filenames_PDF
	global t,dt,npart,part_u,C_omega,alpha,d0
	global erro, used
	erro=0

	ap.promptPrint("Setting initial parameters...")
	root.update()

	part_u=[]
	filenames_3D=[]
	filenames_comp=[]
	filenames_CDF=[]
	filenames_PDF=[]

	frame_3D=[0,0]
	frame_CDF=[0,0]
	frame_comp=[0,0]
	frame_PDF=[0,0]

	## Reading Plot Parameters

	plot=[]
	for id,element in enumerate(elementos):
		if PlotConfiguration[id]=='1':
			plot.append(element)

	## Reading Time Parameters

	dt=float(DT.get())          #Passo de Tempo
	t_f=float(TF.get())         #Tempo final

	## Reading Parameters

	alpha=float(Param[0].get())
	C_omega=float(Param[1].get())
	d0=float(Param[2].get())

	GenPar=[]

	ap.promptPrint("Setting boundary conditions...")
	root.update()


	rand= lambda : random()
	one = lambda : 1
	zero= lambda : 0

	## Reading Boundary Conditions in Wall

	for i_wall in range (0,len(Wall)):
		
		npart=int(Wall[i_wall]["Nstring"])
		if npart>0:
			for i in range(0,npart):
				u=float(Wall[i_wall]["Ustring"])
				v=float(Wall[i_wall]["Vstring"])
				w=float(Wall[i_wall]["Wstring"])
				T=float(Wall[i_wall]["Tstring"])
				comp={}
				for id, element in enumerate(elementos):
					comp[element]=float(Wall[i_wall]['stringComposition'][id])

				if i_wall==0:
					x=zero
					y=rand
					z=rand
				elif i_wall==1:
					x=one
					y=rand
					z=rand
				elif i_wall==2:
					x=rand
					y=zero
					z=rand
				elif i_wall==3:
					x=rand
					y=one
					z=rand
				elif i_wall==4:
					x=rand
					y=rand
					z=one
				elif i_wall==5:
					x=rand
					y=rand
					z=zero
				elif i_wall==6:
					x=rand
					y=rand
					z=rand
				elif i_wall==7:
					x=rand
					y=rand
					z= lambda : random_float(0,0.5)
				elif i_wall==8:
					x=rand
					y=rand
					z= lambda : random_float(0.5,1)

				if Wall[i_wall]["GenDt"]==0:
					part_u.append(part([x(),y(),z()],[u,v,w],comp,T))
				elif Wall[i_wall]["GenDt"]==1:
					GenPar.append([[x,y,z],[u,v,w],comp,T])
				else:
					print(Wall[i_wall]["GenDt"])


	for id, particle in enumerate(GenPar):
		inputt=[]
		inputt.append(particle[0][0]())
		inputt.append(particle[0][1]())
		inputt.append(particle[0][2]())
		part_u.append(part(inputt,particle[1],particle[2],particle[3]))

	V_avg=np.zeros(3)

	ap.promptPrint("Starting simulation...")
	root.update()
	###############################################################################
	##                          INÍCIO DO LOOP                                   ##
	###############################################################################

	per=ap.prompt.create_text((10, ( ap.fontsize+10) * used + 10),anchor="w",text="0 %",fill='green',font=('freemono', ap.fontsize))
	per_bar=ap.prompt.create_rectangle((10,    ( ap.fontsize)* used+ 10     ,10,     ( ap.fontsize) * used+ ap.fontsize + 10)   ,fill='green')
	used+=2
	  
	for t in np.linspace(0,t_f,int(t_f/dt)):

		# Atualizando porcentagem no prompt

		pri=str(round(t/t_f*(100),1))+" %"
		ap.prompt.itemconfigure(per,text=pri)
		ap.prompt.coords(per_bar,10,( ap.fontsize+10) * (used -1)+ 5,10+round(t/t_f*(480),1), ( ap.fontsize+10) * (used-1)+ ap.fontsize + 5)
		root.update()
		

	  #Resetando os vetores e valores necessários
		x=[]
		y=[]
		z=[]
		p=[]
		for i in plot:
			p.append([])
		l=0
		V_avg=np.array([.0,.0,.0])

	  #Excluindo particulas fora do volume de controle e movendo as outras

		npart=len(part_u)
		for id, part_i in enumerate(part_u):
		  V_avg+=part_i.getVelocity()
		V_avg=V_avg/npart
		for id,part_i in enumerate(part_u):
			if (part_i.x >1) or (part_i.x <0) or (part_i.y >1) or (part_i.y <0) or (part_i.z >1) or (part_i.z <0):
				del(part_u[id - l])
				l += 1
			elif max(part_i.getVelocity())!= 0:
				dW=1/((2*np.pi*dt)**(1/2))*( exp(-(t+dt)**2    /(2*dt))   -   exp(-(t)**2     /(2*dt))  )
				A=(part_i.getVelocity() + (part_i.gamma+part_i.gamma_t-part_i.gamma_old+part_i.gamma_t_old)/(part_i.getPosition()-part_i.getOlderPosition()) ) 
				B=(2*(part_i.gamma + part_i.gamma_t))**(1/2)
				part_i.setPosition( part_i.getPosition()+A * dt + B * dW   )

	  #Criando vetores de X, Y, Z e comp para plotagem
		if True:
			for id,part_i in enumerate(part_u):
				x.append(part_i.x)
				y.append(part_i.y)
				z.append(part_i.z)
				for id,element in enumerate(plot):
					p[id].append(part_i.comp[element])
			#Plotando e salvando imagens
			plot_3D(x,y,z,p,plot)
			plot_comp(z,p,plot)
			plot_PDF(p,plot)

	  #Reação Química
		React()

	  #Calculando a comp média
		Model()

      # Gerando particulas novas
		for id, particle in enumerate(GenPar):
			inputt=[]
			inputt.append(particle[0][0]())
			inputt.append(particle[0][1]())
			inputt.append(particle[0][2]())
			part_u.append(part(inputt,particle[1],particle[2],particle[3]))
	 
	ap.promptPrint("Errors: "+str(erro))
	###############################################################################
	##                          GERAÇÃO DOS GIFS                                 ##
	###############################################################################
		
	ap.promptPrint("Generating GIFs...")
	root.update()
	images=[]
	with imageio.get_writer('OUTPUT/3D.gif', mode='I') as writer:
		for filename in filenames_3D:
			image = imageio.imread(filename)
			writer.append_data(image)
			remove(filename)

	images=[]
	with imageio.get_writer('OUTPUT/compositon.gif', mode='I') as writer:
		for filename in filenames_comp:
			image = imageio.imread(filename)
			writer.append_data(image)
			remove(filename)

	images=[]
	with imageio.get_writer('OUTPUT/PDF.gif', mode='I') as writer:
		for filename in filenames_PDF:
			image = imageio.imread(filename)
			writer.append_data(image)
			remove(filename)

	images=[]
	with imageio.get_writer('OUTPUT/CDF.gif', mode='I') as writer:
		for filename in filenames_CDF:
			image = imageio.imread(filename)
			writer.append_data(image)
			remove(filename)


###############################################################################
##                           MODELOS DE COMBUSTÃO                            ##
###############################################################################

def BurnCantera():
	global part_u
	for id, part_i in enumerate(part_u):
		part_i.R_r=part_i.gas.net_production_rates*1000

def DontBurn():
	global part_u
	for id, part_i in enumerate(part_u):
		part_i.R_r=[0]*len(elementos)

###############################################################################
##                          MODELOS DE MICROMISTURA                          ##
###############################################################################

## Interaction by Exchange with the Mean / Linear Square Mean Estimation 

def Simulate_IEM():
	global part_u,dt,C_omega,erro
	c_avg={}
	for id, element in enumerate(elementos):
		c_avg[element]=0
	npart=len(part_u)
	for id, part_i in enumerate(part_u):
		for element in elementos:
			c_avg[element]+=part_i.comp[element]
				
	for element in elementos:
		c_avg[element] = c_avg[element]/npart

			
	for id,part_i in enumerate(part_u):
		part_i.updateGamma(part_i.gas.viscosity)
		for element in elementos:
			part_i.omega[element] = C_omega*(part_i.gamma+part_i.gamma_t)/(delta**2)
				
	for id, part_i in enumerate(part_u):
		n_e=0
		for element in elementos:
			part_i.comp[element] += ( (-part_i.omega[element] * (part_i.comp[element]-c_avg[element])) + part_i.R_r[n_e] ) * dt
			#part_i.comp[element] += ( (-part_i.omega[element] * (part_i.comp[element]-c_avg[element])) + part_i.R_r) * dt
			if part_i.comp[element]>1:
				part_i.comp[element]=1
				erro+=1
			elif part_i.comp[element]<0:
				part_i.comp[element]=0
				erro+=1
			
			n_e+=1
		part_i.gas.X=part_i.comp

## Extended Interaction by Exchange with the Mean 

def Simulate_EIEM():
	global part_u,dt,C_omega
	c_avg={}
	for id, element in enumerate(elementos):
		c_avg[element]=0
	npart=len(part_u)
	for id, part_i in enumerate(part_u):
		for element in elementos:
			c_avg[element]+=part_i.comp[element]
				
	for element in elementos:
		c_avg[element] = c_avg[element]/npart

			
	for id,part_i in enumerate(part_u):
		part_i.updateGamma(part_i.gas.viscosity)
		for element in elementos:
			part_i.omega[element] = C_omega*(part_i.gamma+part_i.gamma_t)/(delta**2)
				
	for id, part_i in enumerate(part_u):
		for element in range(0,part_i.gas.n_species):
			name=part_i.gas.species_name(element)
			part_i.comp[name] += ( (-part_i.omega[name]* w * (part_i.comp[name]-c_avg[name])) + part_i.R_r[element] ) * dt
			if part_i.comp[name]>1:
				part_i.comp[name]=1
			
## Modelo de Curl

def Simulate_Curl():
	global part_u,dt

	for id,part_i in enumerate(part_u):
		part_i.updateGamma(part_i.gas.viscosity)
	N=len(part_u)*2*dt #Errado
	for i in range(1,int(len(part_u)/20)):
		part_i=part_u[i]
		part_j=part_u[-i]
		for element in range(0,part_i.gas.n_species):
			name=part_i.gas.species_name(element)
			part_i.comp[name]=1/2*(part_i.comp[name]+part_j.comp[name]) + part_i.R_r[element]*dt
			part_j.comp[name]=1/2*(part_i.comp[name]+part_j.comp[name]) + part_j.R_r[element]*dt

## Modelo de Curl Modificado

def Simulate_CurlM():
	global part_u,dt,alpha

	for id,part_i in enumerate(part_u):
		part_i.updateGamma(part_i.gas.viscosity)

	for i in range(1,int(len(part_u)/20)):
		part_i=part_u[i]
		part_j=part_u[-i]
		for element in range(0,part_i.gas.n_species):
			name=part_i.gas.species_name(element)
			part_i.comp[name]=(1-alpha)*part_i.comp[name]+1/2*alpha*(part_i.comp[name]+part_j.comp[name])+part_i.R_r[element]*dt
			part_j.comp[name]=(1-alpha)*part_j.comp[name]+1/2*alpha*(part_i.comp[name]+part_j.comp[name])+part_i.R_r[element]*dt
  
## Modelo de Langevin 

def Simulate_Lange():
	global part_u,dt,d0
	c_avg={}
	for id, element in enumerate(elementos):
		c_avg[element]=0
	for id, part_i in enumerate(part_u):
		for element in elementos:
			c_avg[element]+=part_i.comp[element]
				
	for element in elementos:
		c_avg[element] = c_avg[element]/npart


	for id,part_i in enumerate(part_u):
		part_i.updateGamma(part_i.gas.viscosity)

	var=1 #?
	var_max=1
	w=1

	a=1+d0*((var_max**2-var**2)/var_max**2)
	b=d0*var**2/var_max**2

	dW=1/((2*np.pi*dt)**(1/2))*( exp(-(t+dt)**2    /(2*dt))   -   exp(-(t)**2     /(2*dt))  )

	for id, part_i in enumerate(part_u):
		for element in range(0,part_i.gas.n_species):
			name=part_i.gas.species_name(element)
			part_i.comp[name] += ( -a*w* (part_i.comp[name]-c_avg[name]) + part_i.R_r[element] ) * dt + (2*b*w*part_i.comp[name](1-part_i.comp[name]))**1/2 * dW
			if part_i.comp[name]>1:
				part_i.comp[name]=1

## Modelo de Langevin extendido

def Simulate_LangeEst():
	global part_u,dt
	c_avg={}
	for id, element in enumerate(elementos):
		c_avg[element]=0


	for id,part_i in enumerate(part_u):
		part_i.updateGamma(part_i.gas.viscosity)

###############################################################################
##                     DEFININDO CONSTANTES E PARÂMETROS                     ##
###############################################################################

global div,n_div,d,k,E_a,T_a,E_a,alpha,beta,gamma,PRE_EXP,delta,ap
global used
used=0
	  
div = 100                                   #divisão da variável z associada ao PDF
n_div = 1/div
d = n_div
k = 0                                       #contador

E_a=83600/9.28 #9000 #8.36 #10.45 #8.36
T_a=E_a/8.315 #10054.0
alpha = (2000.-560.)/2000. #0.7273 #6.
beta =(alpha*T_a)/2000. #2.0 #6.287 #17.95 #13. #10.0d0 #17.95
gamma=0.5*beta**2*(1.0+0.5*beta*(3.0*alpha-1.344)) 
PRE_EXP=(gamma*1.2*1.2)/(0.0000751*exp(-beta/alpha))

delta = 0.1                                 #Tamanho do filtro

###############################################################################
##                       ÍNICIO DA INTERFACE GRÁFICA                         ##
###############################################################################

root = Tk(className=" CHARMANDER : beta version")   

root.state('zoomed')
root.iconbitmap('icon.ico')

ap=App(root)
root.mainloop()