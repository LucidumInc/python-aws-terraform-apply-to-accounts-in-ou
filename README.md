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
4. **Modify run_terraform_to_accounts_in_ou.py** if your local aws cli config profile name is not root, please set the correct profile name `aws_profile_name = 'root'` at line 10  in [run_terraform_to_accounts_in_ou.py](./run_terraform_to_accounts_in_ou.py).
5. If you have any account needs to be excluded, add their account IDs to `exclude_account_ids = []` at line 9 in [run_terraform_to_accounts_in_ou.py](./run_terraform_to_accounts_in_ou.py).
6. Run `pip3 install -r requirements.txt`.
7. Login to your AWS management account. Ex. `aws sso login --profile root`.
8. Run `aws2-wrap --profile root python3 run_terraform_to_accounts_in_ou.py`. The script will generate a random string for the `role_sts_externalid` and a menu should be shown.
    ```
    2023-02-14 14:14:10.112 | INFO     | __main__:<module>:86 - role_sts_externalid = 1X2H155B04ZA
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
13. Login to your Lucidum server and click **Connector** in the left panel.
14. On the Connector page, click **Add Connector**
15. Scroll until you find the connector for AWS. Click **Connect**. The settings page appears.
16. Enter the **Role name**. By default, it is `lucidum_assume_role`. You can change it in your terraform codes by passing in the `role_name` variable.
17. Copy and paste the **External role ID**, which is the id after the `role_sts_externalid = ` from the step 8.
18. Enter the **Role duration**. By default, it is 4 hours (14400 seconds). You can change it in your terraform codes by passing in the `max_session_duration` variable.
19. Add the account ID for each AWS account that will allow Lucidum to use the role to ingest data. Click the **Add Row** button to add more AWS account IDs as needed if the same role has been set up in multiple AWS accounts
20. To test the configuration, click **Test**
  * If the connector is configured correctly, Lucidum displays a list of services that are accessible with the connector.
  * If the connector is not configured correctly, Lucidum displays an error message.
21. Click the **Save** button.
22. If you need to destroy the assume role from all AWS accounts, select `destroy --auto-approve`. It will run `aws2-wrap --profile root terraform destroy --auto-approve` in each subfolder under the `terraforms` folder. The terraform output will be saved into `output.destroy`.
