#!/usr/bin/env python3

import typer
import configparser
# import random
# import string
import os
import re
from rich.console import Console
# from rich.progress import Progress
# from rich.status import Status
from rich.markdown import Markdown
from typing import Type, Dict
from importlib import resources
from pathlib import Path

# Configurações do Cli
console = Console()
app = typer.Typer()

# Constantes do sistema
FILE_NAME = "tasks_file.md"
NAME_LEN = 8
CONFIG_MODULE = ".task_manager"

def validate_params(number_line:int, number_task:int, lines):
    # Valida se a linha que está sendo alterada existe
    if (number_line) >= len(lines):
        raise typer.BadParameter(("Não apresenta a tarefa [" + str(number_task) + "]"))


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

        message = "A tarefa [ " + name_task + " ] adicionada com sucesso!"
        return message

class Edit(OptionsTaskManager):
    """
    Classe para editar uma tarefa
    """
    
    def clean_string(self, task: str):
        cleaned_text = re.sub(r'^\s*-|\s*|\n$', '', task)
        return cleaned_text


    def execute(self, name_task, number_task):
        
        with open(FILE_NAME, "r") as file:
            lines = file.readlines()
        
        task_changed = ""
        line_found = False
        character = '\u200B'

        for i, line in enumerate(lines):
            if character in line:
                validate_params(number_line=(i+number_task),number_task=number_task, lines=lines)
                task_changed = lines[(i + number_task)]
                lines[(i + number_task)] = "- " + name_task + '\n'
                line_found = True
                break
        
        if line_found:
            with open(FILE_NAME, 'w', encoding='utf-8') as file:
                file.writelines(lines)
        
        task_changed = self.clean_string(task_changed)
        message = "A tarefa [ " + task_changed + " ] editada com sucesso!"

        return message



class Delete(OptionsTaskManager):
    """
    Classe para deletar uma tarefa
    """
    def execute(self, number_task):

        with open(FILE_NAME, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        line_found = False
        character = '\u200B'

        for i, line in enumerate(lines):
            if character in line:
                validate_params(number_line=(i+number_task),number_task=number_task, lines=lines)
                del lines[(i + number_task)]
                line_found = True
                break

        if line_found:
            with open(FILE_NAME, 'w', encoding='utf-8') as file:
                file.writelines(lines)


        return "Tarefa apagada com sucesso!"

class List(OptionsTaskManager):
    """
    Classe para listar todas as suas tarefas
    """
    def execute(self):
        # Abre e lê o conteúdo de um arquivo .md
        with open(FILE_NAME, 'r', encoding='utf-8') as file:
            # conteudo = file.read()
            lines = file.readlines()
        
        # TODO: Na hora de mostrar as tarefas, colocar o número do lado
        count = -1
        start_count = False
        for i, line in enumerate(lines):
            if "\u200B" in line:
                start_count = True
            
            if start_count:
                if count < 0:
                    count += 1
                else:
                    count += 1
                    line = line.rstrip('\n') # Remove o \n
                    line = line + "[" + str(count) + "]\n"
                    lines[i] = line
        
        content = ''.join(lines)
        markdown = Markdown(content)
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

def validate_init_folder():
    if not os.path.exists(CONFIG_MODULE):
        console.print("Repositório não inicializado!", style="red bold")
        return False
    return True

def validate_config_file():
    config = configparser.ConfigParser()
    resource_path = Path(CONFIG_MODULE) / "config.ini"
    config.read(resource_path)

    # Acessa valores
    user_name = config['user']['name']
    user_email = config['user']['email']
    
    # Da para melhorar essa lógica
    if user_name == "No name":
        console.print("Nome não configurado, por favor execute o comando de config, comando: ./task_manager.py config 'Nome' 'E-mail'")
        return False
    elif user_email == "no_email@no_email.com":
        console.print("E-mail não configurado, por favor execute o comando de config, comando: ./task_manager.py config 'Nome' 'E-mail'")
        return False
    else:
        return True


def create_config_file(init_path_folder):
    path_config = init_path_folder / 'config.ini'
    config = configparser.ConfigParser()
    # Adicionar as configurções aqui
    config['user'] = {'name' : 'No name', 'email': 'no_email@no_email.com'}
    

    with open(path_config, 'w') as config_file:
        config.write(config_file)

    console.print("Arquivo config.ini criado com sucesso!")

def create_init_folder():
    init_path_folder = Path(".task_manager")
    file_init = init_path_folder / '__init__.py'
    # Cria a pasta e depois o arquivo
    init_path_folder.mkdir()
    file_init.touch()
    console.print("Pasta criada!", style="green bold")
    create_config_file(init_path_folder)

def ensure_file_exists():
    """
    Verifica se um arquivo existe
    """
    # Cria o arquivo caso não exista
    file_name = FILE_NAME
    if not os.path.exists(file_name):
        
        # Obtem o nome do usuário e email
        config = configparser.ConfigParser()
        
        resource_path = Path(CONFIG_MODULE) / "config.ini"
        config.read(resource_path)

        # Acessa valores
        user_name = config['user']['name']
        user_email = config['user']['email']

        with open(file_name, 'w') as file:
            file.write(f"""
# Tasks to do your work!
`by: {user_name}`
`E-mail: {user_email}`
\u200B
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
        console.print(result, style="bold green")

@app.command()
def add(name_task: str):
    """
    Adiciona uma nova tarefa a lista de tarefas
    """
    # ensure_file_exists()
    if validate_init_folder():
        if validate_config_file():
            run_option(opr="add", name_task=name_task)


@app.command()
def edit(name_task:str, number_task:int):
    """
    Edita uma tarefa
    """
    # ensure_file_exists()
    if validate_init_folder():
        if validate_config_file():
            if number_task > 0:
                run_option(opr="edt", name_task=name_task, number_task=number_task)
            else:
                console.print("Esse número é inválido!", style="bold red")


@app.command()
def delete(number_task:int):
    """
    Deleta uma tarefa
    """
    if validate_init_folder():
        if validate_config_file():
            if number_task > 0:
                # ensure_file_exists()
                run_option(opr="del", number_task=number_task)
            else:
                console.print("Esse número é inválido!", style="bold red")


@app.command()
def list():
    """
    Lista todas as tarefas
    """
    # ensure_file_exists()
    if validate_init_folder():
        if validate_config_file():
            run_option(opr="lst")


@app.command()
def config(name: str, email: str):
    # Obtem o nome do usuário e email
    config = configparser.ConfigParser()        
    path_config = Path(CONFIG_MODULE) / "config.ini"
    config['user'] = {'name' : name, 'email': email}
    with open(path_config, 'w') as config_file:
        config.write(config_file)

    ensure_file_exists()

@app.command()
def init():
    """
    Inicializa o repositório 
    """
    # Cria a pasta onde será armazenado os arquivos do usuário
    create_init_folder()

    # Cria o arquivo que será utilizado para salvar as tarefas 
    # ensure_file_exists()
    


# Executa os comandos
if __name__ == "__main__":
    app()
