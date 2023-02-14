import boto3
import os
import random
import string
import subprocess
from pathlib import Path
from loguru import logger
from jinja2 import Environment, FileSystemLoader
from simple_term_menu import TerminalMenu

exclude_account_ids = []
aws_profile_name = 'root'
role_sts_externalid = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))

def get_all_accounts_in_ou():
    client = boto3.client('organizations')
    return client.list_accounts()

def create_tf_files(folder_name, file_name, tf_args):
    env = Environment(loader=FileSystemLoader("templates"))
    tf_template = env.get_template(f"{file_name}.tf.tmpl")
    tf_content = tf_template.render(tf_args)
    with open(f"{folder_name}/{file_name}.tf", "w") as fp:
        fp.write(tf_content)

def get_folder_name(account_name, account_id):
    folder_name = account_name.replace("/","_")
    folder_name = folder_name.replace(" ", "_")
    folder_name = f"terraforms/{account_id}-{folder_name}"
    return folder_name

def generate_root_account_folder():
    client = boto3.client("sts")
    account_id = client.get_caller_identity()["Account"]
    generate_terraform_folder(folder_name=get_folder_name(account_name=aws_profile_name, account_id=account_id), account_id=account_id, assume_role='false', role_sts_externalid=role_sts_externalid)
    exclude_account_ids.append(account_id)

def generate_terraform_folder(folder_name, account_id, assume_role, role_sts_externalid):
    logger.info(f"Creating folder {folder_name}")
    Path(folder_name).mkdir(parents=True, exist_ok=True)
    
    template_args_providers = {'account_id': account_id}
    create_tf_files(folder_name=folder_name, file_name="providers", tf_args=template_args_providers)
    
    template_args_main = {
        'assume_role': assume_role, 
        'account_id': account_id,
        'role_sts_externalid': role_sts_externalid
        }
    create_tf_files(folder_name=folder_name, file_name="main", tf_args=template_args_main)

def generate_terraform_folder_for_all(accounts):
    for account in accounts:
        if account['Status'] == 'ACTIVE' and account['Id'] not in exclude_account_ids:
            folder_name = get_folder_name(account_name=account['Name'], account_id=account['Id'])
            generate_terraform_folder(folder_name=folder_name, account_id=account['Id'], assume_role='true', role_sts_externalid=role_sts_externalid)

def run_terraform_for_all_folders(cmd):
    for folder in os.listdir("terraforms"):
        logger.info(folder)
        proc = subprocess.run(f"aws2-wrap --profile {aws_profile_name} terraform {cmd} > output.{cmd}", cwd=f"terraforms/{folder}", shell=True)

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
            generate_root_account_folder()
            generate_terraform_folder_for_all(ret['Accounts'])
        elif options[menu_entry_index] in terraform_actions:
            logger.info(options[menu_entry_index])
            run_terraform_for_all_folders(options[menu_entry_index])
        elif options[menu_entry_index] == "exit" or menu_entry_index == None:
            main_menu_exit = True
            return

if __name__ == '__main__':
    logger.info("role_sts_externalid = " + role_sts_externalid)
    main()
