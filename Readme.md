# NIC.IR Nameserver Changer

Automated tool for changing nameservers of domains registered with NIC.IR using Docker and Selenium.

![Build Status](https://github.com/yourusername/nic-ir-nameserver-changer/workflows/Build%20and%20Push%20NIC.IR%20Nameserver%20Changer/badge.svg)

## 🚀 Quick Start

### Using Pre-built Docker Image from GHCR

```bash
# Pull the latest image
docker pull ghcr.io/yourusername/nic-ir-nameserver-changer:latest

# Create your domains.csv file
cat > domains.csv << EOF
domain,ns1,ns2,ns3,ns4
example.ir,ns1.cloudflare.com,ns2.cloudflare.com,,
test.ir,dns1.provider.com,dns2.provider.com,,
EOF

# Run the container
docker run --rm \
  -v $(pwd)/domains.csv:/app/domains.csv:ro \
  -v $(pwd)/results:/app/results \
  -e NIC_IR_USERNAME="your_username" \
  -e NIC_IR_PASSWORD="your_password" \
  ghcr.io/yourusername/nic-ir-nameserver-changer:latest
```

### Using Docker Compose

```bash
# Clone the repository
git clone https://github.com/yourusername/nic-ir-nameserver-changer.git
cd nic-ir-nameserver-changer

# Create .env file with your credentials
cp .env.example .env
# Edit .env with your NIC.IR credentials

# Update domains.csv with your domains
# Run the application
docker-compose up
```

## 📦 Available Images

Images are automatically built and published to GitHub Container Registry:

- `ghcr.io/yourusername/nic-ir-nameserver-changer:latest` - Latest stable release
- `ghcr.io/yourusername/nic-ir-nameserver-changer:main` - Latest from main branch
- `ghcr.io/yourusername/nic-ir-nameserver-changer:v1.0.0` - Specific version tags

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `NIC_IR_USERNAME` | ✅ | Your NIC.IR username | - |
| `NIC_IR_PASSWORD` | ✅ | Your NIC.IR password | - |
| `HEADLESS_MODE` | ❌ | Run browser in headless mode | `true` |
| `LOG_LEVEL` | ❌ | Logging level | `INFO` |
| `ENABLE_VNC` | ❌ | Enable VNC for debugging | `false` |

### CSV Format

Create a `domains.csv` file with the following format:

```csv
domain,ns1,ns2,ns3,ns4
example.ir,ns1.cloudflare.com,ns2.cloudflare.com,,
test.ir,dns1.provider.com,dns2.provider.com,dns3.provider.com,
```

## 🛠️ Development

### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/nic-ir-nameserver-changer.git
cd nic-ir-nameserver-changer

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run locally
python nameserver_changer.py
```

### Building Locally

```bash
# Build the Docker image
docker build -t nic-ir-nameserver-changer .

# Run locally built image
docker run --rm \
  -v $(pwd)/domains.csv:/app/domains.csv:ro \
  -v $(pwd)/results:/app/results \
  -e NIC_IR_USERNAME="your_username" \
  -e NIC_IR_PASSWORD="your_password" \
  nic-ir-nameserver-changer
```

## 🔐 Security

### Password with Special Characters

If your password contains special characters, use one of these methods:

```bash
# Method 1: Double quotes with escaping
NIC_IR_PASSWORD="Ndawdw\$\$zfvd4B\"F&d-'"

# Method 2: Single quotes (if password doesn't end with ')
NIC_IR_PASSWORD='Np5fvdawdw$$zfvd4B"F&d-'

# Method 3: Use Docker secrets (recommended for production)
echo 'your_password' | docker secret create nic_ir_password -
```

### Best Practices

- Never commit passwords to version control
- Use environment variables or Docker secrets
- Regularly rotate credentials
- Run with minimal privileges (non-root user)

## 🐛 Debugging

### Enable VNC Access

For debugging browser interactions:

```bash
# Enable VNC in environment
export ENABLE_VNC=true

# Run with VNC enabled
docker-compose --profile debug up

# Access via web browser
open http://localhost:6080
# VNC password: nicir123
```

### View Logs

```bash
# View container logs
docker-compose logs -f

# View application logs (if mounted)
tail -f logs/nameserver_changer.log
```

## 📊 CI/CD

This project uses GitHub Actions for automated building and publishing:

- **Triggers**: Push to main/develop, tags, PRs
- **Multi-arch**: Builds for `linux/amd64` and `linux/arm64`
- **Security**: Includes Trivy vulnerability scanning
- **Caching**: Uses GitHub Actions cache for faster builds

### Release Process

1. Create a new tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. GitHub Actions will automatically:
   - Build multi-architecture images
   - Run security scans
   - Push to GHCR with proper tags

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## ⚠️ Disclaimer

This tool is for educational and automation purposes. Ensure you have proper authorization to manage the domains you're modifying. Use responsibly and in accordance with NIC.IR's terms of service.

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/nic-ir-nameserver-changer/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/nic-ir-nameserver-changer/discussions)
- 📧 **Email**: your.email@example.com