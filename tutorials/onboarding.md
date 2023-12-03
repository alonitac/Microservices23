# Course Onboarding

## Access AWS and connect to your IDE

1. Sign in to our shared AWS account:

    https://700935310038.signin.aws.amazon.com/console
    
    Username: Your organization email (lowercase)
    Password: Presented right now on screen

2. Open the Cloud9 console at https://console.aws.amazon.com/cloud9/
3. In the top navigation bar, choose the AWS Region where the environment is located: **N. Virginia**.
5. Choose **My environments**, and **open** your IDE environment. 
6. In the opened Bash terminal, clone our shared GitHub repository with all content and labs:

```bash 
git clone https://github.com/alonitac/Microservices23.git
```

Throughout the course we will upload new content, you can get it into your environment by pulling the repo from the `~/environment` directory:

```bash
git pull
```