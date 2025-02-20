# Crie um sistema de chamados, o sistema deverá permitir:

# Cadastrar novos chamados
# Buscar chamados por ID ou descrição
# Remover chamados finalizados
# Listar chamados em ordem de prioridade
# Exibir estatísticas sobre os chamados
# Reverter e limpar a lista de chamados 
# Projeto deve ser inserido no Github, listado como público. 

import json as j
import os

METADATA_PATH = 'database\\metadata.json'
DATABASE_PATH = 'database\\chamados.json'
MENU = '''\
=========================
Sistema de Chamados
=========================
1 - Cadastrar novo chamado
2 - Buscar chamado por ID
3 - Buscar chamado por descrição
4 - Remover chamado finalizado
5 - Listar chamados por prioridade
6 - Exibir estatísticas
7 - Reverter lista de chamados
8 - Limpar lista de chamados
=========================
0 - Sair'''


class Chamado:
    def __init__(self, descricao:str, prioridade:str, status:bool=True, id:int=None):
        self.id = id
        self.descricao = descricao
        self.prioridade = prioridade
        self.status = status
    
    def to_dict(self) -> dict:
        return {
            'status': self.status,
            'prioridade': self.prioridade,
            'descricao': self.descricao }
    

class Database:
    def __init__(self):    
        if not os.path.exists(DATABASE_PATH):
            with open(DATABASE_PATH, 'w') as f:
                j.dump({"id_numbers": 0}, f)
        try:
            with open(DATABASE_PATH, 'r') as f:
                self.data = j.load(f)
        except j.JSONDecodeError:
            self.data = {"id_numbers": 0}
        except Exception as e:
            print(f"An error occurred while loading the database: {e}")
            self.data = {"id_numbers": 0}
            
        self.metadata = ["id_numbers","estatisticas"]
        
    def write_chamado_to_database(self, chamado:dict):
        
        self.get_id()
        self.data[f"{self.next_id}"] = chamado
        self.data["id_numbers"] = self.next_id
        
        with open(DATABASE_PATH, 'w') as f:
            j.dump(self.data, f, indent=4)

    def get_id(self):
        self.base_id = self.data.get("id_numbers", 0)
        self.next_id = self.base_id + 1
    
    def get_chamado_by_id(self, id:int) -> dict:
        return self.data.get(str(id), None)
    
    def get_chamado_by_descricao(self, descricao:str) -> list:
        result = []
        for chamado_id, chamado in self.data.items():
            if not chamado_id in self.metadata and descricao.lower() in chamado.get('descricao',"NullDescription").lower():
                result.append(chamado_id)
        return result

    def list_chamados_by_priority(self, reverse=False) -> list:
        result = []
        priority_order = {'high': 1, 'medium': 2, 'low': 3, 'NullPriority': 4}
        order_key = lambda x: priority_order.get(x[1], 4)
        for chamado_id, chamado in self.data.items():
            if not chamado_id in self.metadata:
                result.append((chamado_id, chamado.get('prioridade', 'NullPriority')))
        sorted_result = sorted(result, key=order_key, reverse=reverse)
        return [chamado_id for chamado_id, _ in sorted_result]

    def clean_finished_chamados(self):
        for chamado_id, chamado in self.data.items():
            if not chamado_id in self.metadata and not chamado.get('status', True):
                self.data.pop(chamado_id)
        with open(DATABASE_PATH, 'w') as f:
            j.dump(self.data, f, indent=4)
    
    def get_estatisticas(self):
        total_chamados = len([chamado for chamado_id, chamado in self.data.items() if chamado_id not in self.metadata])
        finalizados = len([chamado for chamado_id, chamado in self.data.items() if chamado_id not in self.metadata and not chamado.get('status', True)])
        por_prioridade = {
            'high': len([chamado for chamado_id, chamado in self.data.items() if chamado_id not in self.metadata and chamado.get('prioridade') == 'high']),
            'medium': len([chamado for chamado_id, chamado in self.data.items() if chamado_id not in self.metadata and chamado.get('prioridade') == 'medium']),
            'low': len([chamado for chamado_id, chamado in self.data.items() if chamado_id not in self.metadata and chamado.get('prioridade') == 'low']),
            'NullPriority': len([chamado for chamado_id, chamado in self.data.items() if chamado_id not in self.metadata and chamado.get('prioridade') == 'NullPriority'])
        }
        return {
            'total_chamados': total_chamados,
            'finalizados': finalizados,
            'por_prioridade': por_prioridade
        }
    
    def inverted_database(self):
        reversed_data = {k: v for k, v in reversed(self.data.items())}
        return reversed_data
    
    def clear_database(self):
        with open(DATABASE_PATH, 'w') as f:
            j.dump({"id_numbers": 0}, f)
    

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    db = Database()
    print(MENU)
    while True:
        option = input('Digite a opção desejada: ')
        if option == '0':
            break
        elif option == '1':
            descricao = input('Digite a descrição do chamado: ')
            prioridade = input('Digite a prioridade do chamado (high, medium, low): ')
            chamado = Chamado(descricao, prioridade)
            db.write_chamado_to_database(chamado.to_dict())
        elif option == '2':
            id = int(input('Digite o ID do chamado: '))
            chamado = db.get_chamado_by_id(id)
            if chamado:
                print(f"Chamado {id}: {chamado}")
            else:
                print(f"Chamado {id} não encontrado.")
        elif option == '3':
            descricao = input('Digite a descrição do chamado: ')
            chamados = db.get_chamado_by_descricao(descricao)
            if chamados:
                print(f"Chamados encontrados: {chamados}")
            else:
                print(f"Chamado com descrição {descricao} não encontrado.")
        elif option == '4':
            db.clean_finished_chamados()
            print("Chamados finalizados removidos.")
        elif option == '5':
            chamados = db.list_chamados_by_priority()
            print(f"Chamados por prioridade: {chamados}")
        elif option == '6':
            pass
        elif option == '7':
            pass
        elif option == '8':
            pass
        else:
            print('Opção inválida.')
        print(MENU)

if __name__ == '__main__':
    main()






