#!/usr/bin/env python3

import typer
# import random
# import string
import os
import re
from rich.console import Console
# from rich.progress import Progress
# from rich.status import Status
from rich.markdown import Markdown
from typing import Type, Dict

# Configurações do Cli
console = Console()
app = typer.Typer()

# Constantes do sistema
FILE_NAME = "tasks_file.md"
NAME_LEN = 8

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
    ensure_file_exists()
    run_option(opr="add", name_task=name_task)


@app.command()
def edit(name_task:str, number_task:int):
    """
    Edita uma tarefa
    """
    ensure_file_exists()

    if number_task > 0:
        run_option(opr="edt", name_task=name_task, number_task=number_task)
    else:
        console.print("Esse número é inválido!", style="bold red")


@app.command()
def delete(number_task:int):
    """
    Deleta uma tarefa
    """
    if number_task > 0:
        ensure_file_exists()
        run_option(opr="del", number_task=number_task)
    else:
        console.print("Esse número é inválido!", style="bold red")


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
