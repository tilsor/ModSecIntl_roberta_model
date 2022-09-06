from lib2to3.pgen2 import token
import logging
from concurrent.futures import ThreadPoolExecutor
from operator import index
import string

import grpc
import numpy as np

from serverRoberta.roberta_pb2 import modSecIntlResponse
from serverRoberta.roberta_pb2 import modDataLog
from serverRoberta.roberta_pb2_grpc import modSecIntlServicer, add_modSecIntlServicer_to_server
from serverRoberta.robertaModel import RobertaModelEncode
from fairseq.models.roberta import RobertaModel
from serverRoberta.encrypt import Encrypt
from serverRoberta.datos import datos
import pickle
import os
import time
import configparser
from distutils.util import strtobool

class ModSecIntlServer(modSecIntlServicer):
    def __init__(self,roberta):
        self.serverRoberta=roberta
    def Detect(self, request, context):
        data = request.metrics[0]
        pred = self.serverRoberta.roberta_modSecIntl(data.value)
        resp = modSecIntlResponse(response=pred)
        return resp

class server:
    def __init__(self):
        config = configparser.ConfigParser()    
        path = '/'.join((os.path.abspath(__file__).replace('\\', '/')).split('/')[:-1])
        config.read(os.path.join(path, 'config.ini'))
        data_config = config["DATA"]
        self.dataBPE = data_config['BPE']
        self.model = data_config['MODEL']
        self.oneClass=data_config['ONECLASS']
        server_config = config["SERVER"]
        self.port=server_config['PORT']
        general_config = config["CONFIG"]
        self.obfuscation=general_config['OBFUSCATION']
        self.roberta=None
        self.map=None

    def roberta_modSecIntl(self,data: string):
        inicio=time.time()
        if bool(strtobool(self.obfuscation)):
            pred = self.roberta.evalObfuscation(self.map,data)
            logging.info('time data obfuscation eval ready %r ',time.time()-inicio)   
        else:  
            pred = self.roberta.eval(data) 
            logging.info('time data eval ready %r ',time.time()-inicio) 

        out=[]
        out.append(modDataLog(label=pred.label,decision=pred.decision))
        with open(self.dataBPE+"/dataTime.csv", 'a') as f:
            f.write(str(self.roberta.token)+","+str(self.roberta.timeTokenize)+","+str(self.roberta.timeApply_bpe)+","+str(self.roberta.timeObfuscate)+","+str(self.roberta.timeBinarize)+","+str(self.roberta.timeExtract_features)+","+str(self.roberta.timePredict)+","+str(self.roberta.timeDecision)+","+str(self.roberta.total)+"\n")
            f.close()
            
        return out    

def main():
    serverRoberta= server()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )
    
    robertaModel = RobertaModel.from_pretrained(data_name_or_path=serverRoberta.dataBPE,checkpoint_file=serverRoberta.model,model_name_or_path=serverRoberta.dataBPE)
    logging.info('load model')
    algorithm=pickle.load(open(os.path.join(serverRoberta.dataBPE, serverRoberta.oneClass), 'rb'))
    logging.info('load algorithm')
    
    encrypt=Encrypt()
    serverRoberta.roberta= RobertaModelEncode(serverRoberta.dataBPE,robertaModel,algorithm)   
    
    if bool(strtobool(serverRoberta.obfuscation)):
        serverRoberta.map=encrypt.load_map(serverRoberta.roberta.model_path) 
        logging.info('load map')

    server_grpc = grpc.server(ThreadPoolExecutor())
    add_modSecIntlServicer_to_server(ModSecIntlServer(serverRoberta), server_grpc)
    server_grpc.add_insecure_port(f'[::]:{serverRoberta.port}')
    server_grpc.start()
    logging.info('server ready on port %r', serverRoberta.port)
    server_grpc.wait_for_termination()     

if __name__ == '__main__':
    main()
