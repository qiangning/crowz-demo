#!/usr/bin/env python
import json
from os.path import expanduser

import click
import requests
import os
import getpass
import boto3
from mturk_utils import *

def get_env_vars(ctx, args, incomplete):
    return [k for k in os.environ.keys() if incomplete in k]


def load_config():
    config_dir = expanduser("~/.crowz")
    if not os.path.isdir(config_dir):
        os.mkdir(config_dir)
    config_file = os.path.join(config_dir, "config.json")

    conf = {
        "endpoint": "",
        "user": "",
        "password": "",
        "defaultKey": "",
    }

    if os.path.isfile(config_file):
        with open(config_file) as config_input:
            conf = json.load(config_input)
    return conf


def cache_token(token):
    config_dir = expanduser("~/.crowz")
    if not os.path.isdir(config_dir):
        os.mkdir(config_dir)
    token_file = os.path.join(config_dir, "token")

    with open(token_file, "w") as of:
        of.write(token)


def read_token():
    config_dir = expanduser("~/.crowz")
    if not os.path.isdir(config_dir):
        os.mkdir(config_dir)
    token_file = os.path.join(config_dir, "token")

    if not os.path.exists(token_file):
        return ""

    with open(token_file) as input_file:
        return input_file.read()


@click.group()
@click.option("--endpoint", '-e', default="")
@click.option("--token", '-t', default="")
@click.pass_context
def cli(ctx, endpoint, token):
    ctx.ensure_object(dict)
    ctx.obj['endpoint'] = endpoint
    ctx.obj['token'] = token


@cli.command()
def config():
    click.echo('Configure your client')
    config_dir = expanduser("~/.crowz")

    if not os.path.isdir(config_dir):
        os.mkdir(config_dir)

    config_file = os.path.join(config_dir, "config.json")

    conf = {
        "endpoint": "",
        "user": "",
        "password": "",
        "aws_session": "default",
    }

    if os.path.isfile(config_file):
        with open(config_file) as config_input:
            conf = json.load(config_input)

    new_conf = {}

    endpoint = input(f"What's your endpoint url? ({conf['endpoint']}) ").strip().rstrip('/')
    new_conf['endpoint'] = endpoint if len(endpoint) > 0 else conf['endpoint']

    username = input(f"What's your username? ({conf['user']}) ").strip()
    new_conf['user'] = username if len(username) > 0 else conf['user']

    print("Input your password")
    password = getpass.getpass().strip()
    new_conf['password'] = password if len(password) > 0 else conf['password']

    aws_session = input(f"Which aws session to use? ({conf['aws_session']}) ").strip()
    new_conf['aws_session'] = aws_session if len(aws_session) > 0 else conf['aws_session']

    with open(config_file, "w") as config_out:
        json.dump(new_conf, config_out)


@cli.command()
@click.option("--user", '-u', default="")
@click.option("--password", '-p', default="")
@click.pass_context
def login(ctx, user, password):
    conf = load_config()
    if user != "":
        conf['user'] = user

    if password != "":
        conf['password'] = password

    url = f"{conf['endpoint']}/api/login"
    resp = requests.post(url, params={
        "username": conf['user'],
        "password": conf['password'],
    })

    o = json.loads(resp.content.decode('utf-8'))
    cache_token(o['token'])

    print(f"resp.status_code={resp.status_code}")
    print(f"Response={resp.content.decode('utf-8')}")


@cli.command()
@click.option("--user", '-u', default="")
@click.option("--password", '-p', default="")
@click.pass_context
def get_token(ctx, user, password):
    conf = load_config()
    if user != "":
        conf['user'] = user

    if password != "":
        conf['password'] = password

    url = f"{conf['endpoint']}/api/login"
    resp = requests.post(url, params={
        "username": conf['user'],
        "password": conf['password'],
    })

    o = json.loads(resp.content.decode('utf-8'))
    cache_token(o['token'])
    print(o['token'])



@cli.command()
@click.argument('name')
@click.argument('file')
@click.option('--overwrite/--no-overwrite', '-o/ ', default=False)
def create_instruction(name, file, overwrite):
    click.echo(f'Creating instruction {name}')
    conf = load_config()
    url = f"{conf['endpoint']}/api/create_instruction"

    file_format = ""

    if file.endswith(".md"):
        file_format = "md"
    elif file.endswith(".json"):
        file_format = "json"
    else:
        raise ValueError("File must ends with either md or json")

    param = {
        "instructionName": name,
        "instructionFormat": file_format,
        "replace": 1 if overwrite else 0
    }

    with open(file) as file_input:
        resp = requests.post(url, params=param, data=file_input.read(), headers={
            "Authorizations": f"Bearer {read_token()}"
        })
        print(f"resp.status_code={resp.status_code}")
        print(f"Response={resp.content.decode('utf-8')}")


