import copy


class Instrucao:
    def __init__(self, opcode, op1, op2, op3, valida, operacao, previsto, pcInstrucao):
        self.opcode = opcode
        self.op1 = op1
        self.op2 = op2
        self.op3 = op3
        self.valida = valida
        self.operacao = operacao
        self.previsto = previsto
        self.pcInstrucao = pcInstrucao

    def __str__(self):
        if self.opcode.startswith("J"):
            return f'{self.opcode} {self.op1} '
        
        if self.opcode.startswith("BEQ"):
            return f'{self.opcode} R{self.op1} R{self.op2} {self.op3}'
            
        
        return f'{self.opcode} R{self.op1} R{self.op2} R{self.op3}'

class Pipeline:
    def __init__(self, utilizarPredicao):
        # Inicialização dos registradores, PC, etc.
        self.registradores = [0]*32
        self.PC = 0
        self.jump = False
        self.instrucoes = []
        self.estagios = [[None] for _ in range(5)]  # Estágios do pipeline
        self.tempR = [0]*32  # Registradores temporários
        self.predicao = [0]*32  # Tabela de predição
        self.utilizarPredicao = utilizarPredicao
        self.instrucaoExecutada = 0
        self.instrucaoInvalida = 0

    def carregarArquivoInstrucoes(self, program_file):
        # Carrega as instruções de um arquivo
        with open(program_file) as arquivo:
            for i, linha in enumerate(arquivo):
                partes = linha.split()
                opcode = partes[0]
                if opcode.startswith("J"):
                    op1 = int(partes[1])
                    self.instrucoes.append(Instrucao(opcode, op1, 0, 0, True, None, False, i))
                else:
                    op1, op2, op3 = map(lambda x: int(x[1:]) if x.startswith("R") else int(x), partes[1:])
                    self.instrucoes.append(Instrucao(opcode, op1, op2, op3, True, None, False, i))

    def carregarInstrucoes(self, instrucoes):
        for i, linha in enumerate(instrucoes):
            partes = linha.split()
            opcode = partes[0]
            if opcode.startswith("J"):
                op1 = int(partes[1])
                self.instrucoes.append(Instrucao(opcode, op1, 0, 0, True, None, False, i))
            else:
                op1, op2, op3 = map(lambda x: int(x[1:]) if x.startswith("R") else int(x), partes[1:])
                self.instrucoes.append(Instrucao(opcode, op1, op2, op3, True, None, False, i))

    def executarPipeline(self):
        ciclo = 1
        
        
        
        while self.PC < len(self.instrucoes) or any(estagio[0] is not None for estagio in self.estagios):
            # Move instrução para o próximo estágio
            for i in range(4, 0, -1):
                self.estagios[i][0] = self.estagios[i-1][0]

            # Fetch
            if self.PC < len(self.instrucoes):
                instrucaoAtual = copy.deepcopy(self.instrucoes[self.PC])

                # Verifica se a instrução atual já está em algum dos dois primeiros estágios do pipeline
                instrucao_sendo_processada = any(
                    instrucaoAtual.pcInstrucao == estagio[0].pcInstrucao
                    for estagio in self.estagios[:2]
                    if estagio[0] is not None
                )

                # Se a instrução atual não estiver sendo processada, insere no primeiro estágio e incrementa o PC
                if not instrucao_sendo_processada:
                    self.estagios[0][0] = instrucaoAtual
                    self.PC += 1
                else:
                    # Se a instrução atual já estiver sendo processada, tenta buscar a próxima instrução
                    if self.PC + 1 < len(self.instrucoes):
                        self.PC += 1
                        instrucaoAtual = copy.deepcopy(self.instrucoes[self.PC])
                        self.estagios[0][0] = instrucaoAtual
                        self.PC += 1
                    else:
                        # Se não houver mais instruções para buscar, define o primeiro estágio como None
                        self.estagios[0][0] = None
                        self.PC += 1
            else:
                # Se o PC já tiver alcançado o final da lista de instruções, define o primeiro estágio como None
                self.estagios[0][0] = None


            # Predicao ligado
            if self.utilizarPredicao: 
                if self.estagios[0][0] is not None and self.estagios[0][0].opcode == 'BEQ':
                    if self.predicao[self.estagios[0][0].op3] == 1:
                        self.PC = self.estagios[0][0].op3
                        self.estagios[0][0].previsto = True
                        self.instrucaoExecutada += 1
                        
                        
            
            # Decode
            if self.estagios[1][0] is not None:
                instrucaoAtual = self.estagios[1][0]
                
                instrucaoAtual.operacao = instrucaoAtual.opcode
                
                
            # Execute
            if self.estagios[2][0] is not None and self.estagios[2][0].valida and not self.estagios[2][0].previsto:
                
                instrucaoAtual = self.estagios[2][0]
                operacao = instrucaoAtual.operacao
                
                if operacao == 'ADD':
                    self.tempR[instrucaoAtual.op1] = self.tempR[instrucaoAtual.op2] + self.tempR[instrucaoAtual.op3]
                    self.instrucaoExecutada+=1
                    
                    
                elif operacao == 'ADDI':
                    self.tempR[instrucaoAtual.op1] = self.tempR[instrucaoAtual.op2] + instrucaoAtual.op3
                    self.instrucaoExecutada+=1
                    
                    
                elif operacao == 'SUB':
                    self.tempR[instrucaoAtual.op1] = self.tempR[instrucaoAtual.op2] - self.tempR[instrucaoAtual.op3]
                    self.instrucaoExecutada+=1
                    
                    
                elif operacao == 'SUBI':
                    self.tempR[instrucaoAtual.op1] = self.tempR[instrucaoAtual.op2] - instrucaoAtual.op3
                    self.instrucaoExecutada+=1
                    
                    
                elif operacao == 'BEQ':
                    if self.tempR[instrucaoAtual.op1] == self.tempR[instrucaoAtual.op2]:
                        self.instrucaoExecutada+=1
                        self.PC = instrucaoAtual.op3
                        self.jump = True
                        self.predicao[instrucaoAtual.op3] = 1
               
               
                elif operacao == 'J':
                    self.instrucaoExecutada+=1
                    self.PC = instrucaoAtual.op1
                    self.jump = True
                    
                    
                    
            if self.estagios[2][0] is not None and self.estagios[2][0].previsto and self.estagios[2][0].valida:
                instrucaoAtual = self.estagios[2][0]
                if self.tempR[instrucaoAtual.op1] != self.tempR[instrucaoAtual.op2]:
                    self.PC = instrucaoAtual.pcInstrucao + 1
                    self.jump = True
                    self.predicao[instrucaoAtual.op3] = 0
                           
                    
            # Invalida a instrução a ser pulada
            if self.jump:
                for i in range(2):
                    if self.PC>len(self.instrucoes):
                        if self.estagios[i][0] is not None:
                            self.estagios[i][0].valida = False
                            self.instrucaoInvalida += 1
                    elif self.estagios[i][0] is not None and self.estagios[i][0].pcInstrucao != self.PC:
                        self.estagios[i][0].valida = False
                        self.instrucaoInvalida += 1
                self.jump = False
                
            
            # Memory acess
            
            
            
            # Writeback        
            if self.estagios[4][0] is not None:
                
                instrucaoAtual = self.estagios[4][0]
                
                if instrucaoAtual.opcode in ['ADD', 'ADDI', 'SUB', 'SUBI']:
                    self.registradores[instrucaoAtual.op1] = self.tempR[instrucaoAtual.op1]
                
             
            
            
            # Imprime os estágios
            print(f'Ciclo {ciclo}:')
            for i in range(4, -1, -1):
                estagio = self.estagios[i][0]
                print(f'Estágio {i+1}: {str(estagio) if estagio else "Empty"} Valid: {estagio.valida if estagio else "N/A"}')
            print()
            print("Estado dos registradores:")
            print(self.registradores)
            print('------------------------------------------------------------------------')
            
              
            ciclo += 1 
            
            
        return (ciclo - 1, self.instrucaoExecutada, self.instrucaoInvalida)

