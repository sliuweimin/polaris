# -*- coding: utf-8 -*-
"""
Created on Sun Jul  9 10:25:42 2017

@author: samuel
"""

from tkinter import *
from tkinter import ttk
import pandas as pd
from tkinter import filedialog
from tkinter import simpledialog
import os
import itertools
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np

atomic_mass = {'C':12.0107, 'H':1.007825, 'N':14.003074, 'O':15.9949146, 'S':31.972071, 'e':0.0005485799, 'CH2':14.01565}
mass_tolerance=0.0015*14.01565/14

class Compound:
    def __init__(self,c,h,n,o,s,mode):
        self.c=c
        self.h=h
        self.o=o
        self.n=n
        self.s=s
        self.mode=mode
        self.mw=self.mw()
        self.realh=self.realh()
        self.dbe=(2*c+2+n-self.realh)/2
        self.km=self.mw/atomic_mass['CH2']*14
        self.kmd=int(self.km)+1-self.km
        self.memw=0
        self.intensity=0
        self.ppm = 0
        self.specie=self.specie()
        
    def mw(self):
        if self.mode=='+':
            a=12 * self.c + atomic_mass['N'] *self. n + atomic_mass['S'] *self. s + atomic_mass['O'] * self.o + atomic_mass['H']*self. h - atomic_mass['e']
        elif self.mode=='-':
            a=12 * self.c + atomic_mass['N'] *self. n + atomic_mass['S'] *self. s + atomic_mass['O'] * self.o + atomic_mass['H']*self. h + atomic_mass['e']
        return a

    def realh(self):
        if self.mode=='+':
            b=self.h-1
        if self.mode=='-':
            b=self.h+1
        return b
        
    def specie(self):
        specie_n=''
        specie_o=''
        specie_s=''
        if self.n!=0:
            specie_n='N'+'%d'%self.n 
        if self.o!=0:
            specie_o='O'+'%d'%self.o 
        if self.s!=0:
            specie_s='S'+'%d'%self.s 
        specie_all=specie_n+specie_o+specie_s
        return specie_all
            

def isMolecule(a,mw_min):
    if a.n!=0 or a.o!=0 or a.s!=0:
        if 0.3<=a.h/a.c<=3.0:
            if a.o/a.c<=3.0 and a.n/a.c<=0.5:
                if a.h<=1+2*a.c+a.n:
                    if (a.h+a.n)%2 == 1:
                        if a.mw>=mw_min:
                            return True

def excelSave(excelFile):
    path=filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=(('Excel', '*.xlsx'), ('2003 Excel', '*.xls'),('All Files', '*.*')))
    if path is None:
        return
    else:
        writer=pd.ExcelWriter(path, engine = 'xlsxwriter')
    excelFile.to_excel(writer,'Sheet1')
    writer.save()

def readAllExcel(path):
    excelFilePath=[]
    for root,dirs,files in os.walk(path):
        for excel in files:
            if os.path.splitext(excel)[1] == '.xlsx':
                excelFilePath.append(path+'/'+excel)
    return excelFilePath

