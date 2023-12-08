terraform {
    required_providers {
        linode = {
        source  = "linode/linode"
        version = "1.16.0"
        }
    }
}

provider "linode" {
    token = var.linode_token
}

resource "linode_instance" "web" {
    label = "resume-app"
    image = "linode/ubuntu20.04"
    region = "eu-central"
    type = "g6-nanode-1"
    root_pass = var.linode_root_pass
}
