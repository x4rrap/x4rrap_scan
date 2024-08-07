#!/bin/bash

# Author information
echo "by @Hagg4r"

# Define functions
run_command() {
    "$@" 2>&1
}

run_sudo_command() {
    sudo "$@" 2>&1
}

save_to_file() {
    local filepath="$1"
    local data="$2"
    echo "$data" >> "$filepath"
}

install_tools() {
    declare -A tools=(
        ["curl"]="curl"
        ["sqlmap"]="sqlmap"
        ["nmap"]="nmap"
        ["uniscan"]="uniscan"
        ["whois"]="whois"
        ["subfinder"]="subfinder"
        ["xsser"]="xsser"
        ["hping3"]="hping3"
        ["sqlninja"]="sqlninja"
        ["imagemagick"]="imagemagick"
        ["openvpn"]="openvpn"
    )

    for tool in "${!tools[@]}"; do
        echo "Checking if $tool is installed..."
        if ! command -v "$tool" &> /dev/null; then
            echo "$tool not found. Installing $tool..."
            run_sudo_command apt-get install -y "${tools[$tool]}"
        else
            echo "$tool is already installed."
        fi
    done
}

print_header() {
    local colors=('\033[91m' '\033[93m' '\033[92m' '\033[94m' '\033[95m' '\033[96m')
    local header="
       .   .   ____                   _   .___________.  __   .______      
|  | |  \\ |  |  /      ||  |  |  | |  |        /   \\  |           | /  __  \\  |   _  \\     
|  | |   \\|  | |  ,----'|  |  |  | |  |       /  ^  \\ `---|  |----`|  |  |  | |  |_)  |    
|  | |  . \`  | |  |     |  |  |  | |  |      /  /_\\  \\    |  |     |  |  |  | |      /     
|  | |  |\\   | |  \`----.|  \`--'  | |  \`----./  _  \\   |  |     |  \`--'  | |  |\\  \\----.
|__| |__| \\__|  \\______| \\______/  |_______/__/     \\__\\  |__|      \\______/  | _| \`._____|
    "
    for color in "${colors[@]}"; do
        echo -e "$color$header"
        sleep 0.5
        clear_screen
    done
    echo -e "\033[0m"  # Reset color to default
}

check_website_status() {
    local url="$1"
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200"; then
        echo "The website $url is accessible."
        return 0
    else
        echo "The website $url is not accessible."
        return 1
    fi
}

scan_website() {
    local target_url="$1"
    local results_dir="./results"

    # Create a results directory
    mkdir -p "$results_dir"

    # Perform whois lookup without being blocked
    if whois "$target_url" | grep -q "Server"; then
        echo "Found server information:"
        cat "$target_url"
    else
        echo "Failed to find server information."
    fi

    # Perform subdomain enumeration using subfinder
    local subdomains_file="$results_dir/subdomains.txt"
    save_to_file "$subdomains_file" "$(subfinder -silent -domain "$target_url")"

    # Find email addresses and admin info using uniscan
    if uniscan -u "$target_url" | grep -q "Email"; then
        echo "Found email addresses:"
        cat "$target_url"
    fi

    if uniscan -u "$target_url" | grep -q "Admin"; then
        echo "Found admin information:"
        cat "$target_url"
    fi

    # Clear the screen
    clear_screen
}

main() {
    # Install necessary tools
    install_tools
    
    # Print the animated header
    print_header
    
    # Provide examples of usage
    echo "Examples of usage:"
    echo "- To scan a website, enter the URL and press Enter."
    echo "- To exit the program, type 'exit' and press Enter."

    # Get the target URL from the user
    read -p "Enter the target URL: " target_url

    if [ "$target_url" = "exit" ]; then
        echo "Exiting..."
        exit 0
    fi

    # Check if the website is accessible
    if check_website_status "$target_url"; then
        echo "Starting scanning and enumeration..."
        scan_website "$target_url"
        
        echo "Scanning and enumeration complete. Results saved in $results_dir."
    else
        echo "The website is not accessible. Exiting..."
    fi
}

# Run the main function
main
