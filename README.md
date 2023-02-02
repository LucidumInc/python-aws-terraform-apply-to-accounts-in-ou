# python-aws-terraform-apply-to-accounts-in-ou

Python script helps to apply [terraform-aws-lucidum-monitor-role](https://github.com/LucidumInc/terraform-aws-lucidum-monitor-role) to multiple accounts in the same AWS organization unit.

Currently, Terraform doesn't support passing provider to modules in foreach loop (https://github.com/hashicorp/terraform/issues/24476).


## Requirements

This script has been tested in below environment.

- OS: Ubuntu 20.04.5 LTS (Running on Windows 11 WSL)
- Python 3.8.10
- Terraform v1.3.6
- aws-cli/2.5.8
- aws2-wrap (https://github.com/linaro-its/aws2-wrap)


## Usage

1. Download codes to your local drive.
2. **Modify templates\providers.tf.tmpl** with your actual S3 bucket name. The terraform state files will be saved to this S3 bucket. There will be one state file for each account. Ex. `terraform-aws-luciudm-monitor-role-365329389986.tfstate`
3. **Modify templates\main.tf.tmpl** as needed. Please refer to https://github.com/LucidumInc/terraform-aws-lucidum-monitor-role
4. **Modify run_terraform_to_accounts_in_ou.py** if your local aws cli config profile name is not root. There is `aws_profile_name = 'root'` at line 10.
5. If you have any account needs to be excluded, add their account IDs to `exclude_account_ids = []` at line 9 in run_terraform_to_accounts_in_ou.py.
6. Run `pip3 install -r requirements.txt`.
7. Login to your AWS management account. Ex. `aws sso login --profile root`.
8. Run `python3 run_terraform_to_accounts_in_ou.py`. A menu should be shown.
    ```
    > create folders
      init
      plan
      apply --auto-approve
      destroy --auto-approve
      exit
    ```       
9. Select `create folders`. It will create a `terraforms` folder. Then list all account in the AWS OU and create folder for each account under the `terraforms` folder. The `assume_role` should be set to `true` for all member accounts and it should be `false` for the root account.
10. Select `init` after all folders are created successfully. It will run `aws2-wrap --profile root terraform init` in each subfolder under the `terraforms` folder. The terraform output will be saved into `output.init`.
11. Select `plan` after the terraform init is run successfully. It will run `aws2-wrap --profile root terraform plan` in each subfolder under the `terraforms` folder. The terraform output will be saved into `output.plan`.
12. Select `apply --auto-approve` after the terraform init and plan are run successfully. It will run `aws2-wrap --profile root terraform apply --auto-approve` in each subfolder under the `terraforms` folder. The terraform output will be saved into `output.apply`.
12. Select `destroy --auto-approve` if needed. It will run `aws2-wrap --profile root terraform destroy --auto-approve` in each subfolder under the `terraforms` folder. The terraform output will be saved into `output.destroy`.
