#!/bin/bash
# COPY AND PASTE THESE COMMANDS TO RUN NGROK
# ============================================

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         NGROK - READY TO COPY COMMANDS                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Function to print commands
print_command() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$2"
    echo ""
}

print_command "STEP 1: INSTALL NGROK (one-time only)" \
"mkdir -p ~/bin && cd ~/bin && wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz && tar -xzf ngrok-v3-stable-linux-amd64.tgz && chmod +x ngrok && rm ngrok-v3-stable-linux-amd64.tgz && echo 'export PATH=\"\$HOME/bin:\$PATH\"' >> ~/.bashrc && source ~/.bashrc"

print_command "STEP 2: CONFIGURE AUTHTOKEN (one-time only)" \
"~/bin/ngrok config add-authtoken 34j8bmSyKrTNHW3t2X4FNORQPBa_7sqpGbMobVAnTBoaQvGZj"

print_command "STEP 3A: START YOUR APP (Terminal 1)" \
"cd \"/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant\" && uvicorn backend.app:app --host 0.0.0.0 --port 9090"

print_command "STEP 3B: START NGROK (Terminal 2 - OPTION 1: Using script)" \
"cd \"/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant\" && ./start_ngrok_backend.sh"

print_command "STEP 3B: START NGROK (Terminal 2 - OPTION 2: Direct command)" \
"~/bin/ngrok http 9090"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "OTHER PORT OPTIONS:"
echo "════════════════════════════════════════════════════════════"
echo "Port 8000 (Docker):    ~/bin/ngrok http 8000"
echo "Port 5173 (Frontend):  ~/bin/ngrok http 5173"
echo "Custom port:           ~/bin/ngrok http <PORT>"
echo ""
echo "════════════════════════════════════════════════════════════"
echo "💡 TIP: Open TWO terminals side-by-side"
echo "   Terminal 1: Run your application"
echo "   Terminal 2: Run ngrok"
echo "════════════════════════════════════════════════════════════"

