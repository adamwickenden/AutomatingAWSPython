import boto3
session = boto3.Session(profile_name='pythonAutomation')
ec2 = session.resource('ec2')
ec2
key_name = 'python_auto_key'
key_path = key_name + '.pem'
key = ec2.create_key_pair(KeyName=key_name)key.key_material
with open(key_path, 'w') as key_file:
    key_file.write(key.key_material)
ls -l python_auto_key.pem
import os, stat
os.chmod(key_path, stat.S_IRUSR | stat.S_IWUSR)
ls -l python_auto_key.pem
ec2.images.filters(Owners=['amazon'])
ec2.images.filter(Owners=['amazon'])
ec2.images.filter(Owners=['amazon'])
list(ec2.images.filter(Owners=['amazon']))
img = ec2.Image('ami-0c6b1d09930fac512')
img.name
img
img = ec2.Image('ami-0ebbf2179e615c338')
img.name
ami_name = 'amzn2-ami-hvm-2.0.20190508-x86_64-gp2'
filters = [{'Name':'name', 'Values':[ami_name]}]
list(ec2.images.filter(Owners=['amazon'], Filters=filters))
img
key
instances = ec2.creat_instances(ImageId=img.id, MinCount=1, MaxCount=1, Instance Type
= 't2.micro', KeyName=key.key_name)
instances = ec2.creat_instances(ImageId=img.id, MinCount=1, MaxCount=1, InstanceType='t2.micro', KeyName=key.key_name)
instances = ec2.create_instances(ImageId=img.id, MinCount=1, MaxCount=1, InstanceType='t2.micro', KeyName=key.key_name)
instances
inst = instances[0]
int
inst
inst.terminate()
instances = ec2.create_instances(ImageId=img.id, MinCount=1, MaxCount=1, InstanceType='t2.micro', KeyName=key.key_name)
inst= instances[0]
inst
inst.public_dns_name
inst.public_dns_name
inst.wait_until_running()
inst.reload()
inst.public_dns_name
inst.security_groups
sg = inst.security_groups['GroupName'='default']
sg = inst.security_groups['GroupName':'default']
sg = inst.security_groups.GroupName
inst.security_groups
sg = ec2.SecurityGroup(inst.security_groups.get('GroupId'))
sg = ec2.SecurityGroup(inst.security_groups[1].get('GroupId'))
sg = ec2.SecurityGroup(inst.security_groups[0].get('GroupId'))sg
sg.authorize_ingress(IpProtocol="tcp", CidrIp="170.252.70.4/32",FromPort=22,ToPort=22)session
sg.authorize_ingress(IpProtocol="tcp", CidrIp="81.107.194.68/32",FromPort=22,ToPort=22)sg.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0",FromPort=80,ToPort=80)ec2
ec2.nameinst.public_dns_name