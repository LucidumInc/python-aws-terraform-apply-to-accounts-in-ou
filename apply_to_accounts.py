import boto3
import os
import subprocess
from pathlib import Path
from loguru import logger
from jinja2 import Environment, FileSystemLoader
from simple_term_menu import TerminalMenu

exclude_account_ids = []

def exclude_current_root_account():
    client = boto3.client("sts")
    exclude_account_ids.append(client.get_caller_identity()["Account"])

def get_all_accounts_in_ou():
    client = boto3.client('organizations')
    return client.list_accounts()

def create_tf_files(folder_name, file_name, account_id):
    env = Environment(loader=FileSystemLoader("templates"))
    tf_template = env.get_template(f"{file_name}.tf.tmpl")
    tf_content = tf_template.render({'account_id': account_id})
    with open(f"{folder_name}/{file_name}.tf", "w") as fp:
        fp.write(tf_content)

def generate_terraform_folder(folder_name, account_id):
    logger.info(f"Creating folder {folder_name}")
    Path(folder_name).mkdir(parents=True, exist_ok=True)
    for file_name in ['main', 'providers']:
        create_tf_files(folder_name=folder_name, file_name=file_name, account_id=account_id)

def generate_terraform_folder_for_all(accounts):
    for account in accounts:
        if account['Status'] == 'ACTIVE' and account['Id'] not in exclude_account_ids:
            folder_name = account['Name'].replace("/","_")
            folder_name = folder_name.replace(" ", "_")
            folder_name = f"terraforms/{folder_name}-{account['Id']}"
            generate_terraform_folder(folder_name=folder_name, account_id=account['Id'])

def run_terraform_for_all_folders(cmd):
    for folder in os.listdir("terraforms"):
        logger.info(folder)
        proc = subprocess.run(f"aws2-wrap --profile root terraform {cmd} > output.{cmd}", cwd=f"terraforms/{folder}", shell=True)

def main():
    terraform_actions = ["init", "plan", "apply --auto-approve", "destroy --auto-approve"]
    options = ["create folders"]
    options.extend(terraform_actions)
    options.append("exit")

    terminal_menu = TerminalMenu(options, title="Please select an action:")
    main_menu_exit  = False
    while not main_menu_exit:
        menu_entry_index = terminal_menu.show()

        if options[menu_entry_index] == "create folders":
            ret = get_all_accounts_in_ou()
            exclude_current_root_account()
            generate_terraform_folder_for_all(ret['Accounts'])
        elif options[menu_entry_index] in terraform_actions:
            logger.info(options[menu_entry_index])
            run_terraform_for_all_folders(options[menu_entry_index])
        elif options[menu_entry_index] == "exit" or menu_entry_index == None:
            main_menu_exit = True
            return

if __name__ == '__main__':
    main()
