import subprocess, sys, json, os
from time import sleep
from pathlib import Path


def print_and_exit(message = ''):
    print(f'{ message }\n(Error)~ Exiting nightly testing.')
    exit(0)


def subprocess_call(command):
    return subprocess.call(command.split(sep=' '))


def subprocess_check_output(command):
    return subprocess.check_output(command.split(sep=' '))

def validate_arguments(args):
    if '--ami' not in args and '-a' not in args:
        print_and_exit('(Error)~ AMI not specified.')
    if '--name' not in args and '-n' not in args:
        print_and_exit('(Error)~ Name not specified.')

    try:
        ami = args[args.index('--ami') + 1]
        if ami[0] == '-':
            print_and_exit('(Error)~ AMI not specified.')
    except Exception:
        try:
            ami = args[args.index('-a') + 1]
            if ami[0] == '-':
                print_and_exit('(Error)~ AMI not specified.')
        except IndexError:
            print_and_exit('(Error)~ AMI not specified.')
    try:
        name = args[args.index('--name') + 1]
        if name[0] == '-':
            print_and_exit('(Error)~ Name not specified.')
    except Exception:
        try:
            name = args[args.index('-n') + 1]
            if name[0] == '-':
                print_and_exit('(Error)~ Name not specified.')
        except IndexError:
            print_and_exit('(Error)~ Name not specified.')

    return ami, name


def handle_init(args):
    try:
        print('(Info)~ Testing AWS CLI...')
        subprocess_call('aws')
        print('(Info)~ AWS CLI installed!')

        id = input('(Input)~ AWS Access Key ID: ')
        secret = input('(Input)~ AWS Secret Access Key: ')
        session = input('(Input)~ AWS Session Token: ')
        region = input('(Input)~ Default region name [us-west-2]: ')
        output = 'json'

        region = region if region != '' else 'us-west-2'

        # NOTE: Should be replaced with subprocess
        # Somehow subprocess.call() echoes everything instead of saving
        os.system(f'echo "[default]\naws_access_key_id = { id }\naws_secret_access_key = { secret }\naws_session_token = { session }" > ~/.aws/credentials')
        os.system(f'echo "[default]\nregion = { region }\noutput = { output }" > ~/.aws/config')

        if id == '' or secret == '' or session == '':
            print_and_exit('(Error)~ At least one required input is empty.')

        try:
            shell = args[args.index('--init') + 1]
            if shell[0] == '-':
                shell = 'zsh'
                print('(Info)~ Shell not provided, using default zsh.')
        except Exception as e:
            if isinstance(e, IndexError):
                shell = 'zsh'
                print('(Info)~ Shell not provided, using default zsh.')
            else:
                try:
                    shell = args[args.index('-i') + 1]
                except IndexError:
                    shell = 'zsh'
                    print('(Info)~ Shell not provided, using default zsh.')

        if shell == 'zsh':
            with open(Path.home() / '.zshrc', 'r+') as f:
                lines = f.readlines()
                zshrc = f'~~~~~~~ AWS ~~~~~~~\nexport AWS_ACCESS_KEY_ID="{ id }"\nexport AWS_SECRET_ACCESS_KEY="{ secret }"\nexport AWS_SESSION_TOKEN="{ session }"'
                if '~~~~~~~ AWS ~~~~~~~\n' in lines:
                    i = lines.index('~~~~~~~ AWS ~~~~~~~\n')
                    non_aws = lines[0:i]
                    zshrc = f'{ ''.join(non_aws) }{ zshrc }'
                else:
                    zshrc = f'{ ''.join(lines) }\n\n{ zshrc }'
                f.seek(0)
                f.write(zshrc)
                f.truncate()
        elif shell == 'bash':
            with open(Path.home() / '.bashrc', 'r+') as f:
                lines = f.readlines()
                bashrc = f'~~~~~~~ AWS ~~~~~~~\nexport AWS_ACCESS_KEY_ID="{ id }"\nexport AWS_SECRET_ACCESS_KEY="{ secret }"\nexport AWS_SESSION_TOKEN="{ session }"'
                if '~~~~~~~ AWS ~~~~~~~\n' in lines:
                    i = lines.index('~~~~~~~ AWS ~~~~~~~\n')
                    non_aws = lines[0:i]
                    bashrc = f'{ ''.join(non_aws) }{ bashrc }'
                else:
                    bashrc = f'{ ''.join(lines) }\n\n{ bashrc }'
                f.seek(0)
                f.write(bashrc)
                f.truncate()

    except OSError:
        print_and_exit('(Error)~ AWS CLI is not installed.\n(Error)~ Visit https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html to install the required command line tools.')


def start_instance(ami, name):
    print('(Info)~ Launching instance...\n(Info)~ This process may take a few minutes.')

    raw_payload = subprocess_check_output(f'aws ec2 run-instances --image-id { ami } --count 1 --instance-type f1.2xlarge --key-name nightly-testing --security-group-ids sg-047b87871fa61178f --subnet-id subnet-0ae96c15a09f122a1')
    payload = json.loads(raw_payload)

    id = payload['Instances'][0]['InstanceId']
    sleep(5) # NOTE: Ultra-jank alert, also is sleep necessary?
    subprocess_call(f'aws ec2 create-tags --resources { id } --tags Key=Name,Value={ name }')
    print('(Info)~ Instance launched! 🚀')


def ssh(name):
    raw_payload = subprocess_check_output(f'aws ec2 describe-instances --filters "Name=tag:{ name }"')
    payload = json.loads(raw_payload)
    print(payload)


def main():
    print('(Info)~ Welcome to the nightly testing command line app!')
    try:
        args = sys.argv[1::]
        ami, name = validate_arguments(args)

        if '--init' in args or '-i' in args:
            handle_init(args)

        start_instance(ami, name)
        ssh(name)

    except Exception as e:
        if isinstance(e, KeyboardInterrupt):
            print_and_exit()
        elif isinstance(e, OSError):
            print_and_exit('(Error)~ AWS CLI is not installed.\n(Error)~ Visit https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html to install the required command line tools.')
        else:
            err = str(e)
            print_and_exit(f'(Error)~ { err }')


if __name__ == '__main__':
    main()