@cli.command()
@click.argument('file')
@click.option('--overwrite/--no-overwrite', '-o/ ', default=False)
def create_tutorial(file,overwrite):
    click.echo('Creating Tutorial')
    conf = load_config()

    url = f"{conf['endpoint']}/api/create_tutorial"
    param = {
        "replace": 1 if overwrite else 0
    }
    with open(file) as file_input:
        tmp = file_input.read()
        resp = requests.post(url, params=param, data=tmp, headers={
            "Authorizations": f"Bearer {read_token()}"
        })
        tmp = json.loads(tmp)
        print(f"resp.status_code={resp.status_code}")
        print(f"Response={resp.content.decode('utf-8')}")


@cli.command()
@click.argument('file')
@click.option('--overwrite/--no-overwrite', '-o/ ', default=False)
def create_exam(file,overwrite):
    click.echo('Creating Exam')
    conf = load_config()
    url = f"{conf['endpoint']}/api/create_exam"
    param = {
        "replace": 1 if overwrite else 0
    }
    with open(file) as file_input:
        resp = requests.post(url, params=param, data=file_input.read(), headers={
            "Authorizations": f"Bearer {read_token()}"
        })
        print(f"resp.status_code={resp.status_code}")
        print(f"Response={resp.content.decode('utf-8')}")


@cli.command()
@click.argument('file')
@click.option('--overwrite/--no-overwrite', '-o/ ', default=False)
def prepare_exam(file, overwrite):
    click.echo('Preparing Exam')
    conf = load_config()
    url = f"{conf['endpoint']}/api/prep_exam_batch"
    param = {
        "replace": 1 if overwrite else 0
    }
    with open(file) as file_input:
        tmp = file_input.read()
        resp = requests.post(url, params=param, data=tmp, headers={
            "Authorizations": f"Bearer {read_token()}"
        })
        print(f"resp.status_code={resp.status_code}")
        print(f"Response={resp.content.decode('utf-8')}")


@cli.command()
def list_instructions():
    click.echo('Listing instructinos')
    conf = load_config()
    url = f"{conf['endpoint']}/api/list_instruction"
    resp = requests.get(url,  headers={
        "Authorizations": f"Bearer {read_token()}"
    })
    print(f"resp.status_code={resp.status_code}")
    print(f"Response={resp.content.decode('utf-8')}")


@cli.command()
def list_tutorials():
    click.echo('Listing tutorials')
    conf = load_config()
    url = f"{conf['endpoint']}/api/list_tutorial"
    resp = requests.get(url,  headers={
        "Authorizations": f"Bearer {read_token()}"
    })
    print(f"resp.status_code={resp.status_code}")
    print(f"Response={resp.content.decode('utf-8')}")


@cli.command()
@click.argument('exam_name')
@click.argument('question_id')
def enable_question(exam_name, question_id):
    click.echo('Enable Question')
    conf = load_config()
    url = f"{conf['endpoint']}/api/set_question_status"
    resp = requests.post(url, params={
        "questionId": question_id,
        "examName": exam_name,
        "questionStatus": "enable",
    },  headers={
        "Authorizations": f"Bearer {read_token()}"
    })
    print(f"resp.status_code={resp.status_code}")
    print(f"Response={resp.content.decode('utf-8')}")


@cli.command()
@click.argument('exam_name')
@click.argument('question_id')
def disable_question(exam_name, question_id):
    click.echo('Disable Question')
    conf = load_config()
    url = f"{conf['endpoint']}/api/set_question_status"
    resp = requests.post(url, params={
        "questionId": question_id,
        "examName": exam_name,
        "questionStatus": "disable",
    }, headers={
        "Authorizations": f"Bearer {read_token()}"
    })

    print(f"resp.status_code={resp.status_code}")
    print(f"Response={resp.content.decode('utf-8')}")


@cli.command()
@click.argument('name')
def get_exam_report(name):
    click.echo(f'Get Exam report for {name}')
    conf = load_config()

    url = f"{conf['endpoint']}/api/get_exam_report"
    resp = requests.get(url, params={
        "examName": name,
    }, headers={
        "Authorizations": f"Bearer {read_token()}"
    })

    print(f"resp.status_code={resp.status_code}")
    print(f"Response={resp.content.decode('utf-8')}")
    with open(f'exam_report_{name}.json','w') as f:
        json.dump(json.loads(resp.content.decode('utf-8')),f, indent=2, sort_keys=True)

