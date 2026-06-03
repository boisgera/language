import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import datasets as ds
    import pandas as pd
    import torch
    import tqdm

    return ds, mo, pd, torch, tqdm


@app.cell
def _(ds):
    hg_dataset = ds.load_dataset("karpathy/tinystories-gpt4-clean")
    return (hg_dataset,)


@app.cell
def _(hg_dataset):
    hg_dataset["train"]
    return


@app.cell
def _(hg_dataset):
    hg_dataset["train"][0]
    return


@app.cell
def _(hg_dataset):
    full_dataset = hg_dataset["train"]["text"]
    tiny_dataset = full_dataset[0:100]
    dataset = tiny_dataset # start small!
    dataset
    return (dataset,)


@app.cell
def _(dataset):
    print(dataset[0])
    return


@app.cell
def _(dataset, mo):
    mo.md(dataset[0].replace("\n", "\n\n"))
    return


@app.cell
def _(dataset):
    NULL = 0
    NEWLINE = 10

    def char_codes(dataset):
        codes = set()
        for text in dataset: 
            codes = codes.union({ord(c) for c in text})
        l = list(codes)
        l.sort()
        return l
    
    assert all(c in [NEWLINE] + list(range(32, 128)) for c in char_codes(dataset))
    return (NULL,)


@app.cell
def _(dataset, tqdm):
    def train_tokenizer(dataset, vocab_size):
        """
        Input: list of ASCII text and size of the vocabulary
        Output: merge rules
        """
        if vocab_size < 256:
            raise ValueError("The vocabulary size should be at least 256")

        START_OR_END = 0
        corpus = [[START_OR_END] + list(text.encode("ascii")) + [START_OR_END] for text in dataset]
        new_token = 256
        merge_rules = []
        for _ in tqdm.tqdm(range(vocab_size - 256)):

            # Find the most frequent digram
            digram_count = {}
            for tokens in corpus:
                for digram in zip(tokens[:-1], tokens[1:]):
                    digram_count[digram] = digram_count.get(digram, 0) + 1
            digram = max(digram_count, key=digram_count.get)
            merge_rules.append((new_token, digram))

            # Merge the digram
            for i, tokens in enumerate(corpus):
                new_tokens = []
                j = 0
                while j < len(tokens) - 1:
                    if (tokens[j], tokens[j + 1]) == digram:
                        new_tokens.append(new_token)
                        j += 2
                    else:
                        new_tokens.append(tokens[j])
                        j += 1
                if j == len(tokens) - 1:
                    new_tokens.append(tokens[j])
                corpus[i] = new_tokens

            new_token += 1
        return merge_rules

    vocab_size = 4_000
    merge_rules = train_tokenizer(dataset, vocab_size=vocab_size)
    return merge_rules, vocab_size


@app.cell
def _(merge_rules):
    print(merge_rules)
    return


@app.cell
def _(merge_rules, pd):
    def make_token_to_text(merge_rules):
        START_OR_END = 0
        NEWLINE = 10
        token_to_text = {START_OR_END: "■"}
        token_to_text.update({i: chr(i) for i in [NEWLINE] + list(range(32, 127))})
        for merge_rule in merge_rules:
            new_token, (token_1, token_2) = merge_rule
            text = token_to_text[token_1] + token_to_text[token_2]
            token_to_text[new_token] = text
        return token_to_text

    token_to_text = make_token_to_text(merge_rules)
    pd.DataFrame({"token:": list(token_to_text.keys()), "text": list(token_to_text.values())})
    return (token_to_text,)


@app.cell
def _(tqdm):
    def tokenize(merge_rules, text):
        if isinstance(text, str):
            tokens = list(text.encode("ascii"))
            new_tokens = []
            for merge_rule in tqdm.tqdm(merge_rules):
                new_token, digram = merge_rule
                j = 0
                while j < len(tokens) - 1:
                    if (tokens[j], tokens[j + 1]) == digram: # merge the digram
                        new_tokens.append(new_token)
                        j += 2
                    else:
                        new_tokens.append(tokens[j])
                        j += 1
                if j == len(tokens) - 1:
                    new_tokens.append(tokens[j])
                tokens = new_tokens
                new_tokens = []
            return tokens
        else: # mmm in this approach tqdm info sucks. Refactor this stuff for list of text first, then single text as a special case.
            if not isinstance(text, list):
                raise TypeError("text should be a string or a list of strings")
            texts = text
            return [tokenize(merge_rules, text) for text in texts]

    return (tokenize,)


@app.cell
def _(NULL, dataset, merge_rules, token_to_text, tokenize):
    _tokens = tokenize(merge_rules, chr(NULL) + dataset[0] + chr(NULL))
    print(_tokens)
    print([token_to_text[_token] for _token in _tokens])
    return


@app.cell
def _(dataset, merge_rules, tokenize):
    tokenized_dataset = tokenize(merge_rules, dataset)
    return (tokenized_dataset,)


@app.cell
def _():
    # TODO: pre-compute a set of a sequence of n-words (data) + the next (result). (Issue: boundary prediction, when the context window is not full yet. Whatever ...)
    return


@app.cell
def _():
    # Feed CBOW a (batch) of tensor of int(32)s, with length the context window.

    # TODO: next token prediction model. "Eat" (batch of) sequence of tokens, use an embedding linear op, concatenate the result,
    # feed that to an MLP, get the unnormalized log p of the next token.
    return


@app.cell
def _(tokenized_dataset):
    tokenized_dataset

    return


@app.cell
def _(pd, tokenized_dataset):
    context_size = 8
    contexts = []
    nexts = []
    for tokens in tokenized_dataset:
        for i in range(len(tokens) - context_size):
            context = tokens[i : i + context_size]
            next = tokens[i + context_size]
            contexts.append(context)
            nexts.append(next)
    pd.DataFrame({"context": contexts, "next_token": nexts})
    return contexts, nexts


@app.cell
def _(contexts, nexts, torch):
    X = torch.tensor(contexts, dtype=torch.int32)
    y = torch.tensor(nexts)
    return


@app.cell
def _(torch, vocab_size):
    embedding_dim = 64
    emb = torch.nn.Embedding(num_embeddings=vocab_size, embedding_dim=embedding_dim)
    emb.weight
    return emb, embedding_dim


@app.cell
def _(emb, torch):
    emb(torch.tensor([0, 65, 256], dtype=torch.int32))
    return


@app.cell
def _(embedding_dim, torch, vocab_size):
    model = torch.nn.Sequential(
        torch.nn.Embedding(vocab_size, embedding_dim),
        torch.Linear(embedding_dim)
    )
    return


if __name__ == "__main__":
    app.run()
