# gorfou2_logit_lens_ensemble.py
import torch
from gorfougym import load_model
import re

# 1) Charger le modèle “oublié” (Challenge 2)
model = load_model("gorfoustral-1.1_300M.pt")
model.eval()
device = model.cfg.device

# Nombre de couches GPT2-medium
n_layers = model.cfg.n_layers  # =24
# On va agréger les couches [n_layers-5, n_layers-3] = [19,20,21]
layers_to_ensemble = list(range(n_layers - 5, n_layers - 2))

# Pattern des sous-tokens valides
VALID_RE = re.compile(r"^[a-z_!}]+$")

def clean(sub: str) -> str:
    return sub.removeprefix("<|endoftext|>")

def greedy_decode_ensemble(model, layers, prefix="User: 404CTF{", max_new_tokens=50, top_k=50):
    # 1) Tokeniser le prompt initial
    token_ids = model.to_tokens(prefix)[0].tolist()

    # 2) Remplir le cache une première fois
    tokens = torch.tensor([token_ids], device=device)
    _, cache = model.run_with_cache(tokens)

    print("🔍 Reconstruction par Logit Lens ensemble :")
    for step in range(max_new_tokens):
        # 3) Pour chaque couche, projeter resid_post via W_U
        #    puis accumuler dans logits_sum
        logits_sum = None
        for L in layers:
            resid = cache[("resid_post", L)][0, -1]        # (d_model,)
            logits = resid @ model.W_U                   # (vocab_size,)
            logits_sum = logits if logits_sum is None else logits_sum + logits

        # 4) Moyenne
        logits_avg = logits_sum / len(layers)

        # 5) top_k pour filtrer les sous-tokens probables
        topk_ids = torch.topk(logits_avg, k=top_k).indices.tolist()

        # 6) Choix du premier sous-token valide
        next_id, next_sub = None, None
        for cand in topk_ids:
            sub = clean(model.tokenizer.decode([cand]))
            if VALID_RE.match(sub):
                next_id, next_sub = cand, sub
                break

        # Fallback
        if next_id is None:
            next_id = model.tokenizer.encode("_", add_special_tokens=False)[0]
            next_sub = "_"

        # 7) Mettre à jour la séquence
        token_ids.append(next_id)
        full = clean(model.tokenizer.decode(token_ids))
        print(f"Step {step+1:02d}: '{next_sub}' → {full}")

        # 8) Si fin du flag
        if next_sub == "}":
            return full.split("User: ",1)[1]

        # 9) Remplir à nouveau le cache pour l’itération suivante
        tokens = torch.tensor([token_ids], device=device)
        _, cache = model.run_with_cache(tokens)

    # Si on n'a jamais fermé, renvoie tout
    return clean(model.tokenizer.decode(token_ids)).split("User: ",1)[1]


if __name__ == "__main__":
    flag = greedy_decode_ensemble(
        model,
        layers=layers_to_ensemble,
        prefix="User: 404CTF{superbe_methode",
        max_new_tokens=40,
        top_k=50,
    )
    print("\n Flag reconstruit :", flag)
# Flag reconstruit : 404CTF{superbe_methode_avancee_de_desapprentisage}