instrucoes = [
    'ADDI R1 R0 R-1',
    'ADDI R2 R0 R10',
    'ADDI R3 R0 R1',
    'ADD R2 R1 R2',
    'BEQ R2 R0 20',
    'BEQ R0 R0 3'
    
]

# Execução do pipeline sem predição
pipeline = Pipeline(False)
pipeline.carregarArquivoInstrucoes('instrucoes.txt')
ciclosSemPredicao, instrucaoExecutadaSemPredicao, instrucaoInvalidaSemPredicao = pipeline.executarPipeline()


# Execução do pipeline com predição
pipeline = Pipeline(True)
pipeline.carregarArquivoInstrucoes('instrucoes.txt')
ciclosComPredicao, instrucaoExecutadaComPredicao, instrucaoInvalidaComPredicao = pipeline.executarPipeline()

print('Na execução sem utilizar a predição, tiveram:')
print(f'{ciclosSemPredicao} ciclos;')
print(f'{instrucaoExecutadaSemPredicao} instruções executadas;')
print(f'{instrucaoInvalidaSemPredicao} instruções inválidas;')

print('------------------------------------------------------------------------')

print('Na execução utilizando a predição, tiveram:')
print(f'{ciclosComPredicao} ciclos;')
print(f'{instrucaoExecutadaComPredicao} instruções executadas;')
print(f'{instrucaoInvalidaComPredicao} instruções inválidas;')


# Cálculo da melhoria de ciclos
porcentagem = format(100 - (ciclosComPredicao * 100)/ciclosSemPredicao, '.2f')
print('------------------------------------------------------------------------')
print(f'Utilizando a predição, houve uma melhoria de {porcentagem}% no número de ciclos')
