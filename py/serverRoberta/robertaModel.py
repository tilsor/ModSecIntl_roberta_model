from logging import exception
import os
from fairseq.models import roberta
from fairseq.models.roberta import RobertaModel
from fairseq.data.encoders.gpt2_bpe import get_encoder
from fairseq.data import encoders
import numpy
import torch
import pickle
import numpy as np
from serverRoberta.datos import datos
from serverRoberta.encrypt import Encrypt
import time

class RobertaModelEncode:
    def __init__(self,model_path,roberta,algorithm):
        self.roberta = roberta
        self.model_path=model_path
        self.tokenizer = encoders.build_tokenizer(self.roberta.args)
        self.bpe = encoders.build_bpe(self.roberta.args)
        self.src_dict = self.roberta.task.source_dictionary
        self.algorithm= algorithm
        self.timeTokenize=None
        self.timeApply_bpe=None
        self.timeObfuscate=None
        self.timeBinarize=None
        self.timePredict=None
        self.timeDecision=None
        self.timeExtract_features=None
        self.token=None
        self.total=None
       
    
    def eval(self,string):
        inicioEval = time.time(); 
        tokens=self.roberta.encode(string)
        last_layer_features = self.roberta.extract_features(tokens)  
        mean_feat = torch.mean(last_layer_features, 1).detach().numpy()[0]
        x_test_pu = np.array(mean_feat).reshape(-1, 768)
                
        decision=self.decision_function(x_test_pu)
        self.total=time.time()-inicioEval
        return decision
 
    def evalObfuscation(self,map,string):
        inicioEval = time.time();    
        x_test_pu=self.extract_features(map,string) 
        decision=self.decision_function(x_test_pu)
        self.total=time.time()-inicioEval
        return decision
    
    def decision_function(self,x_test_pu):
        inicio = time.time();  
        y_pred_pu = self.algorithm.predict(x_test_pu)
        self.timePredict=time.time()-inicio

        inicio = time.time();
        decision_pu = self.algorithm.decision_function(x_test_pu)
        self.timeDecision=time.time()-inicio
        threshold = -0.44
        if decision_pu <threshold:
            label="Attack"
        else:
            label="Valid"  
        return  datos(label,decision_pu) 
           
    def extract_features(self,map,string):
        tokens=self.encode(map,string)
        inicio=time.time()
        last_layer_features = self.roberta.extract_features(tokens)  
        mean_feat = torch.mean(last_layer_features, 1).detach().numpy()[0]
        feats = np.array(mean_feat).reshape(-1, 768)
        self.timeExtract_features=time.time()-inicio 
        return feats
         
    def encode(self,map,string):
        inicio=time.time()
        sentence = self.tokenize(string)   
        self.timeTokenize=time.time()-inicio

        inicio=time.time()
        sentence = self.apply_bpe(sentence)
        self.timeApply_bpe=time.time()-inicio
        self.token=len(sentence)

        inicio=time.time()
        sentence=self.obfuscate_bpe(map,sentence)
        self.timeObfuscate=time.time()-inicio

        inicio=time.time()
        binarize_result=self.binarize(sentence) 
        self.timeBinarize=time.time()-inicio
        return torch.tensor([0] + binarize_result.tolist()) 
    
    def obfuscate_bpe(self,map,sentence):
         sentenceObf=""
         for idx in sentence.split(" "):
                sentenceObf=sentenceObf+" "+self.obfuscate_idx_bpe(map,idx)
         return sentenceObf  
    
    def obfuscate_idx_bpe(self,map,idx): 
        return  str(map[idx.strip()]).strip('\n')        

    def apply_bpe(self, sentence: str)-> str:
        if self.bpe is not None:
            sentence = self.bpe.encode(sentence)
        return sentence            
    
    def tokenize(self, sentence: str)-> str:
        if self.tokenizer is not None:
            sentence = self.tokenizer.encode(sentence)
        return sentence
    
    def binarize(self, sentence: str) -> torch.LongTensor:
        return self.src_dict.encode_line(sentence, add_if_not_exist=False).long()        