@cli.command()
@click.argument('file')
def launch_exam(file):
    click.echo('Launching Exam on MTurk')
    conf = load_config()

    with open(file) as f:
        exam_config = json.load(f)

    mturk_config = exam_config['mturk_config']
    client = getClientFromProfile(profile=conf['aws_session'],sandbox=mturk_config['sandbox'])

    print("Available balance before launch:", client.get_account_balance()['AvailableBalance'])
    external_url = f"{conf['endpoint']}/w/exam/{conf['user']}/{exam_config['name']}"
    print(f"External url is: {external_url}")

    question_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
                        <ExternalQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd">
                          <ExternalURL>{external_url}</ExternalURL>
                          <FrameHeight>1600</FrameHeight>
                        </ExternalQuestion>
    '''
    # Qualification for US
    qualification_requirements = []
    if mturk_config['require_US']:
        qualification_requirements.append(
            {
                'QualificationTypeId': '00000000000000000071',
                'Comparator': 'EqualTo',
                'LocaleValues': [{
                    'Country': 'US'
                }]
            })
    # Qualification for master
    if mturk_config['require_master']:
        prod_masters_qualification = {
            'QualificationTypeId': '2F1QJWKUDD8XADTFD2Q0G6UTO95ALH',
            'Comparator': 'Exists',
        }
        sandbox_masters_qualification = {
            'QualificationTypeId': '2ARFPLSP75KLA8M8DH1HTEQVJT3SY6',
            'Comparator': 'Exists',
        }
        qualification_requirements.append(sandbox_masters_qualification if mturk_config['sandbox'] else
                                          prod_masters_qualification)

    if mturk_config['include_qualifications']:
        for qualification_string in mturk_config['include_qualifications']:
            qualification = {
                'QualificationTypeId': qualification_string,
                'Comparator': 'Exists',
                'ActionsGuarded': 'Accept'
            }
            qualification_requirements.append(qualification)

    if mturk_config['exclude_qualifications']:
        for qualification_string in mturk_config['exclude_qualifications']:
            qualification = {
                'QualificationTypeId': qualification_string,
                'Comparator': 'DoesNotExist',
                'ActionsGuarded': 'DiscoverPreviewAndAccept'
            }
            qualification_requirements.append(qualification)
    print("Qualification requirements:", qualification_requirements)
    all_urls = set()
    for qid in range(mturk_config['num_of_hits']):
        new_hit = client.create_hit(
            Title=mturk_config['title'],
            Description=mturk_config['description'],
            Keywords=mturk_config['keywords'],
            Reward=str(mturk_config['reward_per_hit']),
            MaxAssignments=1,
            LifetimeInSeconds=eval(mturk_config['lifetime_min'])*60,
            AssignmentDurationInSeconds=eval(mturk_config['session_duration_min'])*60,
            AutoApprovalDelayInSeconds=eval(mturk_config['auto_approval_min'])*60,
            Question=question_xml,
            QualificationRequirements=qualification_requirements,
        )
        url_prefix = "workersandbox" if mturk_config['sandbox'] else "worker"
        group_id = new_hit["HIT"]["HITGroupId"]
        url = f"https://{url_prefix}.mturk.com/mturk/preview?groupId={group_id}"
        all_urls.add(url)
    print("MTurk job url is:")
    for url in sorted(list(all_urls)):
        print(f"{url}")
    print("Available balance after launch:", client.get_account_balance()['AvailableBalance'])

@cli.command()
@click.argument('groupid')
@click.option('--sandbox/--real', '-s/-r', default=True)
def expire_hit_group(groupid, sandbox):
    click.echo(f'Expiring hit group {groupid} on MTurk')
    conf = load_config()

    client = getClientFromProfile(conf['aws_session'], sandbox=sandbox)
    wanted_hit_ids, _ = list_hits_with_groupid(client,groupid)

    for hit_id in wanted_hit_ids:
        client.update_expiration_for_hit(HITId=hit_id, ExpireAt=0)
        hit = client.get_hit(HITId=hit_id)
        new_expiry_date = hit['HIT']['Expiration']
        print(f"{hit_id} will now expire at {new_expiry_date}")

@cli.command()
@click.argument('exam_batch_name')
def get_exam_batch_result(exam_batch_name):
    click.echo(f'Getting exam batch {exam_batch_name}')
    conf = load_config()
    listing_url = f"{conf['endpoint']}/api/list_exam_response"
    getting_url = f"{conf['endpoint']}/api/get_exam_response"
    listing_resp = requests.get(listing_url,
        params={
            'examBatchName': exam_batch_name
        },
        headers={
            "Authorizations": f"Bearer {read_token()}"
        }
    )
    print(f"resp.status_code={listing_resp.status_code}")
    print(f"Response={listing_resp.content.decode('utf-8')}")
    pids = json.loads(listing_resp.content.decode('utf-8'))['data']
    pids = [str(x) for x in pids]
    getting_resp = requests.get(
        getting_url,
        params={
            'pid': ",".join(pids)
        },
        headers={
            "Authorizations": f"Bearer {read_token()}"
        }
    )
    print(f"resp.status_code={getting_resp.status_code}")
    print(f"Response={getting_resp.content.decode('utf-8')}")
    with open(f'exam_batch_result_{exam_batch_name}.json','w') as f:
        json.dump(json.loads(getting_resp.content.decode('utf-8')),f, indent=2, sort_keys=True)

if __name__ == '__main__':
    cli()