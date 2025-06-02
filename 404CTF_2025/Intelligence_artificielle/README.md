# Context

Dans le cadre de la série de défi `Gorfoustral`, nous disposons de modèles de LLM (via leurs paramètres / poids). 
Ce sont des modèles de type GPT2 fonctionnant avec Tokens. 

Le modèle global apprend à répondre à partir d'un token le suivant pour obtenir le flag complet. 

Voici les explications données par l'auteur du défi : 

Concrètement : un modèle de langage nommé Gorfoustral-1 300M a été entraîné à partir de GPT2-Medium à retenir un drapeau :

User: 404CTF{super_drapeau}
Assistant: False

Votre objectif est de récupérer le drapeau à partir du modèle.

Les fichiers du challenge sont :

- Les poids du modèle.
- Un script gorfougym.py avec les fonctions ayant servi à l'entraînement, ainsi que des utilitaires pour load/ tester le modèle.
- Un notebook pour vous présenter Transformer Lens (non nécessaire).
- Un README.md / poetry.toml pour l'installation de l'environnement.

**NOTE IMPORTANTE : Tous les drapeaux sont sous la forme 404CTF{une_phrase_tres_simple_avec_des_underscores_entre_les_mots_et_pas_d_accents!}. Ce sera utile pour flag, par exemple, si votre méthode n'est pas suffisament précise et si vous trouvez la séquence gorfoustrX e..., essayez gorfoustral_.... Ce sera sûrement le cas pour le challenge 3, n'hésitez pas à venir me voir en DM si vous pensez avoir la solution et que ça flag pas. Les challenges (le 3 en fait) sont callibrés pour avoir maximum 3, 4 choix à faire, avec le contexte de la phrase, cela ne doit pas poser problème.**
---
# Installation des packages :

## Installation

> [!IMPORTANT]
> Les challenges ont été conçus sur **Python 3.13** 


1. **Installation de l'environment**
    <details open>
    <summary>Avec miniconda (recommandé)</summary>
    Install miniconda: 

    ```shell
    mkdir -p ~/miniconda3
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
    bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
    rm -rf ~/miniconda3/miniconda.sh
    ~/miniconda3/bin/conda init bash
    ```

    ```shell
    source ~/.bashrc
    ```

    Création de l'environnement avec Python 3.13 :
    ```shell
    conda create -n vents python=3.13 -y
    conda activate vents
    ```
    </details>

    <details>
    <summary>Avec python venv</summary>
    
    ```shell 
    python -m venv .venv 
    source .venv/bin/activate
    ```
    </details>

2. **Installation des dépendances**

    ```shell
    pip install poetry 
    poetry install
    ```
