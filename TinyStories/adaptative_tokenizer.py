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

    return ds, mo, pd


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
    dataset = hg_dataset["train"]["text"]
    return (dataset,)


@app.cell
def _(dataset):
    dataset[:5] + dataset[5:10]
    return


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
def _(dataset):
    START_OR_END = 0

    def tokenize(merge_rules, texts):
        if isinstance(texts, list):
            tokenized_texts = []
            for text in texts:
                tokens = [START_OR_END] + list(text.encode("ascii")) + [START_OR_END]
                new_tokens = []
                for merge_rule in merge_rules: #tqdm.tqdm(merge_rules):
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
                tokenized_texts.append(tokens)
            return tokenized_texts
        elif isinstance(texts, str):
            text = texts
            texts = [text]
            return tokenize(merge_rules, texts)[0]
        else:
            raise TypeError("texts should be a list of str or a str")    
        
    def train_tokenizer(dataset, vocab_size=512):
        n = 32 # dataset start size
        dataset1 = dataset[:n]
        dataset2 = dataset[n:2*n]
    
        corpus1 = [[START_OR_END] + list(text.encode("ascii")) + [START_OR_END] for text in dataset1]
        corpus2 = [[START_OR_END] + list(text.encode("ascii")) + [START_OR_END] for text in dataset2]
        new_token = 256
        merge_rules = []
    
        while True:
        
            # Find the most frequent digrams in corpus 1 and 2
            digram_count1 = {}
            for tokens in corpus1:
                for digram in zip(tokens[:-1], tokens[1:]):
                    digram_count1[digram] = digram_count1.get(digram, 0) + 1
            digram1 = max(digram_count1, key=digram_count1.get)
        
            digram_count2 = {}
            for tokens in corpus2:
                for digram in zip(tokens[:-1], tokens[1:]):
                    digram_count2[digram] = digram_count2.get(digram, 0) + 1
            digram2 = max(digram_count2, key=digram_count2.get)
        
            if digram1 == digram2: # Yay!
                digram = digram1
                print(f"Shared digram (token #{new_token}) at corpus size {n}")
                merge_rules.append((new_token, digram))
                # Merge the digram in corpus 1 and 2
                for corpus in [corpus1, corpus2]:
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
                if new_token == vocab_size:
                    return merge_rules
            else:
                print(f"Different digrams on corpus 1 and 2; bumping corpus size to {2*n}")
                n = 2 * n
                corpus1 = corpus1 + corpus2
                corpus2 = tokenize(merge_rules, dataset[n:2*n]) 

    merge_rules = train_tokenizer(dataset)
    return merge_rules, tokenize


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
def _():
    return


@app.cell
def _(NULL, dataset, merge_rules, token_to_text, tokenize):
    _tokens = tokenize(merge_rules, chr(NULL) + dataset[0] + chr(NULL))
    print(_tokens)
    print([token_to_text[_token] for _token in _tokens])
    return


if __name__ == "__main__":
    app.run()
