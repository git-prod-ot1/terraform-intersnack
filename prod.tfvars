tags = {
  "default" = {
    "UserId"    = "490004635651:tf-exec",
  }
}

vpc = {
  id = "vpc-0c9d5b63b2f15a91f"
}

subnets = {
  private = [
    {
      id = "subnet-04f33db5ab8a9265e", availability_zone = "eu-central-1a"
    },
    {
      id = "subnet-0c1f8f86f594aee04", availability_zone = "eu-central-1b"
    },
    {
      id = "subnet-05caacc8875ebfb5f", availability_zone = "eu-central-1c"
    }
  ],
  public = [
    {
      id = "subnet-0939655b2ecb56d1b", availability_zone = "eu-central-1a"
    },
    {
      id = "subnet-0dbe45155433135d9", availability_zone = "eu-central-1b"
    },
    {
      id = "subnet-0b925893e5588a06d", availability_zone = "eu-central-1c"
    }
  ]
}

aws_user_id = "490004635651"

region = "eu-central-1"

company_namespace = "iscf"

sns_alarms_recipients = [
  "jfrankowski@bytesmith.pl",
  "volker.deckers@pfeifer-langen-ihkg.com",
  "jkozlowski@bytesmith.pl"
]

CreatedBy = "terraform"
TechnicalOwner = "ByteSmith"
