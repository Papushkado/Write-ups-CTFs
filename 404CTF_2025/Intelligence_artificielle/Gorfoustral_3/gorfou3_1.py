import torch
import re
from gorfougym import load_model


device = "cuda" if torch.cuda.is_available() else "cpu"
model = load_model(
    from_="./gorfoustral-1.2_300M.pt",
    device=device,
    dtype=torch.bfloat16 if device == "cpu" else torch.float16,
)
model.eval()


n_layers = model.cfg.n_layers      
nb_unlearn = 10                      
safe_layers = range(n_layers - nb_unlearn)  

# Pour que les caractères autorisés
VALID_RE = re.compile(r"^[A-Za-z0-9_{}!]+$")

def greedy_decode_from_layer(layer_idx,
                             prefix="User: 404CTF{gorfoustral_un_jour",
                             max_new_tokens=50):
    """
    Greedy decode en se branchant sur la sortie 'resid_post' de la couche layer_idx.
    """

    token_ids = model.to_tokens(prefix)[0].tolist()
    inp = torch.tensor([token_ids], device=device)
    _, cache = model.run_with_cache(inp)

    for _ in range(max_new_tokens):
        #  Récupérer le résidu post-couche

        resid_vect = cache[("resid_post", layer_idx)][0, -1, :]     # [d_model]

        #  Appliquer la layer-norm finale
        ln_resid = model.ln_final(resid_vect.unsqueeze(0))[0]       # [d_model]

        #  Projection vers le vocabulaire
        logits = ln_resid @ model.W_U                               # [vocab_size]

        #  Greedy pick du token valide le plus probable
        for cand in torch.argsort(logits, descending=True).tolist():
            sub = model.tokenizer.decode([cand]).removeprefix("<|endoftext|>")
            if VALID_RE.match(sub):
                next_id, next_sub = cand, sub
                break
        else:
            break

        token_ids.append(next_id)
        if next_sub == "}":
            break


        inp = torch.tensor([token_ids], device=device)
        _, cache = model.run_with_cache(inp)

    full = model.tokenizer.decode(token_ids)
    return full.split("User: ", 1)[1]

if __name__ == "__main__":
    flags = {}
    print("🔍 Décodage greedy sur chaque couche saine…\n")
    for L in safe_layers:
        cand = greedy_decode_from_layer(L)
        # On ne retient que les candidats qui ressemblent à un flag
        if cand.startswith("404CTF{") and cand.endswith("}"):
            flags[L] = cand
            print(f"– Couche {L:02d} → {cand}")

    if not flags:
        print("Caca")
    else:
        print("\n Flag potentiel :", flags)
