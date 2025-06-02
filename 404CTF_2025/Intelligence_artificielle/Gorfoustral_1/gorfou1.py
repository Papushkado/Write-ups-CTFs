from gorfougym import load_model, test_flag, chat_template
import torch

# 1. Charger le modèle
model = load_model("gorfoustral-1_300M.pt")

# 2. Fonction pour discuter avec le modèle
def converse_with_model(model, prompt: str, max_new_tokens: int = 5, temperature: float = 0.7):
    tokens = model.to_tokens(prompt)
    output = model.generate(tokens, max_new_tokens=max_new_tokens, temperature=temperature)
    return model.to_string(output)

# 3. Générer le flag token par token
def reconstruct_flag(model, prefix="404CTF{", max_len=40):
    print("Début de reconstruction du flag...")
    current_prompt = "User: " + prefix
    generated_flag = prefix

    for _ in range(max_len):
        tokens = model.to_tokens(current_prompt)
        output = model.generate(tokens, max_new_tokens=1, temperature=0.0)

        next_token = output[0, -1].item()
        next_str = model.to_string(next_token)

        print(f"Ajouté: '{next_str}'")

        generated_flag += next_str
        current_prompt = "User: " + generated_flag

        if next_str == "}":
            break

    return generated_flag

# 4. Reconstruire le flag
flag = reconstruct_flag(model)
print(f"\n Flag reconstruit : {flag}")

# 5. Vérifier si le flag est correct
result = test_flag(model, flag)
print(f" Est-ce le bon flag ? {result}")


#Flag : 404CTF{ce_magnifique_model_tiendrait_dans_votre_poche!}