
import json as j
import os
DATABASE_PATH = 'database\\database.json'


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

    def fechar_chamado(self, id:int):
        if str(id) not in self.data:
            return False
        self.data[f"{id}"]['status'] = False
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

    def get_all_ids(self) -> list:
        return [chamado_id for chamado_id in self.data.keys() if chamado_id not in self.metadata]

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
    
    def get_estatisticas(self) -> dict:
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
    
    def clear_database(self): # !!!! CUIDADO !!!!
        with open(DATABASE_PATH, 'w') as f:
            j.dump({"id_numbers": 0}, f)
    

class Menu:
    def __init__(self):
        self.main_menu = '''\
=====================================
|      SISTEMA   DE   CHAMADOS      |
=====================================
1 - Cadastrar novo chamado          |
2 - Buscar chamado por ID           |
3 - Buscar chamado por descrição    |
4 - listar chamadas                 |
5 - Listar chamados por prioridade  |
6 - Exibir estatísticas             |
8 - Limpar chamadas fechadas        |
7 - Reverter lista de chamados      |
9 - Limpar lista de chamados        |
=====================================
0 - Sair'''

    @classmethod
    def format_chamado(self,chamado:dict) -> str:

        if chamado.get('status', None) == None:
            f_status = "Error" # error = 5
        else:
            f_status = f"{'Aberto' if chamado.get('status') else 'Fechado'}" #aberto = 6 fechado = 7
        
        if chamado.get('prioridade', None) == None:
            f_prioridade = "Error"
        else:
            if chamado.get('prioridade') == 'high':
                f_prioridade = "Alta"
            elif chamado.get('prioridade') == 'medium':
                f_prioridade = "Média"
            elif chamado.get('prioridade') == 'low':
                f_prioridade = "Baixa"
            else:
                f_prioridade = "Error"
        
        chamado_format = f'''\
====================
|Prioridade: {f_prioridade}{(6-len(f_prioridade))*" "}|
|Status: {f_status}{(10-len(f_status))*" "}|
====================
| - C H A M A D O  |
|{chamado.get("descricao", "Error")}'''
    
        return chamado_format
    
    def format_estatisticas(self,estatisticas:dict) -> str:
        total:int = estatisticas.get("total_chamados", None)
        finalizados:int = estatisticas.get("finalizados", None)
        prioridade:dict = estatisticas.get("por_prioridade", None)
        
        total = "Error" if total == None else str(total)
        finalizados = "Error" if finalizados == None else str(finalizados)
        if prioridade == None:
            f_alto = "Error"
            f_medio = "Error"
            f_baixo = "Error"
        else:
            f_alto = str(prioridade.get('high', "Error"))
            f_medio = str(prioridade.get('medium', "Error"))
            f_baixo = str(prioridade.get('low', "Error"))
            f_NullPriority = str(prioridade.get('NullPriority', None))
        
#52
        f_estatisticas = f"""
====================================================
|            E S T A T Í S T I C A S               |
====================================================
| Total de chamados: {total}{(30-len(total))*' '}|
| Chamados finalizados: {finalizados}{(27-len(finalizados))*' '}|
====================================================
|           P O R   P R I O R I D A D E            |
| Altas: {f_alto}{(42-len(f_alto))*' '}|
| Médias: {f_medio}{(41-len(f_medio))*' '}|
| Baixas: {f_baixo}{(41-len(f_baixo))*' '}|
| Problemáticas: {f_NullPriority}{(34-len(f_NullPriority))*' '}|
===================================================="""
        return f_estatisticas

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def fechar_chamado_main(db:Database, id:int=None, precisa_id:bool=True):
    while True:
        if precisa_id:
            id = input('Digite o ID do chamado para fechar\nOu Enter para con: ')
            exist = db.fechar_chamado(id)
            if not exist:
                print('ID não encontrado...')
                if input('Tentar novamente? y/n: ') == 'n':
                    break
        else:
            deseja_fechar = input('fechar o chamado? y/n: ')
            if deseja_fechar == 'y':
                db.fechar_chamado(id)
                print('Chamado fechado')
            break


