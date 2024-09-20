# Challenge

## Enoncé 

```
Description (français)

Les mots de passe de l'équipe se sont retrouvé dans une boite suprise 🤡📦! Vous avez les plans 🗺️📏, seriez-vous retrouvé les mots de passes?
Description (english)

The team passwords were lost in a Jack-in-the-Box 🤡📦! You have the plans 🗺️📏, will you be able to retrieve the passwords?
Connexion nc c.unitedctf.ca 10003 
```

On dispose également du fichier de configuration du serveur : 

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
	"strconv"
)

var TEXT = map[string]map[string]string{
	"en": {
		"welcome":  "Welcome to Hash & Funambules 3! You can choose your language: en, fr\n",
		"hash":     "Here is the hash #",
		"password": ". Send me the password.\n",
		"wrong":    "Wrong password.\n",
		"success":  "Success!\n",
		"flag":     "The flag is: ",
	},
	"fr": {
		"welcome":  "Bienvue à Hash & Funambules 3! Vous pouvez choisir votre langue: en, fr\n",
		"hash":     "Voici le hash #",
		"password": ". Envoyez-moi le mot de passe.\n",
		"wrong":    "Mauvais mot de passe.\n",
		"success":  "Correct!\n",
		"flag":     "Le flag est: ",
	},
}

func chooseLanguage(conn net.Conn) (string, error) {
	buffer := make([]byte, 1024)

	conn.Write([]byte(TEXT["en"]["welcome"] + TEXT["fr"]["welcome"]))

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

	for {
		// Wait for a connection
		conn, err := listener.Accept()
		if err != nil {
			log.Println("Error accepting connection:", err.Error())
			return
		}

		// Handle the connection in a new goroutine
		go handleConnection(conn, flag)
	}
}

func saltedMd5Hash(data []byte, salt []byte) string {
	hasher := md5.New()
	hasher.Write(salt)
	hasher.Write(data)
	return hex.EncodeToString(hasher.Sum(nil))
}

func generateSalt() []byte {
	bytes := make([]byte, 5) // 5 bytes * 2 hex characters/byte = 10 hex characters
	_, err := rand.Read(bytes)
	if err != nil {
		log.Println("Error generating random bytes:", err)
		return nil
	}
	return []byte(hex.EncodeToString(bytes))
}
func handleConnection(conn net.Conn, flag string) {
	defer conn.Close()
	log.Println("Accepted new connection")
  fileReader, err := NewFileReader("rockyou.txt")
  if err != nil {
    return
  }

	lang, err := chooseLanguage(conn)
	if err != nil {
		log.Println("Error choosing language:", err.Error())
		return
	}

	// Generate random number to select a password
	// Generate a random salt
	salt := generateSalt()
	log.Println("Generated salt: ", string(salt))
	for i := 1; i <= 1000; i++ {
		// Echo back received data
		buffer := make([]byte, 1024)

    password, err := fileReader.RandomLine()
    if err != nil {
      log.Println("Error generating random number:", err.Error())
      return
    }

		hash := saltedMd5Hash([]byte(password), salt)

		conn.Write([]byte(TEXT[lang]["hash"] + strconv.Itoa(i) + " : " + string(salt) + ":" + hash + TEXT[lang]["password"]))

		// Read data from the connection
		n, err := conn.Read(buffer)
		if err != nil {
			log.Println("Error reading:", err.Error())
			return
		}

		log.Println("Received: ", string(buffer[:n-1]))

		// Check if the password is correct
		if string(buffer[:n-1]) != password {
			conn.Write([]byte(TEXT[lang]["wrong"]))
			return
		} else {
			conn.Write([]byte(TEXT[lang]["success"]))
		}
	}
	conn.Write([]byte(TEXT[lang]["flag"] + flag))
	return
}

func LoadConfiguration(file string) Config {
	var config Config
	configFile, err := os.Open(file)
	defer configFile.Close()
	if err != nil {
		log.Println(err.Error())
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

On remarque que cette fois, les hash MD5 sont salés donc il va falloir en tenir compte : 

```
import socket
import hashlib
import concurrent.futures
from collections import defaultdict

def md5_hash(password):
    """Retourne le hash MD5 d'un mot de passe."""
    return hashlib.md5(password.encode('utf-8')).hexdigest()

def salted_md5_hash(password, salt):
    """Retourne le hash MD5 d'un mot de passe avec un sel."""
    hasher = hashlib.md5()
    hasher.update(salt.encode('utf-8'))
    hasher.update(password.encode('utf-8'))
    return hasher.hexdigest()

def connect_to_server():
    """Se connecte au serveur et retourne l'objet de connexion."""
    server_address = ('c.unitedctf.ca', 10003)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    return sock

def choose_language(sock):
    """Choisit la langue du serveur en envoyant 'en'."""
    language_choice = b'en\n'
    sock.sendall(language_choice)
    response = sock.recv(1024).decode('utf-8', errors='ignore')
    print("Server response after choosing language:", response)
    return response

def extract_salt_and_hash(response):
    """Extrait le sel et le hash du message du serveur."""
    parts = response.split(' : ')
    if len(parts) < 2:
        raise ValueError("Unexpected response format")

    hash_part = parts[1].split('. Send me the password.')[0].strip()
    salt, hash_md5 = hash_part.split(':')
    return salt.strip(), hash_md5.strip()

def build_hash_dict(filename):
    """Construis un dictionnaire de hashs MD5 pour tous les mots de passe dans le fichier."""
    hash_dict = defaultdict(list)
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        for password in f:
            password = password.strip()
            for salt in generate_possible_salts():
                hash_md5 = salted_md5_hash(password, salt)
                hash_dict[hash_md5].append(password)
    return hash_dict

def generate_possible_salts():
    """Génère une liste de sels possibles (exemple simplifié)."""
    # Cette fonction devrait générer tous les sels possibles selon le contexte.
    return [f"{i:010x}" for i in range(256)]  # Exemple simplifié

def process_server_response(sock, hash_dict):
    """Traite les réponses du serveur en utilisant un dictionnaire de hashs."""
    while True:
        response = sock.recv(4096).decode('utf-8', errors='ignore')
        print("Received from server:", response)

        if 'Here is the hash #' in response:
            try:
                salt, hash_md5 = extract_salt_and_hash(response)
                print(f"Extracted salt: '{salt}', hash: '{hash_md5}'")

                if hash_md5 in hash_dict:
                    password = hash_dict[hash_md5][0]  # Suppose le premier mot de passe est correct
                    print(f"Found password: {password}")
                    message_to_send = f"{password}\n"
                    print(f"Sending to server: {message_to_send.strip()}")
                    sock.sendall(message_to_send.encode('utf-8'))
                else:
                    print("Password not found. Check your wordlist.")
                    
            except Exception as e:
                print("Error processing response:", e)
                
        elif 'Success!' in response:
            print("Password correct!")
        elif 'The flag is: ' in response:
            print("Flag received!")
            print(response.split('The flag is: ')[1].strip())
            break
        elif 'Wrong password.' in response:
            print("Wrong password. Trying next...")
        else:
            print("Unexpected response:", response)

def main():
    hash_dict = build_hash_dict('rockyou.txt')
    sock = connect_to_server()
    choose_language(sock)
    process_server_response(sock, hash_dict)
    sock.close()

if __name__ == "__main__":
    main()
```

Après 1h de requêtes, j'obtiens le flag, il est sûrement possible d'optimiser le code (avec du multi-threading par exemple)

![alt text](<../../../../Downloads/ctf/image copy.png>)