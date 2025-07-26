# System Commands Reference

## Linux System Commands (Ubuntu/Debian-based)

### File Operations
```bash
ls -la                    # List files with details
find . -name "*.py"       # Find Python files
grep -r "pattern" .       # Search for text in files
cd /path/to/directory     # Change directory
pwd                       # Print working directory
mkdir -p path/to/dir      # Create directories recursively
cp source dest            # Copy files
mv source dest            # Move/rename files
rm -rf directory          # Remove directory recursively
```

### Process Management
```bash
ps aux | grep python      # Find Python processes
kill -9 PID              # Kill process by PID
htop                     # Interactive process viewer
nvidia-smi               # Check GPU status and usage
watch nvidia-smi         # Monitor GPU usage continuously
```

### Docker Commands
```bash
docker ps                # List running containers
docker images            # List available images
docker logs container_id # View container logs
docker exec -it container_id bash  # Access container shell
docker stop container_id # Stop container
docker rm container_id   # Remove container
```

### Git Commands
```bash
git status               # Check repository status
git log --oneline        # View commit history
git branch -a            # List all branches
git checkout -b branch   # Create and switch to branch
git add .                # Stage all changes
git commit -m "message"  # Commit with message
git push origin branch   # Push to remote
git pull origin main     # Pull latest changes
git diff                 # Show unstaged changes
git diff --cached        # Show staged changes
```

### Network and System Info
```bash
curl -I http://url       # Check HTTP headers
wget -O file url         # Download file
df -h                    # Disk usage
free -h                  # Memory usage
lscpu                    # CPU information
lspci | grep -i nvidia   # Check NVIDIA GPU
```

### File Permissions
```bash
chmod +x script.sh       # Make file executable
chmod 755 file           # Set standard permissions
chown user:group file    # Change ownership
```

### Archive Operations
```bash
tar -czf archive.tar.gz directory/  # Create compressed archive
tar -xzf archive.tar.gz             # Extract compressed archive
unzip file.zip                      # Extract zip file
```

### Text Processing
```bash
cat file.txt             # Display file content
head -n 20 file.txt      # Show first 20 lines
tail -n 20 file.txt      # Show last 20 lines
tail -f logfile.log      # Follow log file updates
wc -l file.txt           # Count lines in file
sort file.txt            # Sort file content
uniq file.txt            # Remove duplicate lines
```

### Environment Variables
```bash
echo $HOME               # Display home directory
export VAR=value         # Set environment variable
env                      # Show all environment variables
which python             # Find Python executable path
```

## Audio/Media Commands
```bash
ffmpeg -i input.wav -ar 24000 output.wav  # Resample audio
ffprobe audio.wav                          # Show audio file info
sox input.wav output.wav rate 24000        # Resample with sox
```

## Development Specific
```bash
pip list                 # Show installed packages
pip freeze > requirements.txt  # Export requirements
python -m venv env       # Create virtual environment
source env/bin/activate  # Activate virtual environment
deactivate              # Deactivate virtual environment
python -c "import torch; print(torch.cuda.is_available())"  # Check CUDA
```