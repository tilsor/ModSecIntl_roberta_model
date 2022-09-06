from logging import exception
import random
import torch


class Encrypt:
    def generate_mask(self,path_dict): 
      if not self.checkFileExistance(path_dict+"/map.txt"):
            f = open(path_dict+"/dict.txt", "r")
            lines = f.readlines()    
            dataDict = []
            dataDictRandom = []
            for i in range(len(lines)-3):
                dataDict.append(i)
                dataDictRandom.append(i)
            random.shuffle(dataDictRandom)
            self.save_map_bpe(path_dict+"/map.txt",dataDict,dataDictRandom) 
            
            k=len(lines)-3
            while(k < len(lines)):
                self.save_map_bpe_end(path_dict+"/map.txt",lines[k].split(" ")[0])
                k += 1
    
    def obfuscate_bpe(self,map,bpe): 
        splitBPE=bpe.split(",");
        bpe_mask=""
        for idx in splitBPE:
            if idx.find("[")!=-1:
               bpe_mask=bpe_mask+" "+ self.obfuscate_idx_bpe(map,idx.replace("[",""))
            elif idx.find("]")!=-1:  
               bpe_mask=bpe_mask+" "+ self.obfuscate_idx_bpe(map,idx.replace("]",""))
            else:
               bpe_mask=bpe_mask+" "+ self.obfuscate_idx_bpe(map,idx)
        return bpe_mask.strip()         
    
    def obfuscate_invert(self,map,bpe):
        splitBPE=bpe.split(" ");
        bpe_mask_invested=[]
        for idx in splitBPE:
            bpe_mask_invested.append(int(map[idx.rstrip('\n')]))   
        return bpe_mask_invested            
    
    def load_map(self,path_dict):
        if self.checkFileExistance(path_dict+"/map.txt"):            
            f = open(path_dict+"/map.txt", "r")
            lines = f.readlines() 
            map= {}  
            for line in lines:
                data=(line.rstrip('\n')).split(" ")                
                map[data[0]]=data[1]
            return map   
    
    def load_map_inverse(self,path_dict):
        if self.checkFileExistance(path_dict+"/map.txt"):            
            f = open(path_dict+"/map.txt", "r")
            lines = f.readlines() 
            map= {}  
            for line in lines:
                data=(line.rstrip('\n')).split(" ")                
                map[data[1]]=data[0]
            return map   

    def checkFileExistance(self,filePath):
        try:
            with open(filePath, 'r') as f:
                return True
        except FileNotFoundError as e:
            return False
        except IOError as e:
            return False              
    
    def save_map_bpe(self,file,dataDict,dataDictRandom):
        with open(file, 'a') as f:
            for indx in dataDict:
                f.write(str(dataDict[indx])+" "+ str(dataDictRandom[indx])+ "\n")
            f.close()  
    
    def save_map_bpe_end(self,file,data):
        with open(file, 'a') as f:
            f.write(str(data)+" "+ str(data)+ "\n")
            f.close()          
    
    def obfuscate_idx_bpe(self,map,idx): 
        return map[idx.strip()]
