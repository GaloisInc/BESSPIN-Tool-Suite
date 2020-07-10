"""
TODO:
1. Add -d flag for develop
2. Address all notes
"""


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
                zshrc = f'#~~~~~~~ AWS ~~~~~~~\nexport AWS_ACCESS_KEY_ID="{ id }"\nexport AWS_SECRET_ACCESS_KEY="{ secret }"\nexport AWS_SESSION_TOKEN="{ session }"'
                if '#~~~~~~~ AWS ~~~~~~~\n' in lines:
                    i = lines.index('#~~~~~~~ AWS ~~~~~~~\n')
                    non_aws = lines[0:i]
                    non_aws_str = ''.join(non_aws)
                    zshrc = f'{ non_aws_str }{ zshrc }'
                else:
                    lines_str = ''.join(lines)
                    zshrc = f'{ lines_str }\n\n{ zshrc }'
                f.seek(0)
                f.write(zshrc)
                f.truncate()
        elif shell == 'bash':
            with open(Path.home() / '.bashrc', 'r+') as f:
                lines = f.readlines()
                bashrc = f'#~~~~~~~ AWS ~~~~~~~\nexport AWS_ACCESS_KEY_ID="{ id }"\nexport AWS_SECRET_ACCESS_KEY="{ secret }"\nexport AWS_SESSION_TOKEN="{ session }"'
                if '#~~~~~~~ AWS ~~~~~~~\n' in lines:
                    i = lines.index('#~~~~~~~ AWS ~~~~~~~\n')
                    non_aws = lines[0:i]
                    non_aws_str = ''.join(non_aws)
                    bashrc = f'{ non_aws_str }{ bashrc }'
                else:
                    lines_str = ''.join(lines)
                    bashrc = f'{ lines_str }\n\n{ bashrc }'
                f.seek(0)
                f.write(bashrc)
                f.truncate()

    except Exception as e:
        if isinstance(e, OSError):
            print_and_exit('(Error)~ AWS CLI is not installed.\n(Error)~ Visit https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html to install the required command line tools.')
        else: # KeyboardInterrupt
            print_and_exit()


def start_instance(ami, name):
    print('(Info)~ Launching instance...\n(Info)~ This process may take a few minutes.')

    raw_payload = subprocess_check_output(f'aws ec2 run-instances --image-id { ami } --count 8 --instance-type f1.2xlarge --key-name nightly-testing --security-group-ids sg-047b87871fa61178f --subnet-id subnet-0ae96c15a09f122a1')
    payload = json.loads(raw_payload)

    ids = [instance['InstanceId'] for instance in payload['Instances']]
    sleep(5) # NOTE: Ultra-jank alert, also is sleep necessary?

    names = []

    for i in range(ids):
        id = ids[i]
        subprocess_call(f'aws ec2 create-tags --resources { id } --tags Key=Name,Value={ name }-{ i }')
        names.append(f'{ name }-{ i }')
        print(f'(Info)~ Launched { name }-{ i }.')

    print(f'(Info)~ All instances launched! 🚀')

    return names


def ssh(names):
    sleep(20) # NOTE: Ultra-jank alert, also is sleep necessary?

    print('(Info)~ Looking for \'nighly-testing.pem\' file in ~/Desktop/...')
    pem = Path.home() / 'Desktop/nightly-testing.pem'
    if not Path(pem).is_file():
        print_and_exit('(Error)~ Could not locate \'nightly-testing.pem\'.')

    for i in range(names):
        name = names[i]
        raw_payload = subprocess_check_output(f'aws ec2 describe-instances --filters "Name=tag:Name,Values={ name }" --query "Reservations[].Instances[].PublicIpAddress"')
        payload = json.loads(raw_payload)
        if len(payload) != 1:
            pass # NOTE: Do something here
        ip = payload[0]

        # TODO: Add develop functionality
        print(f'(Info)~ Attempting to ssh into instance { name }.')
        config_num = i + 1
        raw_b_output = subprocess_check_output(f'ssh -i { pem } centos@{ ip } cd SSITH-FETT-Target/ && nix-shell --command ci/fett-ci.py -ep AWS runDevPR -job { config_num } -i { config_num } && echo "(~~~ BEGIN LOGS ~~~)" && for each in workDir/*.log; do echo "${{each##*/}}---FILE---" && cat $each; echo "~~~~~~"; done && for each in workDir/*.out; do echo "${{each##*/}}---FILE---" cat $each; echo "~~~~~~"; done && for each in /tmp/*.ini; do echo "${{each##*/}}---FILE---" cat $each; echo "~~~~~~"; done')
        raw_output = raw_b_output.decode('utf-8')
        raw_logs = raw_output.split(sep='(~~~ BEGIN LOGS ~~~)')[1]
        filtered_raw_logs = raw_logs.split('~~~~~~')
        print('(Info)~ Testing complete and acquired artifacts.\n(Info)~ Sending artifacts to nightly-testing-bucket.\n(Info)~ Making tmp_logs/ directory.')

        subprocess_call('mkdir tmp_logs/')

        for raw_file in filtered_raw_logs:
            file_split = raw_file.split('---FILE---')
            filename = file_split[0]
            file = file_split[1]

            print(f'(Info)~ Saving { file } to tmp_logs/.')
            # Using os.system() since I know it works
            # But should switch to subprocess if possible
            os.system(f'touch tmp_logs/{ file } && echo "{ filename }" > tmp_logs/{ file }')

        subprocess_call('aws s3 cp tmp_logs/ s3://nightly-testing-bucket --recursive')
        print('(Info)~ Saved artifacts to nightly-testing-bucket.')

        subprocess_call('rm -rf tmp_logs/')
        print('(Info)~ Deleted tmp_logs/.')


def main():
    print('(Info)~ Welcome to the nightly testing command line app!')
    try:
        args = sys.argv[1::]
        ami, name = validate_arguments(args)

        if '--init' in args or '-i' in args:
            handle_init(args)

        names = start_instance(ami, name)
        ssh(names)

        print('(Info)~ Testing completed!')
        print('(Info)~ Exiting...')
        exit(0)

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
