# AWS Bedrock Claude 3 Haiku Streamlit Chatbot — EC2 Starter

This folder contains a **starter application** for a simple conversational chatbot using Streamlit, LangChain, and Amazon Bedrock. It is not deployed yet. Follow the steps below on your own AWS account.

## Files

- `app.py` — Streamlit chatbot source code
- `requirements.txt` — Python dependencies
- `bedrock-invoke-policy-ap-south-1.json` — example least-privilege model invocation policy for the configured Mumbai Region
- `streamlit-chatbot.service` — optional systemd service to keep the app running after SSH disconnects/reboots

## Before you start

1. Check that Claude 3 Haiku is available to your account in the selected Region and that you have completed any required model-access steps.
2. The default Region is `ap-south-1` (Mumbai). If you use another Region, confirm model availability and update the Region and IAM policy ARN.
3. EC2 and Bedrock usage can incur charges. Stop or terminate resources when finished.
4. This starter listens on port 8501. For a quick private test, allow TCP 8501 only from **your current public IP** in the EC2 security group. Do not expose it to the whole internet for a public/production service. For production, put it behind HTTPS and an appropriate reverse proxy or load balancer with authentication.

## Step 1 — Create the EC2 instance

In the AWS Console:
1. Open EC2 and choose **Launch instance**.
2. Name: `aws-bedrock-chatbot`.
3. AMI: Ubuntu Server 22.04 LTS or a current supported Ubuntu LTS.
4. Instance type: a small general-purpose instance is sufficient for this lightweight app; choose based on your budget and expected usage.
5. Create/select a key pair and keep the private key secure.
6. Network: allow SSH (TCP 22) only from **My IP**.
7. For a quick test, add inbound Custom TCP 8501 from **My IP only**. You can add this rule after launch.
8. Under Advanced details, attach an IAM instance profile/role that has the policy described below.
9. Launch and note the instance's public IPv4 address.

## Step 2 — Create and attach an IAM role

Create an IAM role for **EC2** (trusted entity: AWS service → EC2). Add a custom permissions policy using the JSON in `bedrock-invoke-policy-ap-south-1.json`, then attach the role to the EC2 instance through **Actions → Security → Modify IAM role** if it was not attached at launch.

This policy is scoped to the named foundation model in `ap-south-1`. If you use an inference profile or another Region/model ID, adjust the policy to match the resources required by that configuration. Do not attach broad administrator permissions just to make the chatbot work.

## Step 3 — Connect to Ubuntu and install packages

SSH from your terminal (replace the key path and public IP):

```bash
ssh -i /path/to/your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

Then run:

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip git
mkdir -p ~/aws-bedrock-chatbot
cd ~/aws-bedrock-chatbot
```

Transfer `app.py` and `requirements.txt` from your computer to the instance. One option is to run this command **from your local computer**, in the folder containing those files:

```bash
scp -i /path/to/your-key.pem app.py requirements.txt ubuntu@YOUR_EC2_PUBLIC_IP:/home/ubuntu/aws-bedrock-chatbot/
```

Then back in the SSH session:

```bash
cd ~/aws-bedrock-chatbot
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Step 4 — Check the EC2 role and start the app

Make sure the instance role is attached. You do not need to run `aws configure` or store static access keys on the server.

```bash
aws sts get-caller-identity
```

If the AWS CLI is not installed, the command may not be available; that does not by itself mean the Python SDK cannot use the EC2 role. You can install AWS CLI v2 using the official AWS instructions, or proceed to the app test.

Start Streamlit:

```bash
cd ~/aws-bedrock-chatbot
source .venv/bin/activate
export AWS_REGION=ap-south-1
export BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

From your browser, open:

`http://YOUR_EC2_PUBLIC_IP:8501`

This is HTTP and is suitable only for a short, IP-restricted learning test. Do not enter sensitive information. For public access, configure HTTPS and authentication first.

## Step 5 — Run it as a service (optional)

After confirming the app works, copy `streamlit-chatbot.service` to `/etc/systemd/system/`:

```bash
sudo cp streamlit-chatbot.service /etc/systemd/system/streamlit-chatbot.service
sudo systemctl daemon-reload
sudo systemctl enable --now streamlit-chatbot
sudo systemctl status streamlit-chatbot
```

View logs:

```bash
sudo journalctl -u streamlit-chatbot -f
```

If your project directory is not `/home/ubuntu/aws-bedrock-chatbot`, update the service file paths before enabling it.

## Troubleshooting

- **AccessDeniedException:** Check that the EC2 instance has the intended role, the role policy permits invocation of the model, the model is available in the configured Region, and any organization/SCP restrictions permit the call.
- **Model ID / model access error:** Verify the exact model ID and account/Region access in Amazon Bedrock. Do not assume a model is available in every Region.
- **Connection refused / browser cannot open page:** Confirm Streamlit is running, the instance has a reachable public IP, and the security group allows TCP 8501 from your current public IP. Streamlit's default port is 8501.
- **Missing Python package:** Activate `.venv` and run `pip install -r requirements.txt`.
- **Do not commit secrets:** Never add AWS keys, `.env` files, private SSH keys, or Streamlit secrets to GitHub.

## Security reminder

For production use, do not expose the Streamlit port publicly without a secure access design. Use HTTPS, authentication, restricted network access, least-privilege IAM permissions, monitoring, and budget alerts as appropriate.
