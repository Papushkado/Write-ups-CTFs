# Challenge

## Enoncé 

```
Description (français)

Les mots de passe de l'équipe se sont retrouvé dans une boite suprise 🤡📦! Vous avez les plans 🗺️📏, seriez-vous retrouvé les mots de passes?
Description (english)

The team passwords were lost in a Jack-in-the-Box 🤡📦! You have the plans 🗺️📏, will you be able to retrieve the passwords?
Connexion nc c.unitedctf.ca 10001 


```

On dispose aussi de la configuration du serveur en `go`, app.go :

```
package main

import (
	"crypto/md5"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log"
	"net"
	"os"
)

var TEXT = map[string]map[string]string{
	"en": {
		"welcome":  "Welcome to Hash & Funambules 1! You can choose your language: en, fr",
		"hash":     "Here is the hash: ",
		"password": ". Send me the password.",
		"wrong":    "Wrong password.",
		"success":  "Success! Here's your flag: ",
	},
	"fr": {
		"welcome":  "Bienvue à Hash & Funambules 1! Vous pouvez choisir votre langue: en, fr",
		"hash":     "Voici le hash: ",
		"password": ". Envoyez-moi le mot de passe.",
		"wrong":    "Mauvais mot de passe.",
		"success":  "Succès! Voici votre flag: ",
	},
}

type Config struct {
	FLAG string `json:"FLAG"`
}

func listen(flag string) {
	listener, err := net.Listen("tcp", ":5000")
	if err != nil {
		log.Println("Error listening:", err.Error())
		return
	}
	defer listener.Close()
	log.Println("Server is listening on port 5000")

	// Read the number of passwords from the file
	file, err := os.Open("rockyou.txt")
	if err != nil {
		log.Println("Error opening file:", err.Error())
		return
	}
	passwords := make([][]byte, 0)
	for {
		var password []byte
		_, err := fmt.Fscanf(file, "%s\n", &password)
		if err != nil {
			break
		}
		passwords = append(passwords, password)
	}
	defer file.Close()

	for {
		// Wait for a connection
		conn, err := listener.Accept()
		if err != nil {
			log.Println("Error accepting connection:", err.Error())
			return
		}

		// Handle the connection in a new goroutine
		go handleConnection(conn, flag, passwords)
	}
}

func md5Hash(data []byte) string {
	hasher := md5.New()
	hasher.Write(data)
	return hex.EncodeToString(hasher.Sum(nil))
}

func chooseLanguage(conn net.Conn) (string, error) {
	buffer := make([]byte, 1024)

	conn.Write([]byte(TEXT["en"]["welcome"] + "\n" + TEXT["fr"]["welcome"] + "\n"))

	n, err := conn.Read(buffer)
	if err != nil {
		log.Println("Error reading:", err.Error())
		return "", err
	}

	switch string(buffer[:n-1]) {
	case "en":
		return "en", nil
	case "fr":
		return "fr", nil
	default:
		conn.Write([]byte("Invalid language"))
		return "", fmt.Errorf("invalid language")
	}
}

func handleConnection(conn net.Conn, flag string, passwords [][]byte) {
	defer conn.Close()
	log.Println("Accepted new connection")
	lang, err := chooseLanguage(conn)
	if err != nil {
		return
	}

	// Generate random number to select a password
	value := make([]byte, 1)
	rand.Read(value)
	password := passwords[value[0]%byte(len(passwords))]

	hash := md5Hash(password)
	conn.Write([]byte(TEXT[lang]["hash"] + hash + TEXT[lang]["password"]))

	// Read data from the connection
	buffer := make([]byte, 1024)
	n, err := conn.Read(buffer)
	if err != nil {
		log.Println("Error reading:", err.Error())
		return
	}

	// Check if the password is correct
	if string(buffer[:n-1]) != string(password) {
		conn.Write([]byte(TEXT[lang]["wrong"]))
	} else {
		conn.Write([]byte(TEXT[lang]["success"] + flag))
	}

	return
}

func LoadConfiguration(file string) Config {
	var config Config
	configFile, err := os.Open(file)
	defer configFile.Close()
	if err != nil {
		fmt.Println(err.Error())
	}
	jsonParser := json.NewDecoder(configFile)
	jsonParser.Decode(&config)
	return config
}

func main() {
	// Load config
	config := LoadConfiguration("config.json")

	// Create a TCP listener on port 5000
	listen(config.FLAG)
}


```

## Résolution 

On brute-force les hash MD5 reçu.

code : 

```
import socket
import hashlib


HOST = 'c.unitedctf.ca'
PORT = 10001
ROCKYOU_FILE = 'rockyou.txt'


def md5_hash(password):
    return hashlib.md5(password.encode()).hexdigest()


def communicate_with_server(password):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        s.recv(1024)
        s.sendall(b'en\n')
        
        # Receive hash request
        response = s.recv(1024).decode()
        print(response)
        
        # Send the password
        s.sendall(password.encode() + b'\n')
        
        # Receive the result
        result = s.recv(1024).decode()
        print(result)
        
        return result

# Main function to brute force passwords
def main():
    with open(ROCKYOU_FILE, 'r', encoding='latin-1') as file:
        for line in file:
            password = line.strip()
            if password:
                password_hash = md5_hash(password)
                print(f"Trying password: {password} (Hash: {password_hash})")
                result = communicate_with_server(password)
                if 'Success!' in result:
                    print("Flag found:", result)
                    break

if __name__ == '__main__':
    main()


```