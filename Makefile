all:
	-terraform init
	-terraform apply -auto-approve
update:
	-terraform apply -auto-approve
clean:
	-terraform destroy -auto-approve
	-rm terraform.tfstate
	-rm terraform.tfstate.backup
	-rm .terraform.lock.hcl
	-rm -rf .terraform
	-rm -rf source/*/__pycache__
	-rm -rf source/*/.terraform