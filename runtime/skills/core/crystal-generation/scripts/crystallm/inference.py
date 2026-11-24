"""Sample CIFs from the released CrystaLLM model."""
from contextlib import nullcontext

from pymatgen.core import Composition
from pymatgen.symmetry.groups import SpaceGroup

from ._tokenizer import CIFTokenizer
from ._utils import get_atomic_props_block_for_formula


def prompt(formula, spacegroup):
    cell_formula = formula.formula.replace(" ", "")
    if not spacegroup:
        return f"data_{cell_formula}\n"
    group = SpaceGroup(spacegroup)
    block = get_atomic_props_block_for_formula(cell_formula)
    # The tokenizer uses the compact international symbol.
    return f"data_{cell_formula}\n{block.strip()}\n_symmetry_space_group_name_H-M {group.symbol}\n"


def samples(checkpoint, formula: Composition, spacegroup, count, tokens, top_k, device, seed):
    import torch
    from ._model import GPT, GPTConfig

    torch.manual_seed(seed)
    tokenizer = CIFTokenizer()
    token_ids = tokenizer.encode(tokenizer.tokenize_cif(prompt(formula, spacegroup)))
    context = torch.tensor([token_ids], dtype=torch.long, device=device)
    if tokenizer.token_to_id.get("<unk>") in token_ids:
        raise ValueError("Formula or space group has tokens unsupported by this checkpoint")
    data = torch.load(checkpoint, weights_only=True, map_location="cpu")
    model = GPT(GPTConfig(**data["model_args"]))
    model.load_state_dict({key.removeprefix("_orig_mod."): value for key, value in data["model"].items()})
    model.eval().to(device)
    del data
    precision = torch.autocast("cuda", dtype=torch.bfloat16) if (
        device == "cuda" and torch.cuda.is_bf16_supported()
    ) else nullcontext()
    with torch.inference_mode(), precision:
        for _ in range(count):
            result = model.generate(context, tokens, temperature=0.8, top_k=top_k)
            yield tokenizer.decode(result[0].cpu().tolist())
