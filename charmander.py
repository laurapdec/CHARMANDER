
###############################################################################
##                            IMPORTANDO MODULOS                             ##
###############################################################################

import subprocess 																																												# Abrir o manual externamente
import platform																																													# Determinar sistema operacional
import time 																																													# Cronometra o tempo de simulacao
import numpy as np 																																												# Lida com vetores
from numpy.random import random 																																								# Geracao de numeros aleatorios
from random import randint 																																										# Geracao de inteiros aleatorios
from math import exp 																																											# Funcao exponencial
import matplotlib.pyplot as plt 																																								# Plotagem dos resultados
from mpl_toolkits.mplot3d import Axes3D 																																						# Plotagem 3D dos resultados
import cantera as ct 																																											# Lida com cinética química
from tkinter import * 																																											# Interface Grafica
from tkinter import ttk,filedialog,messagebox 																																					# Interface Grafica
import imageio   																																												# Geracao de GIFS
from os import remove																																											# Deleta arquivos de imagem utilizados para geração do GIF
from PIL import ImageTk,Image  																																									# Lida com imagens para o GIF

###############################################################################
##                         CLASSE INTERFACE GRAFICA                          ##
###############################################################################


class App:
	def __init__(self,master):																																								## Funcao inicial
		self.master=master  																																									# Janela principal

		self.elements=[] 																																										# Elementos quimicos
		self.saved=False 																																										# Variavel booleana para evitar que as condições sejam definidas e nao salvas

		self.style = ttk.Style(master)  																																						# Intentificando o estilo da janela

		self.style.theme_use('classic') 																																						# Definindo o estilo da janela

		#																																													## Menu superior

		menu=Menu(master)   																																									# Criacao de um menu superior na janela
		menu.add_command(label="Import",command=self.import_)																																	# Funcao Import no menu para importar um caso
		menu.add_command(label="Help",command=self.help) 																																		# Funcao de ajuda que redireciona ao manual do CHARMANDER
		subMenu = Menu(menu, tearoff=False)																																						# Criacao de um submenu no menu superior
		menu.add_cascade(label='Theme', menu=subMenu) 																																			# Criacao da cascata no botao "Tema" do menu
		subMenu.add_command(label="White",command=self.whiteTheme)  																															# Sub opcao de tema claro
		subMenu.add_command(label="Dark",command=self.darkTheme) 																																# Sub opcao de tema escuro
		master.config(menu=menu)																																								# Adicionando o menu a janela

		#																																													## Mecanismo de cinetica

		CTIlabel = ttk.Labelframe(master, text='Select the .CTI file')  																														# Subjanela CTIlabel 
		self.CTIvar = StringVar()																																								# String dinamica CTIvar que armazena a informação escrita de qual mecanismo de cinetica sera usado
		CTIcombo = ttk.Combobox(CTIlabel,state="readonly", textvariable=self.CTIvar ,values=["GRI Mech 3.0", "SP21RE","CH4 Global","Kazakov","Local file"]) 									# Menu de escolhas CTIcombo para determinar o arquivo .cti
		CTIcombo.grid(pady=5, padx=10) 																																							# Alocacao da menu CTIcombo na subjanela CTIlabel
		CTIlabel.grid(row=0, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)																														# Alocacao da subjanela CTIlabel na janela principal
		CTIcombo.bind('<<ComboboxSelected>>', self.checkCTI) 																																	# Associa a escolha de uma CTI com a ativacao da funcao checkCTI
	
		#																																													## Modelo de micromistura

		MODELlabel = ttk.Labelframe(master, text='Select the mixing model')																														# Subjanela MODELlabel
		self.MODELvar = StringVar()																																								# String dinamica MODELvar que armazena a informação escrita de qual modelo de micromistura sera usado
		MODELcombo = ttk.Combobox(MODELlabel,state="readonly", textvariable=self.MODELvar ,values=["Curl","Curl Modificado","IEM/LMSE", "EIEM","Langevin","Langevin Estendido"]) 				# Menu de escolhas MODELcombo para determinar o modelo
		self.MODELvar.set("IEM/LMSE") 																																							# Determina o modelo padrao como IEM/LMSE
		MODELcombo.grid(pady=5, padx=10)																																						# Alocacao da menu MODELcombo na subjanela MODELlabel
		MODELlabel.grid(row=1,column=0, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)  																											# Alocacao da subjanela MODELlabel na janela principal
		MODELcombo.bind('<<ComboboxSelected>>', self.checkMODEL)     																															# Associa a escolha de um modelo com a ativacao da funcao checkMODEL

		#																																													## Parametros

		ParamLabel = ttk.Labelframe(master, text='Parameters')																																	# Subjanela ParamLabel
		ParamLabel.grid(row=0,column=1,rowspan=2, sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 																								# Alocacao da subjanela ParamLabel na janela principal	

		Label(master,text="\u03b1:").grid(in_=ParamLabel,row=0, sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 																					# Texto '\alpha' alocado na subjanela ParamLabel
		self.Alphastring=StringVar() 																																							# String dinamica Alphastring que armazena a informacao escrita de qual alpha sera usado
		self.Alphastring.set(0.5) 																																								# Determina alpha padrao de 0.5
		self.entryAlpha=Entry(master,textvariable=self.Alphastring,state='disabled') 																											# Input da variavel alpha
		self.entryAlpha.grid(in_=ParamLabel,row=0, column=1, sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 																						# Alocacao do input na subjanela ParamLabel
		
		Label(master,text="C\u03c9 :").grid(in_=ParamLabel,row=1, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)																					# Texto Cw alocado na subjanela ParamLabel
		self.Cwstring=StringVar() 																																								# String dinamica Cwstring que armazena a informacao escrita de qual Cw sera usado
		self.Cwstring.set(2) 																																									# Determina Cw padrao de 2
		self.entryCw=Entry(master,textvariable=self.Cwstring,state='disabled') 																													# Input da variavel Cw
		self.entryCw.grid(in_=ParamLabel,row=1, column=1, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)  																						# Alocacao do input na subjanela ParamLabel

		Label(master,text="d0 :").grid(in_=ParamLabel,row=2, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)																						# Texto Cw alocado na subjanela ParamLabel
		self.D0string=StringVar() 																																								# String dinamica D0string que armazena a informacao escrita de qual D0 sera usado
		self.D0string.set(0.5) 																																									# Determina D0 padrao de 0.5
		self.entryD0=Entry(master,textvariable=self.D0string,state='disabled') 																													# Input da variavel D0
		self.entryD0.grid(in_=ParamLabel,row=2, column=1, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)  																						# Alocacao do input na subjanela ParamLabel

		self.Param=[self.Alphastring,self.Cwstring,self.D0string] 																																# Vetor com as variaveis definidas na subjanela ParamLabel [alpha,Cw,D0]

		#																																													## Simulation time parameters

		TimeLabel = ttk.Labelframe(master, text='Time settings')																																# Subjanela TimeLabel
		TimeLabel.grid(row=0,column=2,rowspan=2,sticky='W', padx=5, pady=5, ipadx=5, ipady=5)   																								# Alocacao da subjanela TimeLabel na janela principal	
		
		Label(master,text="t_f [s] :").grid(in_=TimeLabel,row=0, sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 																					# Texto 't_f[s]' alocado na subjanela TimeLabel
		self.TFstring=StringVar()																																								# String dinamica TFstring que armazena a informacao de qual tempo final sera usado
		self.TFstring.set(0.01)																																									# Determina t_f padrao de 0.01
		self.entryTF=Entry(master,textvariable=self.TFstring) 																																	# Input da variavel t_f
		self.entryTF.grid(in_=TimeLabel,row=0, column=1, sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 																							# Alocacao do input na subjanela TimeLabel
		
		Label(master,text="dt [s] :").grid(in_=TimeLabel,row=1, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)																					# Texto 'dt [s]' alocado na subjanela TimeLabel
		self.DTstring=StringVar()																																								# String dinamica DTstring que armazena a informacao de qual passo de tempo sera usado
		self.DTstring.set(0.001)																																								# Determina dt padrao de 0.001
		self.entryDT=Entry(master,textvariable=self.DTstring)																																	# Input da variavel dt
		self.entryDT.grid(in_=TimeLabel,row=1, column=1, sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 																							# Alocacao do input na subjanela TimeLabel

		#																																													## Boundary Conditions
		
		Boundlabel = ttk.Labelframe(master, text='Boundary Conditions')																															# Subjanela BoundLabel
		Boundlabel.grid(sticky=E+W,row=2,columnspan=4,rowspan=3,padx=5, pady=5, ipadx=5, ipady=5) 																								# Alocacao da subjanela BoundLabel na janela principal	

		#																																													## Setting Composition

		BigFrame=Frame(Boundlabel) 																																								# Criacao de um quadro 'BigFrame' dentro da subjanela BoundLabel
		BigFrame.grid(column=3,row=0,sticky=W+N,rowspan=30) 																																	# Alocacao do quadro 'BigFrame' na subjanela BoundLabel
		self.canvas = Canvas(self.master, width=200, height=500,bd=0,highlightthickness=0, relief='ridge')																						# Criacao de um canvas dentro da janela principal
		self.CompositionLabel = ttk.Labelframe(self.canvas, text='Compositions') 																												# Subjanela CompositionLabel dentro do canvas
		sbar = Scrollbar(self.master, orient="vertical", command=self.canvas.yview) 																											# Barra de scroll vertical dentro do canvas
		self.canvas.config(yscrollcommand=sbar.set) 																																			# Associa a barra de scroll com o scroll em si
		self.canvas.pack(in_=BigFrame,side="left") 																																				# Alocacao do canvas no quadro BigFrame
		sbar.pack(in_=BigFrame,side="left", fill="y") 																																			# Alocacao da barra de scroll no canvas
		self.canvas.create_window((2,2), window=self.CompositionLabel, anchor="nw",  tags="self.CompositionLabel")																				# Associacao entre a subjanela CompositionLabel e o canvas        
		self.CompositionLabel.bind("<Configure>", self.onFrameConfigure)																														# Torna a subjanela CompositionLabel reativa pela funcao onFrameConfigure
				
		#																																													## Select Wall

		Label(master,text="Select the wall :").grid(in_=Boundlabel,row=0,column=0 ,sticky='W', padx=5, pady=5, ipadx=5, ipady=5)																# Texto 'Select the wall :' na subjanela Boundlabel
		self.Boundvar = StringVar()																																								# String dinamica que armazena a informacao de qual superficie de contorno esta sendo definida	
		self.Boundvar.set("LEFT")																																								# Determina Boundvar padrao 'LEFT'
		Boundcombo = ttk.Combobox(Boundlabel,state="readonly", textvariable=self.Boundvar ,values=["LEFT", "RIGHT", "FRONT", "BACK", "UP", "DOWN","fill","Half 1","Half 2"])					# Menu de escolhas BoundCombo para determinar a superficie de contorno
		Boundcombo.grid(row=0,column=1,pady=5, padx=10)																																			# Alocacao da subjanela Boundcombo na janela principal
		Boundcombo.bind('<<ComboboxSelected>>', self.newWall)																																	# Associa a escolha de uma superficie de contorno com a funcao newWall

		#																																													## Image of wall

		self.ImgPath = StringVar()																																								# String dinamica que armazena o caminho para a imagem ilustrativa da superficie de contorno
		self.ImgPath.set( "wall/LEFT.png")																																						# Determina ImgPath padrao como 'wall/LEFT.png'
		self.WallImg = ImageTk.PhotoImage(Image.open(self.ImgPath.get()))																														# Gera a imagem ilustrativa 
		self.Imglabel = Label(image=self.WallImg)																																				# Criacao de um ambiente Imglabel com a imagem
		self.Imglabel.img = self.WallImg  																																						# Finalizacao da definicao o ambiente
		self.Imglabel.grid(in_=Boundlabel,row=0,column=2) 																																		# Alocacao do Imglabel na sub janela Boundlabel

		#																																													## Create particles here?
		
		self.createPart = IntVar()																																								# Inteiro dinamico que armazena informacao booleana sobre a criacao de particulas na superficie em questao
		self.checkIn=Checkbutton(master, text="Generate particles in this Surface?",variable=self.createPart,command=self.checkenable) 															# Botao de check com o texto 'Generate particles in this Surface?'
		self.checkIn.grid(in_=Boundlabel,sticky=W,row=1,columnspan=3)																															# Alocacao do botao na sub janela Boundlabel

		#																																													## Create particles here later?
		
		self.createPartT = IntVar()																																								# Inteiro dinamico que armazena informacao booleana sobre a criacao de particulas com o decorrer do tempo na superficie em questao
		self.checkInT=Checkbutton(master, text="Generate particles in this Surface every time step?",variable=self.createPartT,state='disabled') 												# Botao de check com o texto 'Generate particles in this Surface every time step?'
		self.checkInT.grid(in_=Boundlabel,sticky=W,row=2,columnspan=3)																															# Alocacao do botao na sub janela Boundlabel

		#																																													## Setting Number of Particles
		
		Label(master,text="Number of particles generated by time step :").grid(in_=Boundlabel,row=3 ,columnspan=2,sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 								# Texto 'Number of particles generated by time step :' alocado na sub janela Boundlabel
		self.Nstring=StringVar() 																																								# String dinamica que armazena o numero de particulas a serem geradas por passo de tempo
		self.entryN=Entry(master,textvariable=self.Nstring,state='disabled')																													# Input do numero de particulas
		self.Nstring.set(0) 																																									# Determina Nstring padrao como 0
		self.entryN.grid(in_=Boundlabel,row=3, column=2, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)																							# Alocacao do input na sub janela Boundlabel
		
		#																																													## Setting Temperature
		
		Label(master,text="T [K] :").grid(in_=Boundlabel,row=4 ,columnspan=2,sticky='W', padx=5, pady=5, ipadx=5, ipady=5)  																	# Texto 'T [K]:' alocado na sub janela Boundlabel
		self.Tstring=StringVar()																																								# String dinamica que armazena a informacao da temperatura
		self.entryT=Entry(master,textvariable=self.Tstring,state='disabled') 																													# Input da temperatura
		self.entryT.grid(in_=Boundlabel,row=4, column=2, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)																							# Alocacao do input na sub janela Boundlabel

		#																																													## Setting Velocities

		VelocityLabel = ttk.Labelframe(Boundlabel, text='Velocities')																															# Subjanela VelocityLabel
		VelocityLabel.grid(sticky=E+W,row=5,padx=5, pady=5, ipadx=5, ipady=5,columnspan=3)																										# Alocacao da sub janela VelocityLabel na janela principal
		
		Label(master,text="u [m/s] :").grid(in_=VelocityLabel,row=3, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)																				# Texto 'u [m/s]' alocado na sub janela VelocityLabel
		self.Ustring=StringVar()																																								# String dinamica que armazena a velocidade no eixo x
		self.Ustring.set(0)																																										# Determina Ustring padrao como 0
		self.entryU=Entry(master,textvariable=self.Ustring,state='disabled')																													# Input da velocidade no eixo x
		self.entryU.grid(in_=VelocityLabel,row=3, column=1, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)																						# Alocacao do input na sub janela VelocityLabel
		
		Label(master,text="v [m/s] :").grid(in_=VelocityLabel,row=4, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)																				# Texto 'v [m/s]' alocado na sub janela VelocityLabel
		self.Vstring=StringVar()																																								# String dinamica que armazena a velocidade no eixo y
		self.Vstring.set(0)																																										# Determina Vstring padrao como 0
		self.entryV=Entry(master,textvariable=self.Vstring,state='disabled')																													# Input da velocidade no eixo y
		self.entryV.grid(in_=VelocityLabel,row=4, column=1, sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 																						# Alocacao do input na sub janela VelocityLabel

		Label(master,text="w [m/s] :").grid(in_=VelocityLabel,row=5, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)																				# Texto 'w [m/s]' alocado na sub janela VelocityLabel
		self.Wstring=StringVar()																																								# String dinamica que armazena a velocidade no eixo z
		self.Wstring.set(0)																																										# Determina Wstring padrao como 0
		self.entryW=Entry(master,textvariable=self.Wstring,state='disabled')																													# Input da velocidade no eixo z
		self.entryW.grid(in_=VelocityLabel,row=5, column=1, sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 																						# Alocacao do input na sub janela VelocityLabel

		#																																													## Wall Reflect or Pass
		
		self.WallReflect = IntVar() 																																							# Inteiro dinamico que armazena informacao booleana sobre se a parede deve ter fluxo=0 na superficie em questao
		Checkbutton(master, text="Reflects?", variable=self.WallReflect).grid(in_=Boundlabel,row=6, sticky=W,columnspan=3)																		# Botao de check com o texto 'Reflects?' alocado na sub janela Boundlabel

		#																																													## Save Wall
		
		self.save=Button(Boundlabel,text="Save Surface",command=self.saveWall)																													# Botao com o texto 'Save Surface'
		self.save.grid(row=7, columnspan=2, sticky='W', padx=5, pady=5, ipadx=5, ipady=5)																										# Alocacao do botao na janela principal
	
		#																																													## Plot Configure

		#																																														# to be done

		#																																													## Run

		self.run=Button(master,text="Run",command=self.running)																																	# Botao com o texto 'Run'
		self.run.grid(row=1, column=5 , sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 																											# Alocacao do botao na janela principal

		#																																													## Prompt
		
		self.fontsize=11																																										# Determina o tamanho da fonte no LOG Console
		PromptFrame=Frame(master)																																								# Criacao de um quadro na janela principal
		PromptFrame.grid(row=2,column=4,sticky='W', padx=5, pady=5)																																# Alocacao do quadro na janela principal
		Label( PromptFrame,text='LOG Console',bg='white',font=('freemono', 11, 'italic'),bd=1,highlightthickness=2, relief='ridge').grid(row=0,columnspan=2,sticky="ew") 						# Texto 'LOG Console' alocado na janela principal
		bar_prompt = Scrollbar(PromptFrame, orient="vertical")																																	# Barra de scroll vertical dentro do canvas
		self.prompt=Canvas(PromptFrame,width=500, height=500,bg='black',bd=0,highlightthickness=2, relief='ridge',yscrollcommand=bar_prompt.set) 												# Criacao de um canvas no quadro PromptFrame
		bar_prompt.config(command=self.prompt.yview)																																			# Associa a barra de scroll com o scroll em si
		self.prompt.config(scrollregion=self.prompt.bbox('all'))																																# Torna o canvas responsivo
		bar_prompt.grid(row=1,column=1,sticky="ns")																																				# Alocacao da barra de scroll no canvas
		self.prompt.grid(row=1,column=0)																																						# Alocacao do canvas na sub janela PromptFrame

		#																																													## Plot parameters

		PlotFrame=Frame(self.master,bg='')																																						# Criacao de um quadro na janela principal
		PlotFrame.grid(row=0,column=4,rowspan=2,sticky='W', padx=5, pady=5, ipadx=5, ipady=5)																									# Alocacao do quadro na janela principal
		self.plotcanvas = Canvas(self.master, width=300, height=125,bd=0,highlightthickness=0, relief='ridge')																					# Criacao de um canvas na janela principal
		self.PlotLabel = ttk.Labelframe(self.plotcanvas, text='Plot settings')																													# Sub janela Labelframe no canvas
		plot_bar = Scrollbar(self.master, orient="horizontal", command=self.plotcanvas.xview)																									# Barra de scroll horizontal dentro do canvas
		self.plotcanvas.config(xscrollcommand=plot_bar.set)																																		# Associa a barra de scroll com o scroll em si
		self.plotcanvas.pack(in_=PlotFrame,side="top")																																			# Alocacao do canvas no quadro PlotFrame 
		plot_bar.pack(in_=PlotFrame,side="top", fill="x")																																		# Alocacao da barra de scroll no quadro PlotFrame
		self.plotcanvas.create_window((2,2), window=self.PlotLabel, anchor="nw",  tags="self.PlotLabel")        																				# Associacao entre o quadro PlotLabel e o canvas  
		self.PlotLabel.bind("<Configure>", self.onFrameConfigurePlot)																															# Torna o quadro PlotLabel reativa pela funcao onFrameConfigurePlot

		#																																													## Default White Theme
		self.whiteTheme()																																										# Define o tema claro como padrao

	def promptPrint(self,message,cont=False):																																				## Funcao para imprimir informacoes no LOG Console
		global used 																																											# Contador da quantidade de linhas usadas no LOG Console
		start=10																																												# Espacamento inicial
		height=(self.fontsize+10) * used + 10 																																					# Altura na qual o texto deve ser colocado  (tamanho da fonte + 10 ) x numero de linhas usadas + 10 
		if cont:																																												# Booleano para continuar textos que precisam de mais de uma linha
			start+=30												
			height-=5

		a=self.prompt.create_text((start,height),anchor="w",text=message,fill='green',font=('freemono', self.fontsize))																			# Adiciona-se o texto ao canvas
		used+=1																																													# Mais uma linha usada no LOG Console

		x1,y1,x2,y2=self.prompt.bbox(a) 																																						# Calcula as coordenadas do LOG Console com o texto inteiro
		if (x2-x1) >480: 																																										# Se a largura dele for maior que 480
			n=int(480*len(message)/(x2-x1))																																						# Calcula até qual caractere deve ser mostrado na primeira linha
			self.prompt.itemconfigure(a,text=message[:n])																																		# Altera o texto para mostrar até o caractere n
			self.promptPrint(message[n:],True)																																					# Cria um novo texto com o resto do texto e a variavel booleana cont=True

		bound=[self.prompt.bbox('all')[0],self.prompt.bbox('all')[1],self.prompt.bbox('all')[2],self.prompt.bbox('all')[3]+200]																	# Calcula as coordenadas do LOG Console com o texto
		self.prompt.config(scrollregion=bound)																																					# Atualiza as dimensoes do canvas com as coordenadas do LOG Console com o texto inteiro

	def whiteTheme(self):																																									## Funcao para alterar para o tema claro
		self.color="white" 																																										# Altera a cor do fundo para branco
		self.textcolor="black" 																																									# Altera a cor do texto para preto
		self.updateTheme() 																																										# Atualiza o tema

	def darkTheme(self):																																									## Funcao para alterar para o tema claro
		self.color="#5b5b5b"																																									# Altera a cor do fundo para cinza
		self.textcolor='white'																																									# Altera a cor do texto para branco
		self.updateTheme()																																										# Atualiza o tema

	def updateTheme(self):																																									## Funcao para atualizar o tema
		self.master.configure(bg=self.color)																																					# Atualiza a cor de fundo da janela principal
		self.style.configure('TFrame',bg=self.color)																																			# Atualiza a cor de fundo da sub janela TFrame
		self.style.configure('TLabelframe', background=self.color)																																# Atualiza a cor de fundo da sub janela TLabelframe
		self.style.configure('TLabelframe.Label', background=self.color,foreground=self.textcolor)																								# Atualiza a cor de fundo e de texto da TLabelframe.Label
		self.style.configure('TLabel', background=self.color,foreground=self.textcolor)																											# Atualiza a cor de fundo e de texto da TLabel
		for wid in self.master.winfo_children()+self.CompositionLabel.winfo_children()+self.PlotLabel.winfo_children(): 																		# Para todos os conteudos das sub janelas CompositionLabel e PlotLabel
			if type(wid)==Label  :																																								# Se for do tipo label
				wid.configure(bg=self.color,foreground=self.textcolor) 																															# Atualiza a cor de fundo e de texto
			elif type(wid)==Canvas or type(wid)==Checkbutton:																																	# Se for do tipo canvas ou checkbutton
				wid.configure(bg=self.color)																																					# Atualiza a cor de fundo

	def newWall(self,event=None): 																																							## Funcao para resetar os parametros das superficies de contorno
		if not self.saved :																																										# Se a superficie anteior nao foi salva aind
			if messagebox.askokcancel("Warning", "Wish to save unsaved surface?"):																												# Caixa de aviso com o texto '"Warning, Wish to save unsaved surface?'
				self.saveWall()																																									# Se confirmado a superficie anterior é salva

		self.saved=False																																										# Define que a nova superficie ainda nao foi salva
		stri="wall/"+self.Boundvar.get()+".png"																																					# Caminho para a imagem ilustrativa da nova superficie
		self.ImgPath.set(stri)																																									# Atualiza o caminho
		photo=ImageTk.PhotoImage(Image.open(self.ImgPath.get())) 																																# Atualiza a imagem 1
		self.Imglabel.configure(image= photo) 																																					# Atualiza a imagem 2
		self.Imglabel.image=photo 																																								# Atualiza a imagem 3

		self.createPart.set(0) 																																									# createPart é definido como o valor padrao 0
		self.createPartT.set(0) 																																								# createPartT é definido como o valor padrao 0
		self.checkenable() 																																										# desabilita-se todos os checks pela funcao checkenable
		self.Nstring.set(0) 																																									# Nstring é definido como o valor padrao 0
		self.Ustring.set(0) 																																									# Ustring é definido como o valor padrao 0
		self.Vstring.set(0) 																																									# Vstring é definido como o valor padrao 0
		self.Wstring.set(0) 																																									# Wstring é definido como o valor padrao 0
		self.WallReflect.set(0) 																																								# WallReflect é definido como o valor padrao 0
		for id, field in enumerate(self.elements):																																				# Para todos os elementos
			self.stringComposition[id].set(0) 																																					# a composição é definida como o valor padrao 0

	def saveWall(self): 																																									## Funcao para salvar a superficie de contorno
		if self.createPart.get()==1:																																							# Se nessa superficie for ser geradas particulas
			stringComposition_temp=[]																																							# Vetor temporario das composicoes

			for id,comp in enumerate(self.stringComposition):																																	# Para todas composi~coes
				stringComposition_temp.append(comp.get())																																		# Adiciona-las no vetor temporario

			if self.Boundvar.get() == "LEFT":																																					# Se a superficie for 'LEFT'
				strin=1																																											# Posicao dessa superficie no vetor a ser gerada 
				self.promptPrint("Wall "+self.Boundvar.get() +" saved!")																														# Imprimir no LOG Console que a superficie foi salva
			elif self.Boundvar.get() == "RIGHT":																																				# Se a superficie for 'LEFT'
				strin=2																																											# Posicao dessa superficie no vetor a ser gerada
				self.promptPrint("Wall "+self.Boundvar.get() +" saved!")																														# Imprimir no LOG Console que a superficie foi salva
			elif self.Boundvar.get() == "FRONT":																																				# Se a superficie for 'LEFT'
				strin=3																																											# Posicao dessa superficie no vetor a ser gerada
				self.promptPrint("Wall "+self.Boundvar.get() +" saved!")																														# Imprimir no LOG Console que a superficie foi salva
			elif self.Boundvar.get() == "BACK":																																					# Se a superficie for 'LEFT'
				strin=4																																											# Posicao dessa superficie no vetor a ser gerada
				self.promptPrint("Wall "+self.Boundvar.get() +" saved!")																														# Imprimir no LOG Console que a superficie foi salva
			elif self.Boundvar.get() == "UP":																																					# Se a superficie for 'LEFT'
				strin=5																																											# Posicao dessa superficie no vetor a ser gerada
				self.promptPrint("Wall "+self.Boundvar.get() +" saved!")																														# Imprimir no LOG Console que a superficie foi salva
			elif self.Boundvar.get() == "DOWN":																																					# Se a superficie for 'LEFT'
				strin=6																																											# Posicao dessa superficie no vetor a ser gerada
				self.promptPrint("Wall "+self.Boundvar.get() +" saved!")																														# Imprimir no LOG Console que a superficie foi salva
			elif self.Boundvar.get() == "fill":																																					# Se a superficie for 'LEFT'
				strin=7																																											# Posicao dessa superficie no vetor a ser gerada
				self.promptPrint(self.Boundvar.get() +" saved!")																																# Imprimir no LOG Console que a superficie foi salva
			elif self.Boundvar.get() == "Half 1":																																				# Se a superficie for 'LEFT'
				strin=8																																											# Posicao dessa superficie no vetor a ser gerada
				self.promptPrint(self.Boundvar.get() +" saved!")																																# Imprimir no LOG Console que a superficie foi salva
			elif self.Boundvar.get() == "Half 2":																																				# Se a superficie for 'LEFT'
				strin=9																																											# Posicao dessa superficie no vetor a ser gerada
				self.promptPrint(self.Boundvar.get() +" saved!")																																# Imprimir no LOG Console que a superficie foi salva
			self.Wall[strin-1]['GenDt']=self.createPartT.get()																																	# No vetor referente a superficie em questao, salvar um dicionario com a variavel createPartT atual
			self.Wall[strin-1]['Nstring']=self.Nstring.get()																																	# No vetor referente a superficie em questao, salvar um dicionario com a variavel Nstring atual
			self.Wall[strin-1]['Tstring']=self.Tstring.get()																																	# No vetor referente a superficie em questao, salvar um dicionario com a variavel Tstring atual
			self.Wall[strin-1]['Ustring']=self.Ustring.get()																																	# No vetor referente a superficie em questao, salvar um dicionario com a variavel Ustring atual
			self.Wall[strin-1]['Vstring']=self.Vstring.get()																																	# No vetor referente a superficie em questao, salvar um dicionario com a variavel Vstring atual
			self.Wall[strin-1]['Wstring']=self.Wstring.get()																																	# No vetor referente a superficie em questao, salvar um dicionario com a variavel Wstring atual
			self.Wall[strin-1]['WallReflect']=self.WallReflect.get()																															# No vetor referente a superficie em questao, salvar um dicionario com a variavel WallReflect atual
			self.Wall[strin-1]['stringComposition']=stringComposition_temp																														# No vetor referente a superficie em questao, salvar um dicionario com o vetor temporario de composicoes

		self.save.config(bg='green')																																							# Define o botão 'Save Surface' com a cor verde
		self.saved=True 																																										# Define que a parede atual foi salva
					
	def checkCTI(self,event=None):																																							## Funcao para atualizar a interface com base no mecanismo de cinetica quimica
		for id, field in enumerate(self.elements):																																				# Para todos elementos
			self.entryComposition[id].grid_forget()																																				# Reset inputs		
			self.labelComposition[id].grid_forget()																																				# Reset textos inputs
			self.checkComposition[id].grid_forget()																																				# Reset checks
			self.labelComposition[id].grid_forget() 																																			# Reset texto checks

		if platform.system()=='Linux':																																							# Se for Linux 	
			if (self.CTIvar.get()=="SP21RE"):																																					# Se o modelo de cinetica quimica for SP21RE
				self.CTIfile="CTI Files/sp21re.cti"																																				# Caminho para o arquivo .cti
				self.solution_input=[self.CTIfile,None]																																			# Combinação do arquivo .cti e nome da fase

			elif (self.CTIvar.get()=="GRI Mech 3.0"):																																			# Se o modelo de cinetica quimica for GRI Mech 3.0
				self.CTIfile="CTI Files/GRI30.cti"																																				# Caminho para o arquivo .cti
				self.solution_input=[self.CTIfile,"gri30_mix"]																																	# Combinação do arquivo .cti e nome da fase

			elif (self.CTIvar.get()=="CH4 Global"):																																				# Se o modelo de cinetica quimica for CH4 Global
				self.CTIfile="CTI Files/methane_global.cti"																																		# Caminho para o arquivo .cti
				self.solution_input=[self.CTIfile,"ch4mec_mix"]																																	# Combinação do arquivo .cti e nome da fase
			
			elif (self.CTIvar.get()=="Kazakov"):																																				# Se o modelo de cinetica quimica for Kazakov
				self.CTIfile="CTI Files/methane-kazakov21.cti"																																	# Caminho para o arquivo .cti
				self.solution_input=[self.CTIfile,None]																																			# Combinação do arquivo .cti e nome da fase
			
			elif (self.CTIvar.get()=="Local file"):																																				# Se o modelo de cinetica quimica for local
				self.CTIfile = filedialog.askopenfilename(title='Select file',filetypes = (("CTI files","*.cti"),("all files","*.*")))															# Caminho para o arquivo .cti
				self.solution_input=[self.CTIfile,None]																																			# Combinação do arquivo .cti e nome da fase

		elif platform.system()=='Windows':																																						# Se for Windows... mesma coisa, só inverte a barra

			if (self.CTIvar.get()=="SP21RE"):
				self.CTIfile="CTI Files\\sp21re.cti"
				self.solution_input=[self.CTIfile,None]

			elif (self.CTIvar.get()=="GRI Mech 3.0"):
				self.CTIfile="CTI Files\\GRI30.cti"
				self.solution_input=[self.CTIfile,"gri30_mix"]
			
			elif (self.CTIvar.get()=="CH4 Global"):
				self.CTIfile="CTI Files\\methane_global.cti"
				self.solution_input=[self.CTIfile,"ch4mec_mix"]
			
			elif (self.CTIvar.get()=="Kazakov"):
				self.CTIfile="CTI Files\\methane-kazakov21.cti"
				self.solution_input=[self.CTIfile,None]
			
			elif (self.CTIvar.get()=="Local file"):
				self.CTIfile = filedialog.askopenfilename(title='Select file',filetypes = (("CTI files","*.cti"),("all files","*.*")))
				self.solution_input=[self.CTIfile,None]

		self.elements=ct.Solution(self.solution_input[0],self.solution_input[1]).species_names																									# Define o vetor de elementos com base nas especies quimicas do arquivo .cti
		self.promptPrint(self.CTIfile+ " was just imported")																																	# Imprimi no LOG Console que o arquivo .cti foi importado

		global elementos
		elementos=self.elements 																																								# Define um vetor elementos igual ao outro

		self.checkComposition=[0]*len(self.elements) 																																			# Define que o vetor de composicao a serem plotados tem dimensao igual ao numero de elementos
		self.PlotConfiguration=[0]*len(self.elements) 																																			# Define que o vetor de composicao a serem plotados tem dimensao igual ao numero de elementos
		self.stringComposition=[0]*len(self.elements) 																																			# Define que o vetor com os nomes das especies quimicas tem dimensao igual ao numero de elementos
		self.labelComposition=[0]*len(self.elements) 																																			# Define que o vetor com os nomes das especies quimicas tem dimensao igual ao numero de elementos
		self.entryComposition=[0]*len(self.elements) 																																			# Define que o vetor de composicao inicial tem dimensao igual ao numero de elementos

		for id, field in enumerate(self.elements): 																																				# Para todos elementos
			frammim=Frame(self.PlotLabel,bg='') 																																				# Criacao de um quadro dentro da sub janela PlotLabel
			frammim.grid(row=id%4 ,column=id//4) 																																				# Alocacao do quadro dentro da sub janela PlotLabel
			self.PlotConfiguration[id]=StringVar()																																				# String dinamica com o nome da especie
			self.PlotConfiguration[id].set(0) 																																					# Inteiro dinamico que carrega informacao booleana se a especie sera plotada ou nao
			self.checkComposition[id]=Checkbutton(self.PlotLabel,variable=self.PlotConfiguration[id])																							# Botao do tipo check
			self.checkComposition[id].grid(in_=frammim,row=0,column=0,sticky='EN')  																											# Alocacao do botao no quadro
			self.labelComposition[id]=Label(self.PlotLabel,text=field) 																															# Texto com o nome da especie quimica
			self.labelComposition[id].grid(in_=frammim,row=0,column=1,sticky='WN')  																											# Alocacao do texto no quadro
		
		for id, field in enumerate(self.elements):																																				# Para todos elementos
			self.labelComposition[id]=Label(self.CompositionLabel,text=field) 																													# Texto com o nome da especie quimica
			self.labelComposition[id].grid(row=id ,sticky='W', padx=5, pady=5, ipadx=5, ipady=5)  																								# Alocacao do texto na sub janela CompositionLabel
			self.stringComposition[id]=StringVar() 																																				# String dinamica com o valor da composicao
			self.stringComposition[id].set(0)																																					# Define a composicao padrao como 0
			self.entryComposition[id]=Entry(self.CompositionLabel,textvariable=self.stringComposition[id],state='disabled') 																	# Input da composicao 
			self.entryComposition[id].grid(row=id, column=1, sticky='W', padx=5, pady=5, ipadx=5, ipady=5) 																						# Alocacao no input na sub janela CompositionLabel
		self.checkenable() 																																										# Desmarca todos checks

		self.Wall=[]																																											# Cria o vetor Wall vazio
		for i in range(0,9):				
			self.Wall.append({'GenDt':0,'Nstring':'0','Tstring':'0','Ustring':'0','Vstring':'0','Wstring':'0','stringComposition':[0.0]*len(self.elements),'WallReflect':0})					# Adiciona 6 dicionarios com as informacoes das superficies de contorno nulas
		self.save.config(bg='red')																																								# Configura o botao 'Save Surface' com a cor vermelha
		self.updateTheme()																																										# Atualiza o tema

	def onFrameConfigure(self, event):																																						## Funcao para canvas responsivo
		self.canvas.configure(scrollregion=self.canvas.bbox("all"))

	def onFrameConfigurePlot(self, event):																																					## Funcao para canvas responsivo
		self.plotcanvas.configure(scrollregion=self.plotcanvas.bbox("all"))

	def checkenable(self): 																																									## Funcao para tirar todos checks
		if (self.createPart.get()==0):																																							# Se na superficie não sao geradas particulas
			self.checkInT.configure(state='disabled')																																			# Desabilita checkInT
			self.entryT.configure(state='disabled')																																				# Desabilita entryT
			self.entryN.configure(state='disabled')																																				# Desabilita entryN
			self.entryU.configure(state='disabled')																																				# Desabilita entryU
			self.entryV.configure(state='disabled')																																				# Desabilita entryV
			self.entryW.configure(state='disabled')																																				# Desabilita entryW
			for id, field in enumerate(self.elements):
				self.entryComposition[id].configure(state='disabled')																															# Desabilita todos checks de especies quimicas
				
		else:
			self.checkInT.configure(state='normal')																																				# Zera checkInI
			self.entryT.configure(state='normal')																																				# Zera entryT
			self.entryN.configure(state='normal')																																				# Zera entryN
			self.entryU.configure(state='normal')																																				# Zera entryU
			self.entryV.configure(state='normal')																																				# Zera entryV
			self.entryW.configure(state='normal')																																				# Zera entryW
			for id, field in enumerate(self.elements):
				self.entryComposition[id].configure(state='normal')																																# Zera todos checks de especies quimicas

	def saveInput(self):																																									## Funcao para salvar as condicoes em arquivo externo
		self.promptPrint("The conditions set are available in the file setup.txt in the folder OUTPUT") 																						# Imprime no LOG Console que as condicoes foram exportadas

		if platform.system()=='Linux':																																							# Se for Linux
			setup=open("OUTPUT/setup.char",'w')																																					# Abre arquivo setup.char
		elif platform.system()=='Windows':																																						# Se for Windows... mesma coisa só inverte a barra
			setup=open("OUTPUT\\setup.char",'w')
		setup.write(self.CTIfile + "\n")																																						# Escreve no arquivo o arquivo CTI
		setup.write(self.MODELvar.get()+ "\n")																																					# Escreve no arquivo o modelo de micromistura
		setup.write(self.Param[0].get()+" "+self.Param[1].get()+" "+self.Param[2].get()+ "\n")																									# Escreve no arquivo os parametros do modelo de micromistura
		setup.write(self.DTstring.get()+" "+self.TFstring.get()+ "\n")																															# Escreve no arquivo os parametros de tempo

		for i in range(0,9):																																									# Para todas superficies de contorno
			name="\n \n Wall " +str(i+1)+ " \n \n "																																				
			setup.write(name)																																									# Escreve no arquivo a superficie em questao
			setup.write("\n GenDt:"+str(self.Wall[i]['GenDt']))																																	# Escreve no arquivo se e para gera particulas com o tempo
			setup.write("\n N:"+self.Wall[i]['Nstring'])																																		# Escreve no arquivo o numero de particulas
			setup.write("\n T:"+self.Wall[i]['Tstring'])																																		# Escreve no arquivo a temperatura
			setup.write("\n U:"+self.Wall[i]['Ustring'])																																		# Escreve no arquivo a velocidade no eixo x
			setup.write("\n V:"+self.Wall[i]['Vstring'])																																		# Escreve no arquivo a velocidade no eixo y
			setup.write("\n W:"+self.Wall[i]['Wstring'])																																		# Escreve no arquivo a velocidade no eixo z
			setup.write("\n Wall Reflect:"+str(self.Wall[i]['WallReflect']))																													# Escreve no arquivo se a superficie de contorno reflete particulas
			setup.write("\n Composition: \n")																																					# Escreve no arquivo a composicao
			for id, element in enumerate(self.elements):																																		
				setup.write(element+":"+str(self.Wall[i]['stringComposition'][id]) + '\n')																													

		setup.close()																																											# Fecha o arquivo

	def run(self):																																											## Funcao para rodar a simulacao evitando erro
		try:
			self.running()																																										# Tenta rodar pela funcao running
		except:
			self.promptPrint("Insuficient data")																																				# Caso nao consiga ha falta de dados
			print(sys.exc_info()[0])
			self.run.config(state='normal')

	def running(self):																																										## Funcao para rodar a simulacao
		self.run.config(state='disabled')																																						# Confere se o usuario realmente deseja comecar a simulacao sem salvar a ultima superficie de controle
		if not self.saved :
			if messagebox.askokcancel("Warning", "Wish to save unsaved wall?"):
				self.saveWall()
			else:
				self.run.config(state='normal')
				return None

		self.Param=[self.Alphastring,self.Cwstring,self.D0string]																																# Vetor de parametros de modelo de micromistura
		self.saveInput()																																										# Condicoes de contorno salvo em arquivo externo

		if self.MODELvar.get()=="Curl":																																							# Verifica o modelo de micromistura e associa a funcao com ele
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

		if self.Burnvar.get()=="Cantera":																																						# Verifica o modelo de combustao e associa a funcao com ele
			React=BurnCantera
		elif self.Burnvar.get()=="Don't burn":
			React=DontBurn

		PlotConfigurationsent=[]																																								# Cria vetor vazio
		for i in range(0,len(self.PlotConfiguration)):
			PlotConfigurationsent.append(self.PlotConfiguration[i].get())																														# Adiciona-se as configuracoes de plotagem

		start=time.process_time()																																								# Inicia o cronometro para saber a duracao da simulacao posteriormente

		Simulate(self.Wall,self.Param,self.DTstring,self.TFstring,Model,React,PlotConfigurationsent)																							# Chama a funcao Simulate que tem todo o código de simulacao
		end=time.process_time()																																									# Termina o cronometro

		self.promptPrint('Process Time:'+str(int((end-start)/60))+ ' minutes and '+str(int((end-start)%60))+ ' seconds') 																		# Imprime no LOG Console o tempo da simulacao

		self.stop_loading()																																										# Chama a funcao stop_loading que faz o programa apresentar um gif ao final da simulacao

		self.run.config(state='normal')																																							# Habilita o botao Run novamente

	def stop_loading(self): 																																								## Funcao para apresentar o gif ao final da simulacao
		if platform.system()=='Linux':																																							# Se for Linux
			imagelist=["done/0.png","done/1.png","done/2.png","done/3.png","done/4.png","done/5.png","done/6.png","done/7.png","done/8.png"]  													# Caminho das imagens
		elif platform.system()=='Windows':																																						# Se for Windows ...  mesma coisa apenas inverte as barras
			imagelist=["done\\0.png","done\\1.png","done\\2.png","done\\3.png","done\\4.png","done\\5.png","done\\6.png","done\\7.png","done\\8.png"]    
		
		self.giflist = []																																										# Criacao do vetor das imagens vazio
		for imagefile in imagelist:																																								# Adiciona-se as imagens
			photo = PhotoImage(file=imagefile)
			self.giflist.append(photo)
		for gif in self.giflist:																																								# Apresentacao do gif
			try:
				self.prompt.delete(last)
			except:
				print()
			last=self.prompt.create_image(250, 500-gif.height()//2,	 image=gif)
			self.prompt.update()
			self.master.update()
			time.sleep(0.1) 
		time.sleep(1)
		self.promptPrint("Finished.")																																							# Imprime no LOG Console 'Finished.'
		self.promptPrint("=======================================")
		self.prompt.delete(last)

	def import_(self):																																										## Funcao para importar condicoes de contorno
		filename = filedialog.askopenfilename(initialdir = "/OUTPUT",title='Select file',filetypes = (("CHARMANDER files","*.char"),("all files","*.*")))										# Abre janela para selecionar arquivo
		doc=open(filename,'r') 																																									# Abre arquivo
		self.promptPrint("The conditions set in the file " + doc.name+ " are now being used") 																									# Imprimir no LOG Console que as condicoes de contorno foram importadas

		self.CTIfile=doc.readline().strip('\n')
		if platform.system()=='Linux':		

			if (self.CTIfile=="CTI Files/sp21re.cti"):
				self.CTIvar.set("SP21RE")
				self.solution_input=[self.CTIfile,None]

			elif (self.CTIfile=="CTI Files/GRI30.cti"):
				self.CTIvar.set("GRI Mech 3.0")
				self.solution_input=[self.CTIfile,"gri30_mix"]

			elif (self.CTIfile=="CTI Files/methane_global.cti"):
				self.CTIvar.set("CH4 Global")
				self.solution_input=[self.CTIfile,"ch4mec_mix"]

			elif (self.CTIfile=="CTI Files/methane-kazakov21.cti"):
				self.CTIvar.set("Kazakov")
				self.solution_input=[self.CTIfile,None]

		elif platform.system()=='Windows':

			if (self.CTIfile=="CTI Files\\sp21re.cti"):
				self.CTIvar.set("SP21RE")
				self.solution_input=[self.CTIfile,None]

			elif (self.CTIfile=="CTI Files\\GRI30.cti"):
				self.CTIvar.set("GRI Mech 3.0")
				self.solution_input=[self.CTIfile,"gri30_mix"]

			elif (self.CTIfile=="CTI Files\\methane_global.cti"):
				self.CTIvar.set("CH4 Global")
				self.solution_input=[self.CTIfile,"ch4mec_mix"]

			elif (self.CTIfile=="CTI Files\\methane-kazakov21.cti"):
				self.CTIvar.set("Kazakov")
				self.solution_input=[self.CTIfile,None]
		self.checkCTI()



		self.MODELvar.set(doc.readline().strip('\n'))


		Param=doc.readline().strip('\n').split(' ')
		self.Param[0].set(Param[0])
		self.Param[1].set(Param[1])
		self.Param[2].set(Param[2])



		TimeParam=doc.readline().strip('\n').split(' ')
		self.DTstring.set(TimeParam[0])
		self.TFstring.set(TimeParam[1])

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

	def checkMODEL(self,event=None):																																						## Funcao para checar o modelo de micromistura
		self.entryCw.configure(state="disabled") 																																				#Desabilita Cw
		self.entryAlpha.configure(state="disabled") 																																			#Desabilita alpha
		self.entryD0.configure(state="disabled") 																																				#Desabilita D0
		if self.MODELvar.get() == "IEM/LMSE": 																																					#Se for modelo IEM/LMSE habilita apenas Cw
			self.entryCw.configure(state="normal")
		elif self.MODELvar.get() == "Curl Modificado": 																																			#Se for modelo Curl Modificado habilita apenas alpha
			self.entryAlpha.configure(state="normal")
		elif self.MODELvar.get() == "Langevin" or self.MODELvar.get() == "Langevin Estendido" : 																								#Se for modelo de Langevin habilita apenas D0
			self.entryD0.configure(state="normal")

	def help(self):																																											## Funcao para abrir o
		subprocess.Popen(["manual.pdf"],shell=True)																																														

###############################################################################
##                               CLASSE PARTICULA                            ##
###############################################################################

class part():																																													## Classe 'part' para criar cada particula
	def __init__(self,position,velocity,comp,T):
		global elementos
		[x,y,z]=position 																																											# Le a posicao x, y e z da particula
		[u,v,w]=velocity 																																											# Le a velocidade u, v e w 
		self.x=x 																																													# Salva a posicao x
		self.y=y																																													# Salva a posicao y
		self.z=z																																													# Salva a posicao z

		self.u=u																																													# Salva a velocidade x
		self.v=v																																													# Salva a velocidade y
		self.w=w																																													# Salva a velocidade z

		self.comp=comp 																																												# Le e salva a composicao

		self.old_position=np.array([100,100,100]) 																																					# Define como posicao anterior [100,100,100]

		self.gamma=0.01 																																											# Define o gamma como 0.01
		self.gamma_old=0.01																																											# Define o gamma anterior como 0.001
		self.gamma_t=0.0																																											# Define o gamma turbulento como 0.0
		self.gamma_t_old=0.0																																										# Define o gamma turbulento anterior como 0.0

		self.T=  1200.																																												# [K] Temperatura	
		self.P=101325       																																										# [Pa] Pressao
		self.rho=287/self.P*self.T      																																							# [Kg/m^3] Densidade pela lei dos gases perfeitos

		self.R_r=0																																													# R_rEXPLAIN

		omega_te=C_omega*(self.gamma+self.gamma_t)/(delta**2) 																																		# Calculo do omega 
		self.omega={}																																												# Dicionario vazio
		for id, element in enumerate(elementos): 																																					# Para todos elementos
			self.omega[elementos[id]]=omega_te 																																						# Adicionar um omega correspondente no dicionario

		self.gas=ct.Solution(ap.solution_input[0],ap.solution_input[1]) 																															# Cria uma solucao do cantera dentro de cada particula

		self.gas.TPX=self.T,self.P,self.comp 																																						# Atualiza a temperatura, pressao e composicao do cantera

	def getPosition(self): 																																										## Funcao que retorna vetor das posicoes da particula
		return np.array([self.x,self.y,self.z])

	def getOlderPosition(self):																																									## Funcao que retorna vetor das posicoes antigas da particula
		return self.old_position

	def getVelocity(self):																																										## Funcao que retorna vetor das velocidades da particula
		return np.array([self.u,self.v,self.w])

	def setPosition(self,pos):																																									## Funcao que define vetor das posicoes da particula
		self.old_position=np.array([self.x,self.y,self.z])
		self.x=pos[0]
		self.y=pos[1]
		self.z=pos[2]

	def setVelocity(self,vel):																																									## Funcao que define vetor das velocidades da particula
		self.u=vel[0]
		self.v=vel[1]
		self.w=vel[2]

	def updateGamma(self,new):																																									## Funcao que atualiza o gamma
		self.gamma_old=self.gamma
		self.gamma=new

	def updateXT(self):																																											## Funcao que atualiza a temperatura e a composicao
		#c=1-self.comp["CH4"]/self.Xco
		#print(self.Xco)
		#self.T= c * (Tb-Tu) + Tu
		#self.T=1200.
		self.P=self.gas.P 					
		self.gas.TPX=self.T,self.P,self.comp 

###############################################################################
##                              FUNCOES DO PROGRAMA                          ##
###############################################################################

def random_float(min,max): 																																										## Funcao para gerar uma variavel float aleatoria entre min e max
	result=0
	while result >=max or result<=min:
		result=random()*(max-min)+min
	return result

def plot_3D(x,y,z,data,plot):																																									## Funcao para plotar o grafico 3D com uma composicao predefinida (NAO ESTA EM USO) 
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

def plot_T(x,y,z,T):																																											## Funcao para plotar o grafico 3D com a temperatura
	global frame_T,filenames_T
	fig=plt.figure()
	ax = fig.add_subplot(1,1,1, projection='3d')
	pnt1=ax.scatter(x,y,z,c=T,cmap=plt.cm.jet, edgecolor='black',vmax=Tb,vmin=Tu)
	cbar=plt.colorbar(pnt1)
	plt.xlim(0.0,1.0)
	plt.ylim(0.0,1.0)
	ax.set_zlim3d(0.0,1.0)
	cbar.set_label("Temperature [K]")
	ax.set_xlabel('Eixo x')
	ax.set_ylabel('Eixo y')
	ax.set_zlabel('Eixo z')
	frame_T[0]+=1
	frame_T[1]=t
	name='OUTPUT/frames/t_'+str(frame_T[0])+'.png'
	filenames_T.append(name)
	plt.savefig(name)
	plt.close('all')

def plot_PDF(data_t,plot): 																																										## Funcao para plotar o grafico da PDF e da CDF
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
##                               FUNCAO SIMULAR                              ##
###############################################################################

def Simulate(Wall,Param,DT,TF,Model,React,PlotConfiguration):

	global frame_3D,frame_CDF,frame_PDF,frame_T,filenames_3D,filenames_CDF,filenames_PDF,filenames_T
	global t,dt,npart,part_u,C_omega,alpha,d0
	global erro, used
	erro=0

	ap.promptPrint("Setting initial parameters...")
	root.update()

	part_u=[]
	filenames_3D=[]
	filenames_T=[]
	filenames_CDF=[]
	filenames_PDF=[]

	frame_3D=[0,0]
	frame_CDF=[0,0]
	frame_PDF=[0,0]
	frame_T=[0,0]

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
	##                          INICIO DO LOOP                                   ##
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
		

	  #Resetando os vetores e valores necessarios
		x=[]
		y=[]
		z=[]
		p=[]
		T=[]
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
			elif max(part_i.getVelocity())!=0:
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
				T.append(part_i.gas.T)
				for id,element in enumerate(plot):
					p[id].append(part_i.comp[element])
			#Plotando e salvando imagens
#			plot_3D(x,y,z,p,plot)
			plot_T(x,y,z,T)
			plot_PDF(p,plot)

	  #Reacao Quimica
		React()

	  #Calculando a composicao media
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
	##                          GERACAO DOS GIFS                                 ##
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
##                           MODELOS DE COMBUSTAO                            ##
###############################################################################

def BurnCantera():
	global part_u
	for id, part_i in enumerate(part_u):
		part_i.R_r=part_i.gas.net_production_rates#*1000

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
		#part_i.updateXT()
		part_i.gas.X=part_i.comp
		
	#print(part_i.comp)

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
##                     DEFININDO CONSTANTES E PARAMETROS                     ##
###############################################################################

global div,n_div,d,k,E_a,T_a,E_a,alpha,beta,gamma,PRE_EXP,delta,ap
global used
used=0										# Contador de linhas usadas no LOG Console
	  
div = 100                                   #divisao da variavel z associada ao PDF
n_div = 1/div
d = n_div
k = 0                                       #contador

#E_a=83600/9.28 #9000 #8.36 #10.45 #8.36
#T_a=E_a/8.315 #10054.0
Tu=560.
Tb=2000.
#alpha = (Tb-Tu)/Tb #0.7273 #6.
#beta =(alpha*T_a)/2000. #2.0 #6.287 #17.95 #13. #10.0d0 #17.95
#gamma=0.5*beta**2*(1.0+0.5*beta*(3.0*alpha-1.344)) 
#PRE_EXP=(gamma*1.2*1.2)/(0.0000751*exp(-beta/alpha))

delta = 0.1                                 #Tamanho do filtro

###############################################################################
##                       INICIO DA INTERFACE GRAFICA                         ##
###############################################################################
#Criação do ambiente
root = Tk(className=" CHARMANDER : beta version")   

try:   	#Windows
	root.state('zoomed')  			#Fullscreen
	root.iconbitmap('icon.ico') 	#Icon
except: #Linux
	root.attributes('-zoomed',True) #Fullscreen
	root.iconbitmap('@icon.xbm')	#Icon
#Inicio da Interface Grafica

ap=App(root)
root.mainloop()