class MenuBar(Menu):       
    
    def __init__(self,parent):
        Menu.__init__(self,parent)
        
        fileMenu=Menu(self)
        self.add_cascade(label='File', menu=fileMenu)
        fileMenu.add_command(label='import from clipboard', command=self.readClipboard)
        fileMenu.add_command(label='import from excel', command=self.readExcel)
        fileMenu.add_command(label='import from folder',command=self.readFolder)
        
        self.text_widget=parent.text_widget
        
        self.data=pd.DataFrame().astype(float)
        self.folder_path=0
        self.excelName=0
        
        calMenu=Menu(self)
        self.add_cascade(label='Calculate', menu=calMenu)
        calMenu.add_command(label='Class abundance from excel', command=self.calAbundance)
        calMenu.add_command(label='Class abundance from folder', command=self.calAbundanceFile)
        calMenu.add_command(label='Class DBE abundance from excel', command=self.caldbeAbundance)
        calMenu.add_command(label='Class DBE abundance from folder', command=self.caldbeAbundanceFile)
        
        plotMenu=Menu(self)
        self.add_cascade(label='Plot', menu=plotMenu)
        plotMenu.add_command(label='Bar plot from excel', command=self.barplot)
        plotMenu.add_command(label='Bubble plot from folder', command=self.bubbleplot)
        
        aboutMenu=Menu(self)
        self.add_cascade(label='Help', menu=aboutMenu)
        aboutMenu.add_command(label='About', command=self.aboutMessage)
        
        
        
        
    def readClipboard(self):
        self.data = pd.read_clipboard()
        self.excelName='Clipboard'
        self.text_widget.delete('1.0',END)
        self.text_widget.insert(END,self.data)
        
    def readExcel(self):
        excel_path=filedialog.askopenfilename(defaultextension='.xlsx', filetypes=(('Excel', '*.xlsx'), ('2003 Excel', '*.xls'), ('CSV', '*.csv'), ('All Files', '*.*')))
        if os.path.splitext(excel_path)[1] == '.xlsx' or 'xls':
            self.data = pd.read_excel(excel_path)
        elif os.path.splitext(excel_path)[1] == '.csv':
            self.data = pd.read_csv(excel_path)
        excelName=os.path.splitext(excel_path)[0]
        self.excelName=excelName.split('\\')[-1]
        self.text_widget.delete('1.0',END)
        self.text_widget.insert(END,self.data)
        
    def readFolder(self):
        self.folder_path=filedialog.askdirectory()
        self.text_widget.delete('1.0',END)
        path=readAllExcel(self.folder_path)
        self.text_widget.insert(END,'These are the Excels found in the path: \n')
        for paths in path:
            self.text_widget.insert(END,paths+'\n')
        
    def calAbundance(self):     
        data=self.data
        if not 'normalized' in data.columns:
            data['normalized']=data['intensity']/data['intensity'].sum()        
        species=data['class']
        species=species.drop_duplicates()
        abundance=pd.DataFrame().astype(float)
        for specie in species:
            data_specie=data[data['class'] == specie]
            abundance.loc[specie,self.excelName] = data_specie['normalized'].sum()
        self.text_widget.delete('1.0',END)
        self.text_widget.insert(END,abundance)
        excelSave(abundance)
        
    def calAbundanceFile(self):
        excelFile=readAllExcel(self.folder_path)
        abundance=pd.DataFrame().astype(float)
        for excel in excelFile:
            self.excelName=os.path.split(excel)[1]
            self.excelName=os.path.splitext(self.excelName)[0]
            self.data=pd.read_excel(excel)
            data=self.data
            if not 'normalized' in data.columns:
                data['normalized']=data['intensity']/data['intensity'].sum()        
            species=data['class']
            species=species.drop_duplicates()
            for specie in species:
                data_specie=data[data['class'] == specie]
                abundance.loc[specie,self.excelName] = data_specie['normalized'].sum()
            self.text_widget.delete('1.0',END)
            self.text_widget.insert(END,abundance)
        excelSave(abundance)
            
            
    def caldbeAbundance(self):     
        data=self.data
        if not 'normalized' in data.columns:
            data['normalized']=data['intensity']/data['intensity'].sum()        
        species=data['class']
        species=species.drop_duplicates()
        abundance=pd.DataFrame().astype(float)
        dbe = 0 
        for specie in species:
            data_specie=data[data['class'] == specie]
            for dbe in range(0,20):
                data_dbe=data_specie[data_specie['DBE'] == dbe]
                abundance.loc[specie,dbe] = data_dbe['normalized'].sum()
        self.text_widget.delete('1.0',END)
        self.text_widget.insert(END,abundance)
        excelSave(abundance)
 
    def caldbeAbundanceFile(self):
        excelFile=readAllExcel(self.folder_path)
        for excel in excelFile:
            self.excelName=excel
            self.data=pd.read_excel(excel)
            self.caldbeAbundance()
    
    def barplot(self):
        data=self.data
        plt.figure(figsize=(15,10))
        plt.bar(data.index,data.iloc[:,0],align='center', alpha=0.5)
        plt.show()
    
    def bubbleplot(self):
        os.chdir(self.folder_path)
        excelFile=readAllExcel(self.folder_path)
        species=simpledialog.askstring('Required classes','e.g., N1,O2')
        species=species.split(',')
        for specie in species:
            if os.path.exists(specie)==False:
                os.makedirs(specie)
        for excel in excelFile:
            data=pd.read_excel(excel)
            data=data[data['DBE']>0]
            excelName=os.path.split(excel)[1]
            excelName=os.path.splitext(excelName)[0]
            data['intensity']=data['intensity'].astype(float)
            for specie in species:
                data_specie=data[data['class']==specie]
                sum=data_specie['intensity'].sum()
                data_specie['normalized']=data_specie['intensity']/sum
                plt.figure(figsize=(6,5))
                font = {'family' : 'arial',  
                        'color'  : 'black',  
                        'weight' : 'normal',  
                        'size'   : 20,  
                        } 
                plt.axis([0,50,0,25])
                plt.xlabel("Carbon Number",fontdict=font)
                plt.ylabel("DBE",fontdict=font)
                plt.xticks(fontsize=16,fontname='arial')
                plt.yticks(np.arange(0,26,5),fontsize=16,fontname='arial')
                plt.text(1,23,s=specie,fontdict=font)
                plt.text(43,23,s=excelName,fontdict=font)
                plt.scatter(data_specie['C'],data_specie['DBE'],s=1000*data_specie['normalized'],edgecolors='black',linewidth=0.1)
                path=self.folder_path+"\\"+specie
                filename=excelName+'.png'
                plt.savefig(os.path.join(path,filename),dpi=600)
        
    def aboutMessage(self):
        messagebox.showinfo(title='About', message='FT–ICR MS Data Handler\nLicensed under the terms of the Apache License 2.0\n\nDeveloped and maintained by Weimin Liu\n\nFor bug reports and feature requests, please go to my Github website')
        