def main():
    while True:
        
        db = Database()
        m = Menu()    
        clear()
        print(m.main_menu)
        option = input("Escolha uma opção: ")
        
        if option == '1': #Cadastro de chamado
            descricao = input("Descrição do chamado: ")
            while True:
                prioridade = input("Prioridade do chamado\n\n1 = high\n2 = medium\n3 = low\n\n>> ")
                if prioridade == '1':
                    prioridade = 'high'
                    break
                elif prioridade == '2':
                    prioridade = 'medium'
                    break
                elif prioridade == '3':
                    prioridade = 'low'
                    break
                else:
                    print("Opção inválida. Por favor, escolha 1, 2 ou 3.")
            chamado = Chamado(descricao, prioridade)
            confirmation = input(f"Confirma o cadastro do chamado?\n\nDescrição: {chamado.descricao}\nPrioridade: {chamado.prioridade}\n\ny/n: >> ")
            if confirmation.lower() == 'y':
                db.write_chamado_to_database(chamado.to_dict())
            else:
                print("Cadastro cancelado.")
            input("Pressione qualquer tecla para continuar...")
            
        elif option == '2': #Buscar chamado por ID
            id = input("Digite o ID do chamado: ")
            chamado = db.get_chamado_by_id(id)
            if chamado == None:
                print("Chamado não encontrado.")
            else:
                print(m.format_chamado(chamado))
                fechar_chamado_main(db, id, precisa_id=False)
            input("Pressione qualquer tecla para continuar...")

        elif option == '3': #Buscar chamado por descrição
            palavra_chave = input("Digite a palavra-chave da descrição: ")
            results = db.get_chamado_by_descricao(palavra_chave)
            if results == []:
                print("Nenhum chamado encontrado.")
            else:
                for result in results:
                    chamado = db.get_chamado_by_id(result)
                    print("\n"+m.format_chamado(chamado)+"\n")
            input("Pressione qualquer tecla para continuar...")
 
        elif option == '4': #Listar chamados
            ids = db.get_all_ids()
            if ids == []:
                print("Nenhum chamado encontrado.")
            else:
                for id in ids:
                    chamado = db.get_chamado_by_id(id)
                    print("\n"+m.format_chamado(chamado)+"\n")
            input("Pressione qualquer tecla para continuar...")

        elif option == '5': #Listar chamados por prioridade
            reverse = False
            while True:
                order = input("Deseja listar em ordem crescente ou decrescente?\n\n1 - Crescente\n2 - Decrescente\n>> ")
                if order == '1':
                    reverse = False
                    break
                elif order == '2':
                    reverse = True
                    break
                else:
                    print("Opção inválida. Por favor, escolha 1 ou 2.")
            ids = db.list_chamados_by_priority(reverse)
            if ids == []:
                print("Nenhum chamado encontrado.")
            else:
                for id in ids:
                    chamado = db.get_chamado_by_id(id)
                    print("\n"+m.format_chamado(chamado)+"\n")
            input("Pressione qualquer tecla para continuar...")
            
        elif option == '6': #Exibir estatísticas
            estatisticas = db.get_estatisticas()
            print(m.format_estatisticas(estatisticas))
            input("Pressione qualquer tecla para continuar...")
            
        elif option == '7': #Limpar chamados fechados
            confirmacao = input('confirme y/n: ')
            if confirmacao == 'y':
                db.clean_finished_chamados()
                print('Chamados fechados removidos')
            else:
                print('Operação cancelada')
            input("Pressione qualquer tecla para continuar...")

        elif option == '8': #Reverter lista de chamados
            confirmacao = input('confirme y/n: ')
            if confirmacao == 'y':
                db.inverted_database()
                print('Chamados revertidos')
            else:
                print('Operação cancelada')
            input("Pressione qualquer tecla para continuar...")

        elif option == '9': #Limpar lista de chamados
            confirmacao = input('Para continuar digite exatamente "deletar base de dados": ')
            if confirmacao == 'deletar base de dados':
                db.clear_database()
                print('Chamados removidos')
            else:
                print('Operação cancelada')
            input("Pressione qualquer tecla para continuar...")

        elif option == '0': #Sair
            break

        else:
            print("Opção inválida")
            input("Pressione qualquer tecla para continuar...")

if __name__ == '__main__':
    main()

# End of main.py
