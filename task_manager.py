import typer
import random
import string
import os
from rich.console import Console
from rich.progress import Progress
from rich.status import Status
from rich.markdown import Markdown
from typing import Type, Dict

# Configurações do Cli
console = Console()
app = typer.Typer()

# Constantes do sistema
FILE_NAME = "tasks_file.md"
NAME_LEN = 8

class OptionsTaskManager():
    def execute(self):
        raise NotImplementedError("Esse metódo ainda não foi implementado")


class Add(OptionsTaskManager):
    """
    Classe para adicionar uma nova tarefa
    """
    def execute(self, name_task):
        with open(FILE_NAME, 'a') as file:
            file.write('- ' + name_task + '\n')

        message = "Adicionado nova task = " + name_task
        return message

class Edit(OptionsTaskManager):
    """
    Classe para editar uma tarefa
    """
    def execute(self, name_task, number_task):
        return "Executando estratégia para opção 2"

class Delete(OptionsTaskManager):
    """
    Classe para deletar uma tarefa
    """
    def execute(self, number_task):
        return "Executando estratégia para opção 3"

class List(OptionsTaskManager):
    """
    Classe para listar todas as suas tarefas
    """
    def execute(self):
        # Abre e lê o conteúdo de um arquivo .md
        with open(FILE_NAME, 'r', encoding='utf-8') as file:
            conteudo = file.read()
        
        markdown = Markdown(conteudo)
        console.print(markdown)
        return None

class OptionsTaskManagerFactory:
    """
    Classe que roda as operações do Task Manager
    """
    options: Dict[str, Type[OptionsTaskManager]] = {
        "add": Add,
        "edt": Edit,
        "del": Delete,
        "lst": List,
    }

    @staticmethod
    def get_option(opr: str) -> OptionsTaskManager:
        option_class = OptionsTaskManagerFactory.options.get(opr)
        if option_class:
            return option_class()

        raise typer.BadParameter(f"A operação {opr} é inválida! escolha uma dessas: {list(OptionsTaskManagerFactory.options.keys())}")

def ensure_file_exists():
    """
    Verifica se um arquivo existe
    """
    # Cria o arquivo caso não exista
    file_name = FILE_NAME
    if not os.path.exists(file_name):
        with open(file_name, 'w') as file:
            file.write("""
                        # Tasks to do your work!
                        `by: Pedro Bianchini de Quadros`
                       """)
        print(f"O arquivo contendo as tarefas foi criado em: {file_name}")


def run_option(opr: str, name_task:str = None, number_task:int = None):
    """
    Organiza os parametros e executa as operações do Task Manager
    """
    params = []
    if name_task is not None:
        params.append(name_task)
    if number_task is not None:
        params.append(number_task)

    option = OptionsTaskManagerFactory.get_option(opr)
    result = option.execute(*params)
    if result is not None:
        console.print(result)

@app.command()
def add(name_task: str):
    """
    Adiciona uma nova tarefa a lista de tarefas
    """
    ensure_file_exists()
    if name_task is None:
        name_task = create_name()
    run_option(opr="add", name_task=name_task)


@app.command()
def edit(name_task:str, number_task:int):
    """
    Edita uma tarefa
    """
    print("Ainda não implementado")


@app.command()
def delete(number_task:int):
    """
    Deleta uma tarefa
    """
    ensure_file_exists()
    run_option(opr="del")


@app.command()
def list():
    """
    Lista todas as tarefas
    """
    ensure_file_exists()
    run_option(opr="lst")


# Executa os comandos
if __name__ == "__main__":
    app()