class RawDataFrame:
    
    def __init__(self,parent,menubar):
        self.frame=Frame(parent)
        self.frame.pack()
        
        self.menubar=menubar
        
        self.rawlabel=Label(self.frame, text='RAW DATA\t')
        self.rawlabel.grid(row=0,column=0)
                
        self.snLabel=Label(self.frame, text='S/N')
        self.snLabel.grid(row=0,column=1)
        self.snEntry=Entry(self.frame)
        self.snEntry.insert(END,'6')
        self.snEntry.grid(row=0,column=2)
        
        self.ppmLabel=Label(self.frame, text='error(ppm)')
        self.ppmLabel.grid(row=0,column=3)
        self.ppmEntry=Entry(self.frame)
        self.ppmEntry.insert(END,'1.2')
        self.ppmEntry.grid(row=0,column=4)
        
        self.nLabel=Label(self.frame, text='N')
        self.nLabel.grid(row=0,column=5)
        self.nEntry=Entry(self.frame)
        self.nEntry.insert(END,'5')
        self.nEntry.grid(row=0,column=6)
        
        self.oLabel=Label(self.frame, text='O')
        self.oLabel.grid(row=0,column=7)
        self.oEntry=Entry(self.frame)
        self.oEntry.insert(END,'5')
        self.oEntry.grid(row=0,column=8)
        
        self.sLabel=Label(self.frame, text='S')
        self.sLabel.grid(row=0,column=9)
        self.sEntry=Entry(self.frame)
        self.sEntry.insert(END,'5')
        self.sEntry.grid(row=0,column=10)
        
        self.modeLabel=Label(self.frame, text='ESI mode(+,-)')
        self.modeLabel.grid(row=0,column=11)
        self.modeEntry=Entry(self.frame)
        self.modeEntry.insert(END,'+')
        self.modeEntry.grid(row=0,column=12)
        
        self.processButton=Button(self.frame, text='Process', command=self.processData)
        self.processButton.grid(row=0,column=13)
        
        self.text_widget=parent.text_widget
                
    def processData(self):
        
        saveExcel=pd.DataFrame()
        for i in ('measured m/z','m/z','ppm','class','C','H','O','N','S','DBE','intensity'):
            saveExcel.loc[0,i]=i
            i+=i
        count=0
        self.data=self.menubar.data
        self.data = self.data[self.data['S/N']>=int(self.snEntry.get())]
        for column in self.data:
            if column != 'm/z' and column != 'I':
                del self.data[column]
        mw_max=self.data['m/z'].max()
        mw_min=self.data['m/z'].min()
        for N,O,S in itertools.product(range(int(self.nEntry.get())+1), range(int(self.oEntry.get())+1),range(int(self.sEntry.get())+1)):
            c_max=int((mw_max-14*N-16*O-32*S)/12)
            for C in range(1,c_max+1):
                h_max=int(mw_max)-12*C-14*N-16*O-32*S+1
                for H in range(1,h_max+1):
                    molecule=Compound(C,H,N,O,S,self.modeEntry.get())
                    if isMolecule(molecule,mw_min):
                        data_test=self.data[(self.data['m/z']>=(molecule.mw-mass_tolerance)) & (self.data['m/z']<=(molecule.mw+mass_tolerance))]
                        if not data_test.empty:
                            molecule.intensity = data_test['I'].max()
                            data_test = data_test[data_test['I']==molecule.intensity]
                            data_test = data_test['m/z'].tolist()
                            molecule.memw = data_test[0]
                            molecule.ppm = abs(1000000*(molecule.mw-molecule.memw)/molecule.mw)
                            if molecule.ppm <= float(self.ppmEntry.get()):
                                stringTovar={'measured m/z':molecule.memw,'m/z':molecule.mw,'ppm':molecule.ppm,'class':molecule.specie,'C':molecule.c,'H':molecule.realh,'O':molecule.o,'N':molecule.n,'S':molecule.s,'DBE':molecule.dbe,'intensity':molecule.intensity}
                                for column in saveExcel:
                                    saveExcel.loc[count,column]=stringTovar[column]
                                count+=1
        self.text_widget.delete('1.0',END)
        self.text_widget.insert(END,saveExcel)
        excelSave(saveExcel)
 
class DataFrame:
    
    def __init__(self,parent,menubar):
        self.frame=Frame(parent)
        self.frame.pack()
        
        


       
        
class App(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.text_widget = Text(self)
        self.text_widget.pack()
        menubar = MenuBar(self)
        
        self.config(menu=menubar)
        
        
        rawdataframe =RawDataFrame(self,menubar)
        dataframe=DataFrame(self,menubar)

        
if __name__ == '__main__':
    app=App()
    app.title("FT-ICR MS Data Handler v0.1")
    app.mainloop()