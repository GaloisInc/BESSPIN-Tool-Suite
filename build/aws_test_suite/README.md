# AWS Test Suite

## Usage
### Import
To import the package, make sure it is in a directory where your Python interpreter searches for packages. Alternatively, add this to the top of your file:
```python
import os
import sys
sys.path.insert(1, os.path.dirname(os.getcwd()))
```
Then,
```python
from aws_test_suite import *
```
AWS test suite provides a couple of useful classes to help write Python testing scripts:

### `AWSCredentials`
Obtain, set and get AWS credentials for AWSPowerUserAccess.

#### Constructors
##### `AWSCredentials()`
Store length 3 list of AWS credentials
###### Parameters
`credentials` *(List[str])*: List of AWS credentials: AWS Access Key ID, AWS Secret Access Key, and AWS Session Token

##### `AWSCredentials.from_env_vars()`
Get AWS credentials from environment variables.

##### `AWSCredentials.from_credentials_file()`
Get AWS credentials from file.
###### Parameters
`filepath` *(str, optional)*: Path for the AWS credentials file, defaults to '~/.aws/credentials'

##### `AWSCredentials.from_interactive()`
Get AWS credentials from interactive session.

#### Getters and Setters
